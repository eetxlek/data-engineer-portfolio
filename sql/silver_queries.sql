-- silver: solo válidos, con campos derivados
CREATE OR REPLACE TEMP VIEW siniestros_silver AS
SELECT *, YEAR(fecha_accidente) AS anio_accidente
FROM parquet.`data/lake/siniestros/`;

-- ============================================================
-- SILVER LAYER — Datos limpios y estandarizados
-- Fuente: siniestros_validos.jsonl / lake/siniestros/ (Parquet)
-- Solo contiene registros que superaron la validación Pydantic
-- ============================================================

-- 1. Vista base silver: registros válidos con campos derivados
SELECT
    siniestro_id,
    tipo_seguro,
    fecha_accidente,
    YEAR(fecha_accidente)  AS anio_accidente,
    MONTH(fecha_accidente) AS mes_accidente,
    importe_reclamado,
    dni_asegurado,
    codigo_proveedor
FROM siniestros_silver;

-- 2. Importe medio reclamado por tipo de seguro y año
SELECT
    tipo_seguro,
    YEAR(fecha_accidente)        AS anio,
    AVG(importe_reclamado)       AS avg_importe,
    MIN(importe_reclamado)       AS min_importe,
    MAX(importe_reclamado)       AS max_importe
FROM siniestros_silver
GROUP BY tipo_seguro, YEAR(fecha_accidente)
ORDER BY anio DESC, tipo_seguro;

-- 3. Distribución de siniestros por mes (estacionalidad)
SELECT
    MONTH(fecha_accidente) AS mes,
    tipo_seguro,
    COUNT(*)               AS total_siniestros
FROM siniestros_silver
GROUP BY MONTH(fecha_accidente), tipo_seguro
ORDER BY mes, tipo_seguro;

-- 4. Proveedores activos por tipo de seguro
-- Códigos válidos: HOGAR→[HOGAR_REPAR_001/002], COCHE→[TALLER_001/002], SALUD→[HOSP_001/002, CLINICA_001]
SELECT
    tipo_seguro,
    codigo_proveedor,
    COUNT(*)               AS siniestros_gestionados,
    SUM(importe_reclamado) AS importe_total
FROM siniestros_silver
GROUP BY tipo_seguro, codigo_proveedor
ORDER BY tipo_seguro, siniestros_gestionados DESC;

-- 5. Siniestros por rango de importe (segmentación)
SELECT
    tipo_seguro,
    CASE
        WHEN importe_reclamado < 1000              THEN 'BAJO (<1k)'
        WHEN importe_reclamado BETWEEN 1000 AND 5000 THEN 'MEDIO (1k-5k)'
        WHEN importe_reclamado BETWEEN 5000 AND 20000 THEN 'ALTO (5k-20k)'
        ELSE                                            'MUY ALTO (>20k)'
    END AS rango_importe,
    COUNT(*) AS total
FROM siniestros_silver
GROUP BY tipo_seguro, rango_importe
ORDER BY tipo_seguro, rango_importe;

-- 6. Validación de integridad: cruce código_proveedor vs tipo_seguro
SELECT
    tipo_seguro,
    codigo_proveedor,
    COUNT(*) AS total
FROM siniestros_silver
WHERE
    (tipo_seguro = 'HOGAR' AND codigo_proveedor NOT IN ('HOGAR_REPAR_001', 'HOGAR_REPAR_002'))
 OR (tipo_seguro = 'COCHE' AND codigo_proveedor NOT IN ('TALLER_001', 'TALLER_002'))
 OR (tipo_seguro = 'SALUD' AND codigo_proveedor NOT IN ('HOSP_001', 'HOSP_002', 'CLINICA_001'))
GROUP BY tipo_seguro, codigo_proveedor;
-- Si esta query devuelve resultados, hay inconsistencias en la capa silver