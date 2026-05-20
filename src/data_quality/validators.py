from __future__ import annotations
from pydantic import BaseModel, Field, field_validator, ValidationError
from datetime import datetime
from typing import Optional
import re

# Constantes para las reglas de negocio
TIPOS_SEGURO_VALIDOS = ["HOGAR", "COCHE", "SALUD"]
CODIGOS_PROVEEDOR_VALIDOS = {
    "HOGAR": ["HOGAR_REPAR_001", "HOGAR_REPAR_002"],
    "COCHE": ["TALLER_001", "TALLER_002"],
    "SALUD": ["HOSP_001", "HOSP_002", "CLINICA_001"]
}
IMPORTE_MAXIMO = {
    "HOGAR": 50000,
    "COCHE": 30000,
    "SALUD": 100000
}

class SiniestroValidado(BaseModel):
    """Modelo Pydantic con reglas de negocio integradas"""
    
    siniestro_id: int = Field(..., ge=10000, le=99999, description="ID único del siniestro")
    fecha_accidente: datetime = Field(..., description="Fecha del accidente")
    tipo_seguro: str = Field(..., description="Tipo de seguro: HOGAR, COCHE, SALUD")
    importe_reclamado: float = Field(..., gt=0, description="Importe reclamado (debe ser positivo)")
    dni_asegurado: str = Field(..., min_length=9, max_length=9, description="DNI con letra")
    codigo_proveedor: Optional[str] = Field(None, description="Código del proveedor/taller/hospital")
    
    @field_validator("fecha_accidente")
    @classmethod
    def validar_fecha_no_futura(cls, v: datetime) -> datetime:
        """Regla de negocio: No se pueden registrar accidentes en el futuro"""
        if v > datetime.now():
            raise ValueError(f"Fecha {v.date()} no puede ser futura")
        return v
    
    @field_validator("tipo_seguro")
    @classmethod
    def validar_tipo_seguro(cls, v: str) -> str:
        """Regla de negocio: Solo seguros HOGAR, COCHE o SALUD"""
        if v not in TIPOS_SEGURO_VALIDOS:
            raise ValueError(f"Tipo de seguro '{v}' no válido. Debe ser {TIPOS_SEGURO_VALIDOS}")
        return v
    
    @field_validator("importe_reclamado")
    @classmethod
    def validar_importe_por_tipo(cls, v: float, info) -> float:
        """Regla de negocio: El importe no puede exceder el máximo por tipo de seguro"""
        # info.data contiene los campos ya validados
        tipo = info.data.get("tipo_seguro")
        if tipo and v > IMPORTE_MAXIMO.get(tipo, float('inf')):
            raise ValueError(f"Importe {v}€ excede el máximo para {tipo} ({IMPORTE_MAXIMO[tipo]}€)")
        return v
    
    @field_validator("dni_asegurado")
    @classmethod
    def validar_dni(cls, v: str) -> str:
        """Regla de negocio: Formato DNI español válido"""
        patron = r'^\d{8}[A-Z]$'
        if not re.match(patron, v):
            raise ValueError(f"DNI '{v}' no tiene formato válido (8 números + letra)")
        
        # Validar letra (algoritmo oficial)
        numeros = int(v[:8])
        letras = "TRWAGMYFPDXBNJZSQVHLCKE"
        letra_calculada = letras[numeros % 23]
        if v[8] != letra_calculada:
            raise ValueError(f"Letra del DNI '{v[8]}' incorrecta. Debería ser {letra_calculada}")
        
        return v
    
    @field_validator("codigo_proveedor")
    @classmethod
    def validar_proveedor_por_tipo(cls, v: Optional[str], info) -> Optional[str]:
        """Regla de negocio: El código de proveedor debe ser válido según el tipo de seguro"""
        if v is None:
            return v
        
        tipo = info.data.get("tipo_seguro")
        if tipo and v not in CODIGOS_PROVEEDOR_VALIDOS.get(tipo, []):
            raise ValueError(f"Código '{v}' no válido para seguro {tipo}")
        return v

def validar_siniestro(siniestro: dict) -> dict:
    """
    Valida un siniestro. Si es válido, devuelve el objeto validado.
    Si no, lanza ValidationError con los detalles.
    """
    return SiniestroValidado(**siniestro).model_dump()

def limpiar_error(error: dict) -> dict:
    """Limpia un error de Pydantic para hacerlo JSON serializable"""
    error_limpio = {
        "type": error.get("type", ""),
        "loc": error.get("loc", []),
        "msg": error.get("msg", ""),
        "input": error.get("input"),
    }
    # Limpiar ctx si existe (puede contener objetos no serializables)
    if error.get("ctx"):
        ctx = error["ctx"]
        if isinstance(ctx, dict):
            error_limpio["ctx"] = {k: str(v) for k, v in ctx.items()}
        else:
            error_limpio["ctx"] = str(ctx)
    return error_limpio

def validar_lote(siniestros: list) -> tuple[list, list]:
    """
    Valida un lote completo.
    Retorna: (siniestros_validos, siniestros_invalidos_con_errores)
    """
    validos = []
    invalidos = []
    
    for idx, siniestro in enumerate(siniestros):
        try:
            validado = validar_siniestro(siniestro)
            validos.append(validado)
        except ValidationError as e:
             # Limpiar cada error para que sea serializable
            errores_limpios = [limpiar_error(err) for err in e.errors()]
            invalidos.append({
                "indice": idx,
                "siniestro_id": siniestro.get("siniestro_id"),
                "errores": errores_limpios,
                "datos_originales": siniestro
            })
    
    return validos, invalidos