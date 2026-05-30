# =============================================================================
# routers/equipos.py — Endpoints CRUD para Equipos + Historial de Auditoría
# IMPORTANTE: al cambiar el campo 'estado', el trigger SQL dispara automáticamente
# la inserción en historial_equipos — no es necesario hacerlo manualmente aquí.
# =============================================================================

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Equipo, HistorialEquipo
from app.schemas import (
    EquipoCreate, EquipoUpdate, EquipoResponse, HistorialResponse
)

router = APIRouter(prefix="/equipos", tags=["Equipos"])


@router.get("/", response_model=List[EquipoResponse], summary="Listar todos los equipos")
def listar_equipos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Devuelve todos los equipos del inventario con paginación opcional."""
    return db.query(Equipo).offset(skip).limit(limit).all()


@router.get("/{equipo_id}", response_model=EquipoResponse, summary="Obtener equipo por ID")
def obtener_equipo(equipo_id: int, db: Session = Depends(get_db)):
    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail=f"Equipo {equipo_id} no encontrado")
    return equipo


@router.post("/", response_model=EquipoResponse, status_code=status.HTTP_201_CREATED,
             summary="Registrar nuevo equipo")
def crear_equipo(payload: EquipoCreate, db: Session = Depends(get_db)):
    """Registra un equipo nuevo. El número de serie debe ser único."""
    existente = db.query(Equipo).filter(Equipo.numero_serie == payload.numero_serie).first()
    if existente:
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe un equipo con el número de serie '{payload.numero_serie}'"
        )

    nuevo = Equipo(**payload.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{equipo_id}", response_model=EquipoResponse, summary="Actualizar equipo")
def actualizar_equipo(equipo_id: int, payload: EquipoUpdate, db: Session = Depends(get_db)):
    """
    Actualiza un equipo. Si se cambia el campo 'estado', el trigger SQL
    audit_cambio_estado registrará el cambio automáticamente en historial_equipos.
    """
    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail=f"Equipo {equipo_id} no encontrado")

    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(equipo, campo, valor)

    db.commit()
    db.refresh(equipo)
    return equipo


@router.delete("/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar equipo")
def eliminar_equipo(equipo_id: int, db: Session = Depends(get_db)):
    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail=f"Equipo {equipo_id} no encontrado")

    db.delete(equipo)
    db.commit()


# -----------------------------------------------------------------------------
# Endpoint de Auditoría — lee el historial generado por el trigger SQL
# -----------------------------------------------------------------------------
@router.get("/{equipo_id}/historial", response_model=List[HistorialResponse],
            summary="Ver historial de cambios de estado de un equipo")
def ver_historial(equipo_id: int, db: Session = Depends(get_db)):
    """
    Devuelve todos los cambios de estado de un equipo.
    Este historial es generado automáticamente por el trigger 'audit_cambio_estado'.
    """
    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail=f"Equipo {equipo_id} no encontrado")

    return (
        db.query(HistorialEquipo)
        .filter(HistorialEquipo.equipo_id == equipo_id)
        .order_by(HistorialEquipo.cambiado_en.desc())
        .all()
    )
