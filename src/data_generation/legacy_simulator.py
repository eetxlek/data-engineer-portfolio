import random
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Posibles valores (incluyendo inválidos a propósito)
TIPOS_SEGURO_VALIDOS = ["HOGAR", "COCHE", "SALUD"]  # Vacío es inválido
DNI_LETRAS = "TRWAGMYFPDXBNJZSQVHLCKE"

# Códigos válidos por tipo de seguro
CODIGOS_VALIDOS = {
    "HOGAR": ["HOGAR_REPAR_001", "HOGAR_REPAR_002"],
    "COCHE": ["TALLER_001", "TALLER_002"],
    "SALUD": ["HOSP_001", "HOSP_002", "CLINICA_001"]
}

# Posibles errores para la rama inválida
TIPOS_INVALIDOS = ["", "INVALIDO", "OTRO"]
CODIGOS_INVALIDOS = ["INVALIDO", "CODIGO_FALSO", None]

def generar_dni_valido() -> str:
    """Genera un DNI válido (8 números + letra calculada correctamente)"""
    numeros = random.randint(10000000, 99999999)
    letra = DNI_LETRAS[numeros % 23]
    return f"{numeros}{letra}"


def generar_dni_invalido() -> str:
    """Genera DNI con formato incorrecto (sin letra, números fuera de rango, etc.)"""
    opcion = random.choice([1, 2, 3])
    if opcion == 1:
        return f"{random.randint(0, 99999999)}"  # Sin letra
    elif opcion == 2:
        return f"{random.randint(100000000, 999999999)}X"  # Números fuera de rango
    else:
        return f"{random.randint(0, 99999999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"  # Letra incorrecta

def generar_fecha_valida() -> str:
    """Genera una fecha válida (pasada, formato YYYY-MM-DD)"""
    return (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")

def generar_fecha_invalida() -> str:
    """Genera fechas inválidas (futuro, formato incorrecto)"""
    opcion = random.choice([1, 2])
    if opcion == 1:
        # Fecha futura
        futuro = datetime.now() + timedelta(days=random.randint(30, 365))
        return futuro.strftime("%Y-%m-%d")
    else:
        # Formato incorrecto
        return f"{random.randint(1,31)}/{random.randint(1,12)}/{random.randint(2020,2025)}"

def generar_siniestro(tasa_error: float) -> Dict[str, Any]:
    """Genera un siniestro. tasa_error = probabilidad de datos inválidos"""

    # El 30% de los siniestros tienen algún error, para bajar pon 0.05 que es 5% de errores
    tiene_error = random.random() < tasa_error
    
    if tiene_error:
        # Datos INválidos (pueden tener errores en varios campos)
        tipo = random.choice(TIPOS_SEGURO_VALIDOS + TIPOS_INVALIDOS)
        fecha = generar_fecha_invalida()
        importe = random.choice([-random.randint(100, 5000), random.randint(-1000, -1), None])
        dni = generar_dni_invalido()
        # Código puede ser válido o no, pero no necesariamente coincide con el tipo
        codigo = random.choice(CODIGOS_INVALIDOS + [c for lista in CODIGOS_VALIDOS.values() for c in lista])
    else:
        # Datos VÁLIDOS (todo cumple las reglas)
        tipo = random.choice(TIPOS_SEGURO_VALIDOS)
        fecha = generar_fecha_valida()
        importe = random.randint(100, 10000)
        dni = generar_dni_valido()
        codigo = random.choice(CODIGOS_VALIDOS[tipo])
    
    return {
        "siniestro_id": random.randint(10000, 99999),
        "fecha_accidente": fecha,
        "tipo_seguro": tipo,
        "importe_reclamado": importe,
        "dni_asegurado": dni,
        "codigo_proveedor": codigo
    }

def generar_lote(cantidad: int = 100, tasa_error: float =0.05 ) -> list:
    """Genera un lote de siniestros"""
    return [generar_siniestro(tasa_error) for _ in range(cantidad)]

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

def guardar_jsonl(datos: list, filename: str):
    """Guarda una lista en formato JSONL"""
    import os
    os.makedirs("data", exist_ok=True)
    datos_serializables = convertir_fechas_a_string(datos)
    with open(f"data/{filename}", "w", encoding="utf-8") as f:
        for registro in datos_serializables:
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")
    print(f"✅ Guardados {len(datos)} registros en data/{filename}")


if __name__ == "__main__":
    # Ejecución directa para probar
    print("Generando 50 siniestros con tasa_error=0.1...")
    lote = generar_lote(50, 0.1)
    guardar_jsonl(lote, "test.jsonl")
    print("\n📊 Muestra del primer registro:")
    print(json.dumps(lote[0], indent=2, ensure_ascii=False))