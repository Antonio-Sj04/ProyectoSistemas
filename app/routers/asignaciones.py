# =============================================================================
# routers/asignaciones.py — Endpoints CRUD para Asignaciones de equipos
# =============================================================================

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Asignacion, Equipo
from app.schemas import AsignacionCreate, AsignacionUpdate, AsignacionResponse

router = APIRouter(prefix="/asignaciones", tags=["Asignaciones"])


@router.get("/", response_model=List[AsignacionResponse], summary="Listar todas las asignaciones")
def listar_asignaciones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Asignacion).offset(skip).limit(limit).all()


@router.get("/{asig_id}", response_model=AsignacionResponse, summary="Obtener asignación por ID")
def obtener_asignacion(asig_id: int, db: Session = Depends(get_db)):
    asig = db.query(Asignacion).filter(Asignacion.id == asig_id).first()
    if not asig:
        raise HTTPException(status_code=404, detail=f"Asignación {asig_id} no encontrada")
    return asig


@router.post("/", response_model=AsignacionResponse, status_code=status.HTTP_201_CREATED,
             summary="Registrar nueva asignación")
def crear_asignacion(payload: AsignacionCreate, db: Session = Depends(get_db)):
    """
    Crea una asignación. Valida que el equipo exista.
    Nota: cambiar el estado del equipo a 'asignado' se hace mediante el endpoint PUT /equipos/{id}.
    """
    equipo = db.query(Equipo).filter(Equipo.id == payload.equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail=f"Equipo {payload.equipo_id} no encontrado")

    nueva = Asignacion(**payload.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@router.put("/{asig_id}", response_model=AsignacionResponse, summary="Actualizar asignación")
def actualizar_asignacion(asig_id: int, payload: AsignacionUpdate, db: Session = Depends(get_db)):
    """Útil para registrar la fecha de devolución cuando se devuelve el equipo."""
    asig = db.query(Asignacion).filter(Asignacion.id == asig_id).first()
    if not asig:
        raise HTTPException(status_code=404, detail=f"Asignación {asig_id} no encontrada")

    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(asig, campo, valor)

    db.commit()
    db.refresh(asig)
    return asig


@router.delete("/{asig_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar asignación")
def eliminar_asignacion(asig_id: int, db: Session = Depends(get_db)):
    asig = db.query(Asignacion).filter(Asignacion.id == asig_id).first()
    if not asig:
        raise HTTPException(status_code=404, detail=f"Asignación {asig_id} no encontrada")

    db.delete(asig)
    db.commit()
