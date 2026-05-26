-- Modelo Gold: Ranking de proveedores por siniestralidad
WITH silver_data AS (
    SELECT * FROM {{ ref('silver_siniestros') }}
)

SELECT
    codigo_proveedor,
    tipo_seguro_normalizado AS tipo_seguro,
    
    -- Métricas del proveedor
    COUNT(*) AS total_siniestros,
    SUM(importe_reclamado) AS importe_total,
    AVG(importe_reclamado) AS importe_promedio,
    MAX(importe_reclamado) AS importe_maximo,
    
    -- Distribución temporal
    COUNT(DISTINCT año_mes) AS meses_con_siniestros,
    MIN(fecha_accidente) AS primer_siniestro,
    MAX(fecha_accidente) AS ultimo_siniestro,
    
    -- Porcentaje sobre el total
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY tipo_seguro_normalizado), 2) AS porcentaje_tipo_seguro

FROM silver_data
GROUP BY codigo_proveedor, tipo_seguro_normalizado
ORDER BY tipo_seguro_normalizado, importe_total DESC