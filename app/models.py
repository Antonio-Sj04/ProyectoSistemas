# =============================================================================
# models.py — Modelos ORM (SQLAlchemy)
# Mapean las tablas de PostgreSQL a clases Python
# =============================================================================

import enum
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime,
    Enum, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.database import Base


# Enums de Python que coinciden con los ENUMs de PostgreSQL
class TipoEquipo(str, enum.Enum):
    laptop     = "laptop"
    switch_poe = "switch_poe"
    servidor   = "servidor"


class EstadoEquipo(str, enum.Enum):
    bodega       = "bodega"
    asignado     = "asignado"
    mantenimiento = "mantenimiento"


# -----------------------------------------------------------------------------
# Modelo: Departamento
# -----------------------------------------------------------------------------
class Departamento(Base):
    __tablename__ = "departamentos"

    id         = Column(Integer, primary_key=True, index=True)
    nombre     = Column(String(100), unique=True, nullable=False)
    ubicacion  = Column(String(150))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación: un departamento tiene muchos equipos
    equipos = relationship("Equipo", back_populates="departamento")


# -----------------------------------------------------------------------------
# Modelo: Equipo
# -----------------------------------------------------------------------------
class Equipo(Base):
    __tablename__ = "equipos"

    id              = Column(Integer, primary_key=True, index=True)
    nombre          = Column(String(150), nullable=False)
    # name= debe coincidir exactamente con el ENUM creado en schema.sql
    tipo            = Column(Enum(TipoEquipo,   name="tipo_equipo"),   nullable=False)
    estado          = Column(Enum(EstadoEquipo, name="estado_equipo"), nullable=False, default=EstadoEquipo.bodega)
    numero_serie    = Column(String(100), unique=True, nullable=False)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    departamento = relationship("Departamento", back_populates="equipos")
    asignaciones = relationship("Asignacion", back_populates="equipo")
    historial    = relationship("HistorialEquipo", back_populates="equipo")


# -----------------------------------------------------------------------------
# Modelo: Asignacion
# -----------------------------------------------------------------------------
class Asignacion(Base):
    __tablename__ = "asignaciones"

    id                = Column(Integer, primary_key=True, index=True)
    equipo_id         = Column(Integer, ForeignKey("equipos.id"), nullable=False)
    responsable       = Column(String(150), nullable=False)
    fecha_asignacion  = Column(Date, default=date.today)
    fecha_devolucion  = Column(Date, nullable=True)
    notas             = Column(Text, nullable=True)

    equipo = relationship("Equipo", back_populates="asignaciones")


# -----------------------------------------------------------------------------
# Modelo: HistorialEquipo (tabla de auditoría — poblada por el trigger)
# -----------------------------------------------------------------------------
class HistorialEquipo(Base):
    __tablename__ = "historial_equipos"

    id               = Column(Integer, primary_key=True, index=True)
    equipo_id        = Column(Integer, ForeignKey("equipos.id"), nullable=False)
    estado_anterior  = Column(Enum(EstadoEquipo, name="estado_equipo"), nullable=False)
    estado_nuevo     = Column(Enum(EstadoEquipo, name="estado_equipo"), nullable=False)
    cambiado_en      = Column(DateTime(timezone=True), server_default=func.now())
    cambiado_por     = Column(String(100), default="api_user")

    equipo = relationship("Equipo", back_populates="historial")
