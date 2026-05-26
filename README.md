# 🏗️ End-to-End Data Pipeline: Legacy to Lake

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![PySpark](https://img.shields.io/badge/Spark-3.5-orange.svg)](https://spark.apache.org/)
[![Pydantic](https://img.shields.io/badge/pydantic-2.7-green.svg)](https://docs.pydantic.dev/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://www.docker.com/)
[![Delta Lake](https://img.shields.io/badge/delta--lake-3.2-blue.svg)](https://delta.io/)
[![dbt](https://img.shields.io/badge/dbt-1.11-orange.svg)](https://www.getdbt.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.5.3-yellow.svg)](https://duckdb.org/)

> Pipeline ETL/ELT que simula la migración de datos desde un sistema **legacy (mainframe)** a un **Data Lake moderno**, demostrando validación, procesamiento distribuido y almacenamiento optimizado.

---

## 📐 Arquitectura

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Legacy System  │───▶│    Validator     │────▶│      Spark       │───▶│    Data Lake     │
│   (Simulador)    │     │   (Pydantic)     │     │    (PySpark)     │     │    (Delta lake)  │
└──────────────────┘     └──────────────────┘     └──────────────────┘     └──────────────────┘
         │                        │                        │                        │
         ▼                        ▼                        ▼                        ▼
 raw_siniestros.jsonl    válidos/inválidos         Transformaciones         Particionado por
                         (separación datos)        (enriquecimiento)        tipo_seguro / año
```

---

## 📁 Estructura del Proyecto

```
data-engineer-portfolio/
│
├── src/
│   ├── data_generation/
│   │   └── legacy_simulator.py        # Generador de datos legacy con errores controlados
│   ├── data_quality/
│   │   └── validators.py              # Validación y gobierno del dato con Pydantic
│   └── spark_jobs/
│       └── transform_to_delta.py     # Transformación y escritura con PySpark + Delta
│
├── tests/
│   └── test_validators.py             # Tests del pipeline completo
│
├── sql/
│   ├── bronze_queries.sql             # Consultas sobre datos crudos (detección de errores)
│   ├── silver_queries.sql             # Consultas sobre datos limpios y estandarizados
│   └── gold_kpi.sql                   # KPIs de negocio y agregaciones finales
│
├── dbt/
│   ├── dbt_project.yml           # Configuración del proyecto
│   ├── profiles.yml              # Conexión a DuckDB + Delta Lake
│   ├── models/
│   │   ├── silver/
│   │   │   └── silver_siniestros.sql
│   │   └── gold/
│   │       ├── gold_kpi_mensual.sql
│   │       └── gold_top_proveedores.sql
│   ├── analyses/
│   │   └── analisis_outliers.sql
│   └── macros/
│       └── calcular_estacionalidad.sql
│    
├── data/
│   ├── raw_siniestros.jsonl           # Datos sin procesar (salida del simulador)
│   ├── siniestros_validos.jsonl       # Registros que superan validación
│   ├── siniestros_invalidos.jsonl     # Registros rechazados con motivo
│   └── lake/
│       └── siniestros_delta/          # Delta Lake particionado por tipo y año
│
├── docker-compose.yaml                # Infraestructura (Spark + MinIO)
├── Dockerfile                         # Imagen personalizada con dependencias Python
├── requirements.txt
└── README.md
```

---

## 📊 Flujo de Datos

| Fase | Input | Output | Tecnología |
|---|---|---|---|
| **Ingesta** | Generación sintética | `raw_siniestros.jsonl` | Python |
| **Validación** | `raw_siniestros.jsonl` | `validos.jsonl` / `invalidos.jsonl` | Pydantic |
| **Transformación** | `validos.jsonl` | Delta Lake particionado | PySpark + Delta Lake |
| **Almacenamiento** | Delta Lake | Data Lake local / MinIO | Delta Lake + MinIO |
| **Trazabilidad** | Todas las fases | `pipeline_trace.jsonl` | Python |

---

## ✅ Reglas de Negocio

| Campo | Regla de Validación |
|---|---|
| `siniestro_id` | Entre 10.000 y 99.999 |
| `fecha_accidente` | No puede ser fecha futura |
| `tipo_seguro` | Valores permitidos: `HOGAR`, `COCHE`, `SALUD` |
| `importe_reclamado` | Mayor que 0 y dentro de máximos por tipo |
| `dni_asegurado` | Formato español válido (8 dígitos + letra) |
| `codigo_proveedor` | Debe corresponder al tipo de seguro |

---

## 🚀 Ejecución

### Requisitos previos

```bash
# Clonar repositorio
git clone https://github.com/eetxlek/data-engineer-portfolio.git
cd data-engineer-portfolio

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecución local

```bash
# 1. Generar datos y ejecutar validaciones
python tests/test_validators.py

# 2. Transformar datos válidos a Delta Lake con Spark
python src/spark_jobs/transform_to_delta.py
```

### Ejecución con Docker Compose

```bash
# 1. Construir la imagen personalizada (solo la primera vez, o al cambiar requirements.txt)
docker compose build

# 2. Levantar toda la infraestructura (Spark + MinIO + dbt)
docker compose --profile dbt up -d

# 3. Ejecutar el pipeline completo
docker exec spark-master python tests/test_validators.py
docker exec spark-master spark-submit src/spark_jobs/transform_to_delta.py
docker exec dbt dbt run

# 4. Verificar resultados
docker exec dbt duckdb /dbt_project/analytics.duckdb -c "SELECT * FROM gold_kpi_mensual;"
```

> La imagen incluye todas las dependencias Python necesarias (pydantic, pyspark, etc.).
> No es necesario instalar nada manualmente en el contenedor.

### Interfaces web disponibles

| Servicio | URL | Credenciales |
|---|---|---|
| Spark UI | http://localhost:8080 | — |
| Spark Worker UI | http://localhost:8081 | — |
| MinIO Console | http://localhost:9001 | `minioadmin` / `minioadmin` |
| dbt Docs | http://localhost:8083 | — |

---

## 🗄️ Arquitectura Medallion (SQL)

Las queries SQL siguen el patrón **Bronze → Silver → Gold**, ejecutables sobre el Data Lake generado por el pipeline. Requieren que la tabla Delta esté generada previamente.

| Capa | Archivo | Descripción |
|---|---|---|
| **Bronze** | `sql/bronze_queries.sql` | Datos crudos: detección de errores, registros inválidos, tasa de rechazo |
| **Silver** | `sql/silver_queries.sql` | Datos limpios: agregaciones por tipo, estacionalidad, actividad por proveedor |
| **Gold** | `sql/gold_kpi.sql` | KPIs de negocio: coste total, evolución anual, ranking de proveedores, outliers |

---

## 🔄 Transformaciones Analíticas con dbt

El pipeline incorpora **dbt (data build tool)** para transformaciones SQL versionadas sobre el Delta Lake, siguiendo el patrón **Silver → Gold**.

### Arquitectura dbt

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Delta Lake     │───▶│   dbt Silver     │────▶│   dbt Gold       │
│   (Bronze)       │     │   (Limpieza)     │     │   (KPIs)         │
└──────────────────┘     └──────────────────┘     └──────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
   siniestros_delta/      silver_siniestros       gold_kpi_mensual
                                                  gold_top_proveedores


### Modelos dbt

| Capa | Modelo | Descripción |
|---|---|---|
| **Silver** | `silver_siniestros` | Datos enriquecidos: categorización de importes, estacionalidad, normalización |
| **Gold** | `gold_kpi_mensual` | KPIs agregados: total siniestros, importe total/promedio por tipo de seguro |
| **Gold** | `gold_top_proveedores` | Ranking de proveedores: siniestralidad, importes, porcentaje por tipo |

### Ejecución con dbt

```bash
# Ejecutar todas las transformaciones
docker exec dbt dbt run

# Ejecutar solo capa Silver
docker exec dbt dbt run --select silver

# Ejecutar solo capa Gold
docker exec dbt dbt run --select gold

# Ejecutar tests de calidad de datos (verifica id, importe, tipo segurro, categoria importe)
docker exec dbt dbt test

# Generar documentación HTML (docuemnta modelos. Servir con dbt (requiere abrir puerto))
docker exec dbt dbt docs generate
# Ejecutar en segundo plano
docker exec -d dbt dbt docs serve --host 0.0.0.0 --port 8083
```

### Consultas analíticas con DuckDB

dbt utiliza DuckDB como motor analítico, permitiendo consultas SQL directamente sobre las tablas generadas desde dentro del contenedor:

# Entrar al entorno interactivo
docker exec -it dbt duckdb /dbt_project/analytics.duckdb

# Dentro de DuckDB:
SELECT * FROM gold_kpi_mensual;

SELECT codigo_proveedor, total_siniestros, importe_total
FROM gold_top_proveedores
ORDER BY importe_total DESC
LIMIT 10;

---

## ⚡ Delta Lake vs Parquet

La capa de almacenamiento usa Delta Lake sobre Parquet, lo que añade capacidades que Parquet puro no tiene:

**Transaccionalidad** — cada escritura genera una versión en `_delta_log/`. Si el job falla a mitad, no quedan datos corruptos. Con Parquet un fallo dejaba el lake en estado inconsistente.

**Versionado automático** — cada ejecución incrementa `delta_version`. Puedes consultar el estado del lake en cualquier versión anterior con `VERSION AS OF N`. Con Parquet los datos anteriores se perdían en cada overwrite.

**Trazabilidad real** — el `pipeline_trace.jsonl` incluye `delta_version` y `delta_operacion` extraídos del transaction log de Delta, no de conteos manuales. Es auditoría real, no logging artesanal.

**MERGE preparado** — aunque no se usa aún, la tabla ya admite upserts atómicos. Con Parquet corregir un registro significaba reescribir toda la partición.

**Schema enforcement** — Delta rechaza escrituras que no respeten el esquema definido. Con Parquet podías escribir columnas de tipo incorrecto sin error.

| Capacidad | Parquet | Delta Lake |
|---|---|---|
| Transaccionalidad ACID | ❌ | ✅ |
| Versionado automático | ❌ | ✅ `VERSION AS OF N` |
| Time travel | ❌ | ✅ |
| MERGE / upserts atómicos | ❌ | ✅ |
| Schema enforcement | ❌ | ✅ |
| Auditoría de operaciones | ❌ | ✅ `DESCRIBE HISTORY` |
| Formato de datos en disco | Parquet | Parquet + `_delta_log/` |

> Los datos en disco siguen siendo ficheros `.parquet`. Delta añade un transaction log (`_delta_log/`) encima sin cambiar el formato de almacenamiento.

### Ejecución de queries con Spark SQL

```bash
# Entrar en la shell interactiva de Spark SQL
docker exec -it -w /opt/spark/work-dir spark-master spark-sql
```

Cada archivo comienza registrando la vista Delta Lake correspondiente:

```sql
-- Bronze: apunta al lake completo
CREATE OR REPLACE TEMP VIEW siniestros_bronze AS
SELECT * FROM delta.`data/lake/siniestros_delta/`;

-- Verificar que hay datos
SELECT tipo_seguro, COUNT(*) AS total
FROM siniestros_bronze
GROUP BY tipo_seguro;
```

> Las queries SQL solo tienen sentido una vez ejecutado el pipeline completo
> (`test_validators.py` + `transform_to_delta.py`).

---

## 📈 Resultados Esperados

Con una tasa de error del 5% (`tasa_error=0.05`) sobre 100 registros:

```
📊 Resultados:
   ✅ Válidos:    95
   ❌ Inválidos:   5
```

Los registros válidos se almacenan en Delta Lake particionado por:

- `tipo_seguro` → `HOGAR` | `COCHE` | `SALUD`
- `anio_accidente` → extraído de `fecha_accidente`

---

## 🔎 Trazabilidad del Pipeline

Cada ejecución genera un log estructurado en `data/pipeline_trace.jsonl` con métricas por fase:

```json
{"fase": "ingesta", "timestamp": "2026-05-16T10:00:01", "registros_generados": 100, "tasa_error_configurada": 0.05, "estado": "ok"}
{"fase": "validacion", "timestamp": "2026-05-16T10:00:01", "registros_entrada": 100, "registros_validos": 95, "registros_invalidos": 5, "tasa_rechazo": 0.05, "motivos_rechazo": {"DNI inválido": 3, "importe fuera de rango": 2}, "estado": "ok"}
{"fase": "transformacion_delta", "timestamp": "2026-05-16T10:00:45", "registros_entrada": 95, "registros_salida": 95, "particiones_generadas": ["HOGAR", "COCHE", "SALUD"], "columnas_añadidas": ["anio_accidente", "rango_importe"], "output_path": "data/lake/siniestros_delta", "formato": "delta", "delta_version": 0, "delta_operacion": "WRITE", "estado": "ok"}
```

El log es acumulativo: cada ejecución añade sus entradas sin sobrescribir las anteriores, permitiendo auditar el histórico completo del pipeline.

---

## 🛠️ Stack Tecnológico

| Categoría | Tecnologías |
|---|---|
| **Core Data** | Python 3.11, PySpark 3.5, Pandas |
| **Validación** | Pydantic 2.7 |
| **Transformaciones** | dbt (data build tool) 1.11, DuckDB |
| **SQL / Análisis** | Spark SQL, dbt SQL, DuckDB |
| **Formatos** | JSONL, Parquet, Delta Lake |
| **Contenedores** | Docker, Docker Compose |
| **Storage** | MinIO (S3-compatible), Sistema de ficheros local |

---

## 👤 Autor

**Eetxlek** - Data Engineer

- GitHub: [@eetxlek](https://github.com/eetxlek)
- Proyecto: [data-engineer-portfolio](https://github.com/eetxlek/data-engineer-portfolio)

---

⭐ Si este proyecto te ha sido útil ⭐