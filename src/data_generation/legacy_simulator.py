import random
import json
from datetime import datetime, timedelta
from typing import Dict, Any
TIPOS_SEGURO = ["HOGAR", "COCHE", "SALUD", ""]  # Vacío es inválido
DNI_LETRAS = "TRWAGMYFPDXBNJZSQVHLCKE"

def generar_dni_invalido() -> str:
    """Genera DNI con formato incorrecto"""
    opcion = random.choice([1, 2, 3])
    if opcion == 1:
        return f"{random.randint(0, 99999999)}"  # Sin letra
    elif opcion == 2:
        return f"{random.randint(100000000, 999999999)}X"  # Números fuera de rango
    else:
        return f"{random.randint(0, 99999999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"

def generar_fecha_invalida() -> str:
    """Genera fechas inválidas"""
    opcion = random.choice([1, 2])
    if opcion == 1:
        futuro = datetime.now() + timedelta(days=random.randint(30, 365))
        return futuro.strftime("%Y-%m-%d")
    else:
        return f"{random.randint(1,31)}/{random.randint(1,12)}/{random.randint(2020,2025)}"

def generar_siniestro() -> Dict[str, Any]:
    """Genera un siniestro con datos potencialmente inválidos"""
    tipo = random.choice(TIPOS_SEGURO)
    
    tiene_error = random.random() < 0.3
    
    if tiene_error:
        fecha = generar_fecha_invalida()
        importe = random.choice([-random.randint(100, 5000), random.randint(-1000, -1), None])
        dni = generar_dni_invalido()
    else:
        fecha = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
        importe = random.randint(100, 10000)
        dni = f"{random.randint(10000000, 99999999)}{random.choice(DNI_LETRAS)}"
    
    return {
        "siniestro_id": random.randint(10000, 99999),
        "fecha_accidente": fecha,
        "tipo_seguro": tipo,
        "importe_reclamado": importe,
        "dni_asegurado": dni,
        "codigo_proveedor": random.choice(["TALLER_001", "HOSP_002", "TALLER_002", "INVALIDO", None])
    }

def generar_lote(cantidad: int = 100) -> list:
    return [generar_siniestro() for _ in range(cantidad)]

def guardar_como_json(lote: list, filename: str = "raw_siniestros.json"):
    import os
    os.makedirs("data", exist_ok=True)
    with open(f"data/{filename}", "w", encoding="utf-8") as f:
        json.dump(lote, f, indent=2, ensure_ascii=False)
    print(f"✅ Generados {len(lote)} registros en data/{filename}")

if __name__ == "__main__":
    lote = generar_lote(50)
    guardar_como_json(lote)
    print("\n📊 Muestra de un registro:")
    print(json.dumps(lote[0], indent=2, ensure_ascii=False))
