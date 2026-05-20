# 🏗️ End-to-End Data Pipeline: Legacy to Lake

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![PySpark](https://img.shields.io/badge/Spark-3.5-orange.svg)](https://spark.apache.org/)
[![Pydantic](https://img.shields.io/badge/pydantic-2.7-green.svg)](https://docs.pydantic.dev/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://www.docker.com/)

> Pipeline ETL/ELT que simula la migración de datos desde un sistema **legacy (mainframe)** a un **Data Lake moderno**, demostrando validación, procesamiento distribuido y almacenamiento optimizado.

---

## 📐 Arquitectura

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Legacy System  │───▶│    Validator     │────▶│      Spark       │───▶│    Data Lake     │
│   (Simulador)    │     │   (Pydantic)     │     │    (PySpark)     │     │    (Parquet)     │
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
│       └── transform_to_parquet.py    # Transformación y escritura con PySpark
│
├── tests/
│   └── test_validators.py             # Tests del pipeline completo
│
├── data/
│   ├── raw_siniestros.jsonl           # Datos sin procesar (salida del simulador)
│   ├── siniestros_validos.jsonl       # Registros que superan validación
│   ├── siniestros_invalidos.jsonl     # Registros rechazados con motivo
│   └── lake/
│       └── siniestros/                # Parquet particionado por tipo y año
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
| **Transformación** | `validos.jsonl` | Parquet particionado | PySpark |
| **Almacenamiento** | Parquet | Data Lake local / MinIO | Parquet + MinIO |
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

# 2. Transformar datos válidos a Parquet con Spark
python src/spark_jobs/transform_to_parquet.py
```

### Ejecución con Docker Compose

```bash
# 1. Construir la imagen personalizada (solo la primera vez, o al cambiar requirements.txt)
docker compose build

# 2. Levantar el cluster Spark + MinIO
docker compose up -d

# 3. Ejecutar el pipeline
docker exec spark-master python3 tests/test_validators.py
docker exec spark-master spark-submit src/spark_jobs/transform_to_parquet.py
```

> La imagen incluye todas las dependencias Python necesarias (pydantic, pyspark, etc.).
> No es necesario instalar nada manualmente en el contenedor.

### Interfaces web disponibles

| Servicio | URL | Credenciales |
|---|---|---|
| Spark UI | http://localhost:8080 | — |
| Spark Worker UI | http://localhost:8081 | — |
| MinIO Console | http://localhost:9001 | `minioadmin` / `minioadmin` |

---

## 📈 Resultados Esperados

Con una tasa de error del 5% (`tasa_error=0.05`) sobre 100 registros:

```
📊 Resultados:
   ✅ Válidos:    95
   ❌ Inválidos:   5
```

Los registros válidos se almacenan en Parquet particionado por:

- `tipo_seguro` → `HOGAR` | `COCHE` | `SALUD`
- `anio_accidente` → extraído de `fecha_accidente`

---

## 🔎 Trazabilidad del Pipeline

Cada ejecución genera un log estructurado en `data/pipeline_trace.jsonl` con métricas por fase:

```json
{"fase": "ingesta", "timestamp": "2026-05-16T10:00:01", "registros_generados": 100, "tasa_error_configurada": 0.05, "estado": "ok"}
{"fase": "validacion", "timestamp": "2026-05-16T10:00:01", "registros_validos": 95, "registros_invalidos": 5, "tasa_rechazo": 0.05, "motivos_rechazo": {"DNI inválido": 3, "importe fuera de rango": 2}, "estado": "ok"}
{"fase": "transformacion_spark", "timestamp": "2026-05-16T10:00:45", "registros_entrada": 95, "registros_salida": 95, "particiones_generadas": ["HOGAR", "COCHE", "SALUD"], "formato": "parquet", "estado": "ok"}
```

El log es acumulativo: cada ejecución añade sus entradas sin sobrescribir las anteriores, permitiendo auditar el histórico completo del pipeline.

---

## 🛠️ Stack Tecnológico

| Categoría | Tecnologías |
|---|---|
| **Core Data** | Python 3.11, PySpark 3.5, Pandas |
| **Validación** | Pydantic 2.7 |
| **Formatos** | JSONL, Parquet |
| **Contenedores** | Docker, Docker Compose |
| **Storage** | MinIO (S3-compatible), Sistema de ficheros local |

---

## 👤 Autor

**Eetxlek** - Data Engineer

- GitHub: [@eetxlek](https://github.com/eetxlek)
- Proyecto: [data-engineer-portfolio](https://github.com/eetxlek/data-engineer-portfolio)

---

⭐ Si este proyecto te ha sido útil ⭐