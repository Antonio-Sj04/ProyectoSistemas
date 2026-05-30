# =============================================================================
# routers/departamentos.py — Endpoints CRUD para Departamentos
# =============================================================================

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Departamento
from app.schemas import DepartamentoCreate, DepartamentoUpdate, DepartamentoResponse

# Prefijo /departamentos aplicado a todas las rutas de este router
router = APIRouter(prefix="/departamentos", tags=["Departamentos"])


@router.get("/", response_model=List[DepartamentoResponse], summary="Listar todos los departamentos")
def listar_departamentos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Devuelve la lista completa de departamentos con paginación opcional."""
    return db.query(Departamento).offset(skip).limit(limit).all()


@router.get("/{dep_id}", response_model=DepartamentoResponse, summary="Obtener departamento por ID")
def obtener_departamento(dep_id: int, db: Session = Depends(get_db)):
    """Busca un departamento por su ID. Devuelve 404 si no existe."""
    dep = db.query(Departamento).filter(Departamento.id == dep_id).first()
    if not dep:
        raise HTTPException(status_code=404, detail=f"Departamento {dep_id} no encontrado")
    return dep


@router.post("/", response_model=DepartamentoResponse, status_code=status.HTTP_201_CREATED,
             summary="Crear nuevo departamento")
def crear_departamento(payload: DepartamentoCreate, db: Session = Depends(get_db)):
    """Crea un nuevo departamento. El nombre debe ser único."""
    existente = db.query(Departamento).filter(Departamento.nombre == payload.nombre).first()
    if existente:
        raise HTTPException(status_code=409, detail=f"Ya existe un departamento con el nombre '{payload.nombre}'")

    nuevo = Departamento(**payload.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{dep_id}", response_model=DepartamentoResponse, summary="Actualizar departamento")
def actualizar_departamento(dep_id: int, payload: DepartamentoUpdate, db: Session = Depends(get_db)):
    """Actualiza los campos enviados de un departamento existente."""
    dep = db.query(Departamento).filter(Departamento.id == dep_id).first()
    if not dep:
        raise HTTPException(status_code=404, detail=f"Departamento {dep_id} no encontrado")

    # Solo actualiza los campos que vienen en el payload (excluye None)
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(dep, campo, valor)

    db.commit()
    db.refresh(dep)
    return dep


@router.delete("/{dep_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar departamento")
def eliminar_departamento(dep_id: int, db: Session = Depends(get_db)):
    """Elimina un departamento. Los equipos asociados quedan sin departamento (SET NULL)."""
    dep = db.query(Departamento).filter(Departamento.id == dep_id).first()
    if not dep:
        raise HTTPException(status_code=404, detail=f"Departamento {dep_id} no encontrado")

    db.delete(dep)
    db.commit()
