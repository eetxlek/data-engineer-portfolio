# 🏗️ End-to-End Data Pipeline: Legacy to Lake

[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/)
[![PySpark](https://img.shields.io/badge/Spark-3.5-orange.svg)](https://spark.apache.org/)
[![Pydantic](https://img.shields.io/badge/pydantic-2.13-green.svg)](https://docs.pydantic.dev/)
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
├── docker-compose.yml                 # Infraestructura (Spark + MinIO)
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
git clone <repo-url>
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
# Levantar cluster Spark + MinIO
docker compose up -d

# Instalar dependencias en el contenedor Spark
docker exec -u root spark-master bash -c "apt-get update && apt-get install -y python3 python3-pip"
docker exec spark-master pip3 install pydantic

# Ejecutar pipeline dentro del contenedor
docker exec spark-master python3 tests/test_validators.py
docker exec spark-master spark-submit src/spark_jobs/transform_to_parquet.py
```

### Interfaces web disponibles

| Servicio | URL | Credenciales |
|---|---|---|
| Spark UI | http://localhost:8080 | — |
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

## 🛠️ Stack Tecnológico

| Categoría | Tecnologías |
|---|---|
| **Core Data** | Python, PySpark, Pandas |
| **Validación** | Pydantic |
| **Formatos** | JSONL, Parquet |
| **Contenedores** | Docker, Docker Compose |
| **Storage** | MinIO (S3-compatible), Sistema de ficheros local |