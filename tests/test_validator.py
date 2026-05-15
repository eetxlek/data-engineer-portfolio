import sys
sys.path.append('src')
from data_quality.validators import validar_lote
from data_generation.legacy_simulator import generar_lote, guardar_como_json
import json


if __name__ == "__main__":
    # Generar datos
    print("🔄 Generando datos de prueba...")
    lote = generar_lote(100)
    
    # Validar
    print("🔍 Validando datos...")
    validos, invalidos = validar_lote(lote)
    
    # Resultados
    print(f"\n📊 Resultados:")
    print(f"   ✅ Válidos: {len(validos)}")
    print(f"   ❌ Inválidos: {len(invalidos)}")
    
    # Guardar resultados
    guardar_como_json(validos, "siniestros_validos.json")
    
    with open("data/siniestros_invalidos.json", "w", encoding="utf-8") as f:
        json.dump(invalidos, f, indent=2, ensure_ascii=False)
    
    # Mostrar algunos inválidos de ejemplo
    print("\n⚠️ Ejemplos de registros inválidos:")
    for inv in invalidos[:3]:
        errores_msg = [e.get("msg", str(e)) for e in inv.get("errores", [])] 
        print(f"   ID: {inv['siniestro_id']} - Errores: {errores_msg}")