-- ============================================================
-- PASO 0 — Registrar la fuente Delta Lake como vista consultable
-- Ejecutar esto antes que cualquier query
-- ============================================================
-- Vista temporal de todos los siniestros validados
CREATE OR REPLACE TEMP VIEW bronze_siniestros AS
SELECT *
FROM delta.`data/lake/siniestros_delta/`;
-- Consultar una versión anterior específica. Capacidad sin activar por defecto
-- VERSION AS OF 2;
-- Consultar por timestamp. Capacidad sin activar por defecto
-- TIMESTAMP AS OF '2026-05-16T10:00:00';

-- ============================================================
-- BRONZE LAYER — Datos crudos validados
-- Fuente: raw_siniestros.jsonl / tabla siniestros_bronze
-- Contiene todos los registros, válidos e inválidos
-- ============================================================

-- 1. Vista general de todos los registros ingestados
SELECT *
FROM siniestros_bronze
WHERE tipo_seguro IS NOT NULL;

-- 2. Conteo total de registros por estado de validación
SELECT
    CASE
        WHEN tipo_seguro IN ('HOGAR', 'COCHE', 'SALUD') THEN 'VALIDO'
        ELSE 'INVALIDO'
    END AS estado,
    COUNT(*) AS total
FROM siniestros_bronze
GROUP BY estado;

-- 3. Registros con tipo_seguro inválido (detección de errores de origen)
SELECT
    siniestro_id,
    tipo_seguro,
    codigo_proveedor,
    importe_reclamado,
    dni_asegurado
FROM siniestros_bronze
WHERE tipo_seguro NOT IN ('HOGAR', 'COCHE', 'SALUD')
   OR tipo_seguro IS NULL;

-- 4. Registros con código de proveedor sospechoso
SELECT
    siniestro_id,
    tipo_seguro,
    codigo_proveedor
FROM siniestros_bronze
WHERE codigo_proveedor IN ('INVALIDO', 'CODIGO_FALSO')
   OR codigo_proveedor IS NULL;

-- 5. Registros con importe reclamado fuera de rango básico
SELECT
    siniestro_id,
    tipo_seguro,
    importe_reclamado
FROM siniestros_bronze
WHERE importe_reclamado <= 0
   OR importe_reclamado IS NULL;

-- 6. Tasa de error por lote (útil para monitoreo del pipeline)
SELECT
    COUNT(*) AS total_registros,
    SUM(CASE WHEN tipo_seguro NOT IN ('HOGAR', 'COCHE', 'SALUD') THEN 1 ELSE 0 END) AS registros_invalidos,
    ROUND(
        SUM(CASE WHEN tipo_seguro NOT IN ('HOGAR', 'COCHE', 'SALUD') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    ) AS tasa_error_pct
FROM siniestros_bronze;