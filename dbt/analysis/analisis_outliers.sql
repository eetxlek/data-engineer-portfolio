-- Análisis de outliers en importes
WITH silver_data AS (
    SELECT * FROM {{ ref('silver_siniestros') }}
),
stats AS (
    SELECT 
        tipo_seguro_normalizado,
        AVG(importe_reclamado) AS media,
        STDDEV(importe_reclamado) AS desviacion
    FROM silver_data
    GROUP BY tipo_seguro_normalizado
)
SELECT 
    s.siniestro_id,
    s.tipo_seguro_normalizado,
    s.importe_reclamado,
    s.codigo_proveedor,
    st.media,
    st.desviacion,
    CASE 
        WHEN s.importe_reclamado > st.media + 3 * st.desviacion THEN 'OUTLIER_SUPERIOR'
        WHEN s.importe_reclamado < st.media - 3 * st.desviacion THEN 'OUTLIER_INFERIOR'
        ELSE 'NORMAL'
    END AS tipo_outlier
FROM silver_data s
JOIN stats st ON s.tipo_seguro_normalizado = st.tipo_seguro_normalizado
WHERE s.importe_reclamado > st.media + 3 * st.desviacion
   OR s.importe_reclamado < st.media - 3 * st.desviacion
ORDER BY s.importe_reclamado DESC