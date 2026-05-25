-- gold: ya agregado o enriquecido desde silver
CREATE OR REPLACE TEMP VIEW siniestros_gold AS
SELECT * FROM siniestros_silver;

-- ============================================================
-- GOLD LAYER — KPIs de negocio
-- Fuente: siniestros_silver / lake/siniestros_delta/ (Delta Lake)
-- Agregaciones finales para reporting y toma de decisiones
-- ============================================================

-- 1. KPI principal: coste total y volumen por línea de negocio
SELECT
    tipo_seguro,
    COUNT(*)                                    AS total_siniestros,
    SUM(importe_reclamado)                      AS total_coste,
    ROUND(AVG(importe_reclamado), 2)            AS coste_medio,
    ROUND(SUM(importe_reclamado) * 100.0 /
          SUM(SUM(importe_reclamado)) OVER (), 2) AS pct_sobre_total
FROM siniestros_gold
GROUP BY tipo_seguro
ORDER BY total_coste DESC;

-- 2. Evolución anual del coste por tipo de seguro
SELECT
    tipo_seguro,
    anio_accidente,
    COUNT(*)               AS total_siniestros,
    SUM(importe_reclamado) AS coste_total,
    ROUND(
        (SUM(importe_reclamado) - LAG(SUM(importe_reclamado))
            OVER (PARTITION BY tipo_seguro ORDER BY anio_accidente))
        * 100.0 /
        NULLIF(LAG(SUM(importe_reclamado))
            OVER (PARTITION BY tipo_seguro ORDER BY anio_accidente), 0),
    2) AS variacion_pct_anual
FROM siniestros_gold
GROUP BY tipo_seguro, anio_accidente
ORDER BY tipo_seguro, anio_accidente;

-- 3. Ranking de proveedores por coste gestionado
SELECT
    tipo_seguro,
    codigo_proveedor,
    COUNT(*)                                      AS siniestros,
    SUM(importe_reclamado)                        AS coste_total,
    RANK() OVER (
        PARTITION BY tipo_seguro
        ORDER BY SUM(importe_reclamado) DESC
    )                                             AS ranking_por_tipo
FROM siniestros_gold
GROUP BY tipo_seguro, codigo_proveedor
ORDER BY tipo_seguro, ranking_por_tipo;

-- 4. Siniestros de alto impacto (outliers por tipo)
-- Registros que superan 2 desviaciones estándar sobre la media de su tipo
SELECT
    siniestro_id,
    tipo_seguro,
    importe_reclamado,
    ROUND(AVG(importe_reclamado) OVER (PARTITION BY tipo_seguro), 2)    AS media_tipo,
    ROUND(STDDEV(importe_reclamado) OVER (PARTITION BY tipo_seguro), 2) AS stddev_tipo
FROM siniestros_gold
WHERE importe_reclamado > (
    AVG(importe_reclamado) OVER (PARTITION BY tipo_seguro)
    + 2 * STDDEV(importe_reclamado) OVER (PARTITION BY tipo_seguro)
)
ORDER BY tipo_seguro, importe_reclamado DESC;

-- 5. Resumen ejecutivo del pipeline (trazabilidad de calidad)
SELECT
    'TOTAL INGESTADOS'  AS metrica, COUNT(*) AS valor FROM siniestros_bronze
UNION ALL
SELECT
    'TOTAL VALIDADOS'   AS metrica, COUNT(*) AS valor FROM siniestros_silver
UNION ALL
SELECT
    'TOTAL RECHAZADOS'  AS metrica,
    (SELECT COUNT(*) FROM siniestros_bronze) - COUNT(*) AS valor
FROM siniestros_silver;