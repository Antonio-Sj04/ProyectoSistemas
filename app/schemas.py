# =============================================================================
# schemas.py — Schemas Pydantic para validación de datos de entrada/salida
# Pydantic v2 garantiza que la API rechace datos malformados automáticamente
# =============================================================================

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models import TipoEquipo, EstadoEquipo


# =============================================================================
# SCHEMAS DE DEPARTAMENTO
# =============================================================================

class DepartamentoBase(BaseModel):
    nombre: str
    ubicacion: Optional[str] = None


class DepartamentoCreate(DepartamentoBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Tecnología",
                "ubicacion": "Edificio D, Piso 2"
            }
        }
    )


class DepartamentoUpdate(BaseModel):
    nombre: Optional[str] = None
    ubicacion: Optional[str] = None


class DepartamentoResponse(DepartamentoBase):
    id: int
    created_at: datetime

    # Permite leer atributos de objetos ORM (no solo dicts)
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# SCHEMAS DE EQUIPO
# =============================================================================

class EquipoBase(BaseModel):
    nombre: str
    tipo: TipoEquipo
    estado: EstadoEquipo = EstadoEquipo.bodega
    numero_serie: str
    departamento_id: Optional[int] = None


class EquipoCreate(EquipoBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Dell Latitude 5550",
                "tipo": "laptop",
                "estado": "bodega",
                "numero_serie": "DL5550-011-GT",
                "departamento_id": 1
            }
        }
    )


class EquipoUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[TipoEquipo] = None
    estado: Optional[EstadoEquipo] = None
    numero_serie: Optional[str] = None
    departamento_id: Optional[int] = None


class EquipoResponse(EquipoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# SCHEMAS DE ASIGNACION
# =============================================================================

class AsignacionBase(BaseModel):
    equipo_id: int
    responsable: str
    fecha_asignacion: date = date.today()
    fecha_devolucion: Optional[date] = None
    notas: Optional[str] = None


class AsignacionCreate(AsignacionBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "equipo_id": 3,
                "responsable": "María García",
                "fecha_asignacion": "2026-05-30",
                "fecha_devolucion": None,
                "notas": "Asignado para trabajo remoto"
            }
        }
    )


class AsignacionUpdate(BaseModel):
    responsable: Optional[str] = None
    fecha_devolucion: Optional[date] = None
    notas: Optional[str] = None


class AsignacionResponse(AsignacionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# SCHEMAS DE HISTORIAL (solo lectura — lo genera el trigger)
# =============================================================================

class HistorialResponse(BaseModel):
    id: int
    equipo_id: int
    estado_anterior: EstadoEquipo
    estado_nuevo: EstadoEquipo
    cambiado_en: datetime
    cambiado_por: Optional[str]

    model_config = ConfigDict(from_attributes=True)
