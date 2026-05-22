import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType
import json
from datetime import datetime
from delta import configure_spark_with_delta_pip
from delta.tables import DeltaTable

# Configurar Spark añadiendo delta
builder = SparkSession.builder \
    .appName("Legacy to Lake") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

def read_validated_jsonl(input_path: str = "data/siniestros_validos.jsonl"):
    """Lee archivo JSONL (un JSON por línea) validado con esquema definido"""
    
    schema = StructType([
        StructField("siniestro_id", IntegerType(), True),
        StructField("fecha_accidente", StringType(), True),
        StructField("tipo_seguro", StringType(), True),
        StructField("importe_reclamado", FloatType(), True),
        StructField("dni_asegurado", StringType(), True),
        StructField("codigo_proveedor", StringType(), True)
    ])
    # JSONL no necesita multiline
    df = spark.read.schema(schema).json(input_path)
    print(f"📖 Leídos {df.count()} registros desde {input_path}")
    return df

def transform(df):
    """Transformaciones adicionales (enriquecimiento, limpieza)"""
    
    # Añadir año de accidente para particionamiento
    df = df.withColumn("anio_accidente", 
                       when(col("fecha_accidente").isNotNull(),
                            col("fecha_accidente").substr(1, 4))
                       .otherwise(lit("unknown")))
    
    # Clasificar por importe
    df = df.withColumn("rango_importe",
                       when(col("importe_reclamado") < 1000, "bajo")
                       .when(col("importe_reclamado") < 5000, "medio")
                       .otherwise("alto"))
    
    return df

# antes "data/lake/siniestros" en parquet particionado ahora delta lake
def write_to_lake(df, output_path: str = "data/lake/siniestros_delta"):
    """Escribe en delta lake"""
    df.write \
        .format("delta") \
        .mode("overwrite") \
        .partitionBy("tipo_seguro", "anio_accidente") \
        .save(output_path)
    
    print(f"💾 Guardados {df.count()} registros en {output_path} como Delta Lake")

# Antes: leer particiones del filesystem (solo funciona con Parquet)
# Después: leer particiones desde el transaction log de Delta
def guardar_log_spark(df_entrada, df_transformado, output_path, pipeline_trace="data/pipeline_trace.jsonl"):
    """
    Registra métricas de la fase Spark en el log de trazabilidad del pipeline.
    Se añade al mismo archivo que genera test.py para tener el rastro completo.
    """
    version_actual = 0
    operacion = "WRITE"
    particiones = []

    if DeltaTable.isDeltaTable(spark, output_path):
        dt = DeltaTable.forPath(spark, output_path)
        history = dt.history(1).collect()[0]
        version_actual = history["version"]
        operacion = history["operation"]

    if os.path.exists(output_path):
        for entry in os.listdir(output_path):
            if entry.startswith("tipo_seguro="):
                particiones.append(entry.replace("tipo_seguro=", ""))

    log = {
        "fase": "transformacion_delta",          # ← renombrado
        "timestamp": datetime.now().isoformat(),
        "registros_entrada": df_entrada.count(),
        "registros_salida": df_transformado.count(),
        "columnas_añadidas": ["anio_accidente", "rango_importe"],
        "particiones_generadas": particiones,
        "output_path": output_path,
        "formato": "delta",                      # ← cambiado
        "delta_version": version_actual,         # ← nuevo
        "delta_operacion": operacion,            # ← nuevo
        "estado": "ok"
    }

    os.makedirs("data", exist_ok=True)
    with open(pipeline_trace, "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")

    print(f"\n🔎 Trazabilidad Spark guardada en {pipeline_trace}")

if __name__ == "__main__":
    print("🚀 Iniciando pipeline Spark: Legacy → Lake")
    
    # Ejecutar pipeline
    df = read_validated_jsonl()
    
    if df.count() > 0:
        df.cache()  # ← evita releer el dataset en cada count()
        df_transformed = transform(df)
        df_transformed.cache()   
        write_to_lake(df_transformed) # operacion sincrona en pyspark, cuando ofrece el log, ya esta escrito en disco.
        guardar_log_spark(df, df_transformed, "data/lake/siniestros_delta") 

        print("\n📊 Muestra de datos en el lake:")
        df_transformed.show(5, truncate=False)

        df.unpersist()           # ← liberar memoria al terminar
        df_transformed.unpersist()
    else:
        print("⚠️ No hay datos válidos para procesar")
    
    spark.stop()