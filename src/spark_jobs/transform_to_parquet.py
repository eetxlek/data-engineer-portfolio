import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType

# Configurar Spark
spark = SparkSession.builder \
    .appName("Legacy to Lake") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

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

def write_to_lake(df, output_path: str = "data/lake/siniestros"):
    """Escribe en formato Parquet particionado"""
    
    df.write \
        .mode("overwrite") \
        .partitionBy("tipo_seguro", "anio_accidente") \
        .parquet(output_path)
    
    print(f"💾 Guardados {df.count()} registros en {output_path} como Parquet particionado")

if __name__ == "__main__":
    print("🚀 Iniciando pipeline Spark: Legacy → Lake")
    
    # Ejecutar pipeline
    df = read_validated_jsonl()
    
    if df.count() > 0:
        df_transformed = transform(df)
        write_to_lake(df_transformed)
        
        print("\n📊 Muestra de datos en el lake:")
        df_transformed.show(5, truncate=False)
    else:
        print("⚠️ No hay datos válidos para procesar")
    
    spark.stop()