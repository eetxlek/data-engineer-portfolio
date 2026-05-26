-- Modelo Gold: KPIs agregados por mes y tipo de seguro
WITH silver_data AS (
    SELECT * FROM {{ ref('silver_siniestros') }}
)

SELECT
    año_mes,
    tipo_seguro_normalizado AS tipo_seguro,
    mes_accidente,
    
    -- KPIs principales
    COUNT(*) AS num_siniestros,
    SUM(importe_reclamado) AS importe_total,
    AVG(importe_reclamado) AS importe_promedio,
    MIN(importe_reclamado) AS importe_minimo,
    MAX(importe_reclamado) AS importe_maximo,
    
    -- KPIs adicionales
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY importe_reclamado) AS mediana_importe,
    SUM(CASE WHEN categoria_importe = 'ALTO' THEN 1 ELSE 0 END) AS siniestros_alto,
    SUM(CASE WHEN categoria_importe = 'MEDIO' THEN 1 ELSE 0 END) AS siniestros_medio,
    SUM(CASE WHEN categoria_importe = 'BAJO' THEN 1 ELSE 0 END) AS siniestros_bajo,
    SUM(CASE WHEN es_importe_alto THEN 1 ELSE 0 END) AS siniestros_mas_10k,
    
    -- Diversidad de proveedores
    COUNT(DISTINCT codigo_proveedor) AS proveedores_distintos
    
FROM silver_data
GROUP BY año_mes, tipo_seguro_normalizado, mes_accidente
ORDER BY año_mes DESC, tipo_seguro_normalizado