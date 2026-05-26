-- Modelo Silver: Lee del Delta Lake y añade transformaciones
WITH source AS (
    SELECT 
        siniestro_id,
        fecha_accidente,
        tipo_seguro,
        importe_reclamado,
        dni_asegurado,
        codigo_proveedor,
        anio_accidente,
        rango_importe
    FROM delta_scan('/data/lake/siniestros_delta/')
)

SELECT
    siniestro_id,
    fecha_accidente,
    tipo_seguro,
    importe_reclamado,
    dni_asegurado,
    codigo_proveedor,
    anio_accidente,
    rango_importe,
    
    -- Enriquecimiento Silver
    CASE 
        WHEN importe_reclamado < 1000 THEN 'BAJO'
        WHEN importe_reclamado BETWEEN 1000 AND 5000 THEN 'MEDIO'
        WHEN importe_reclamado > 5000 THEN 'ALTO'
        ELSE 'SIN_CLASIFICAR'
    END AS categoria_importe,
    
    -- Extraer mes y año-mes para análisis temporal
    SUBSTR(fecha_accidente, 6, 2) AS mes_accidente,
    SUBSTR(fecha_accidente, 1, 7) AS año_mes,
    
    -- Flag de importe alto (para alertas)
    CASE 
        WHEN importe_reclamado > 10000 THEN TRUE 
        ELSE FALSE 
    END AS es_importe_alto,
    
    -- Normalizar tipo_seguro (asegurar mayúsculas)
    UPPER(TRIM(tipo_seguro)) AS tipo_seguro_normalizado

FROM source
WHERE importe_reclamado > 0  -- Filtro de calidad adicional
  AND siniestro_id IS NOT NULL