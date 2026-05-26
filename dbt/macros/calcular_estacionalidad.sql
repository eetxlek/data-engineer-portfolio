-- Macro para calcular índice estacional
{% macro indice_estacional(medida, grupo, total_general) %}
    ROUND(100.0 * {{ medida }} / NULLIF({{ total_general }}, 0), 2)
{% endmacro %}

-- Macro para categorizar importes
{% macro categorizar_importe(importe) %}
    CASE 
        WHEN {{ importe }} < 1000 THEN 'BAJO'
        WHEN {{ importe }} < 5000 THEN 'MEDIO'
        ELSE 'ALTO'
    END
{% endmacro %}