import sys
sys.path.append('src')
from data_quality.validators import validar_lote
from data_generation.legacy_simulator import generar_lote, guardar_jsonl
import json
import os
import os
from datetime import datetime

def convertir_fechas_a_string(obj):
    """Convierte objetos datetime a string recursivamente"""
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d")
    elif isinstance(obj, dict):
        return {k: convertir_fechas_a_string(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convertir_fechas_a_string(item) for item in obj]
    else:
        return obj


def guardar_jsonl(datos: list, filepath: str):
    """Guarda una lista de diccionarios en formato JSONL (un JSON por línea)"""
    os.makedirs("data", exist_ok=True)
    # Convertir fechas a string antes de guardar
    datos_serializables = convertir_fechas_a_string(datos)
    with open(filepath, "w", encoding="utf-8") as f:
        for registro in datos_serializables:
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")
    print(f"✅ Guardados {len(datos)} registros en {filepath}")

def leer_jsonl(filepath: str) -> list:
    """Lee un archivo JSONL y devuelve una lista de diccionarios"""
    datos = []
    with open(filepath, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea:
                datos.append(json.loads(linea))
    return datos

def guardar_log_validacion(lote, validos, invalidos, filepath="data/pipeline_trace.jsonl"):
    motivos = {}
    for inv in invalidos:
        for error in inv.get("errores", []):
            msg = error.get("msg", "desconocido")
            motivos[msg] = motivos.get(msg, 0) + 1

    fases = [
        {
            "fase": "ingesta",
            "timestamp": datetime.now().isoformat(),
            "registros_generados": len(lote),
            "tasa_error_configurada": 0.05,
            "estado": "ok"
        },
        {
            "fase": "validacion",
            "timestamp": datetime.now().isoformat(),
            "registros_entrada": len(lote),
            "registros_validos": len(validos),
            "registros_invalidos": len(invalidos),
            "tasa_rechazo": round(len(invalidos) / len(lote), 4),
            "motivos_rechazo": motivos,
            "estado": "ok"
        }
    ]

    os.makedirs("data", exist_ok=True)
    with open(filepath, "a", encoding="utf-8") as f:
        for fase in fases:
            f.write(json.dumps(fase, ensure_ascii=False) + "\n")

    print(f"\n🔎 Trazabilidad guardada en {filepath}")

if __name__ == "__main__":
    # Generar datos
    print("🔄 Generando datos de prueba...")
    lote = generar_lote(100, tasa_error=0.05) # ajustar tasa de error aquí si quieres más o menos registros inválidos
    
    # Validar
    print("🔍 Validando datos...")
    validos, invalidos = validar_lote(lote)
    
    # Resultados
    print(f"\n📊 Resultados:")
    print(f"   ✅ Válidos: {len(validos)}")
    print(f"   ❌ Inválidos: {len(invalidos)}")
    
    # Guardar en formato JSONL
    guardar_jsonl(lote, "data/raw_siniestros.jsonl")
    guardar_jsonl(validos, "data/siniestros_validos.jsonl")

    # Para inválidos, serializar errores correctamente
    invalidos_serializables = []
    for inv in invalidos:
        inv_serializable = {
            "indice": inv.get("indice"),
            "siniestro_id": inv.get("siniestro_id"),
            "errores": inv.get("errores"),  # Ya están serializables por validators.py
            "datos_originales": inv.get("datos_originales")
        }
        invalidos_serializables.append(inv_serializable)

    guardar_jsonl(invalidos_serializables, "data/siniestros_invalidos.jsonl")

    print("\n✅ Datos guardados en data/ (formato JSONL)")
    print(f"   - raw_siniestros.jsonl: {len(lote)} registros")
    print(f"   - siniestros_validos.jsonl: {len(validos)} registros")
    print(f"   - siniestros_invalidos.jsonl: {len(invalidos)} registros")
    
    print("\n⚠️ Ejemplos de registros inválidos:")
    for inv in invalidos[:3]:
        errores_msg = [e.get("msg", str(e)) for e in inv.get("errores", [])]
        print(f"   ID: {inv.get('siniestro_id')} - Errores: {errores_msg}")
    
    guardar_log_validacion(lote, validos, invalidos)