# =============================================================================
# main.py — Punto de entrada de la API FastAPI
# Sistema de Inventario de Equipos TI — Proyecto Final SO2
# Antonio Samayoa
# =============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.database import engine, Base
from app.routers import departamentos, equipos, asignaciones

Base.metadata.create_all(bind=engine)

# Metadatos de los tags — aparecen como secciones con descripción en Swagger
tags_metadata = [
    {
        "name": "Departamentos",
        "description": "Gestión de los **departamentos** de la empresa. "
                       "Cada equipo pertenece a un departamento.",
    },
    {
        "name": "Equipos",
        "description": "Catálogo completo de **equipos TI**: laptops, switches POE y servidores. "
                       "Al cambiar el campo `estado`, el **trigger SQL** registra automáticamente "
                       "el cambio en el historial de auditoría.",
    },
    {
        "name": "Asignaciones",
        "description": "Control de **asignaciones** de equipos a empleados. "
                       "Registra responsable, fecha de asignación y devolución.",
    },
    {
        "name": "Health",
        "description": "Endpoints de salud usados por **Docker Swarm** y balanceadores de carga.",
    },
    {
        "name": "Root",
        "description": "Información general de la API.",
    },
]

app = FastAPI(
    title="Sistema de Inventario de Equipos TI",
    version="1.0.0",
    description="""
## Sistema de Inventario de Equipos TI

API REST para gestionar el inventario de equipos tecnológicos de una empresa.
Desarrollada como **Proyecto Final de Sistemas Operativos II**.

---

### Infraestructura DevOps
| Componente | Tecnología |
|-----------|-----------|
| Backend | Python 3.11 + FastAPI |
| Base de Datos | PostgreSQL 15 con Trigger de auditoría |
| Contenedores | Docker + Docker Swarm |
| CI/CD | GitHub Actions + Trivy (DevSecOps) |
| Nube | AWS EC2 + Terraform |
| Monitoreo | Prometheus + Grafana |

---

### Funcionalidades
- **CRUD completo** para Departamentos, Equipos y Asignaciones
- **Trigger SQL `audit_cambio_estado`** — registra automáticamente cada cambio de estado en `historial_equipos`
- **Health check** en `/health` para Docker Swarm
- **Métricas** en `/metrics` para Prometheus

---

### Datos de prueba incluidos
La base de datos incluye datos dummy con **5 departamentos** (Administración, Redes, etc.),
**10 equipos** variados y asignaciones incluyendo a **Ana Lucia Pérez**.
    """,
    openapi_tags=tags_metadata,
    contact={
        "name": "Antonio Samayoa",
        "url": "https://github.com/Antonio-Sj04/ProyectoSistemas",
        "email": "antoniosamayoa5@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    swagger_ui_parameters={
        "syntaxHighlight.theme": "monokai",   # Tema oscuro para el código
        "tryItOutEnabled": True,               # Habilitar "Try it out" por defecto
        "displayRequestDuration": True,        # Mostrar tiempo de cada request
        "filter": True,                        # Barra de búsqueda de endpoints
        "defaultModelsExpandDepth": 2,         # Expandir modelos automáticamente
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(departamentos.router)
app.include_router(equipos.router)
app.include_router(asignaciones.router)

Instrumentator().instrument(app).expose(app)


@app.get("/", tags=["Root"], summary="Informacion de la API")
def root():
    """Ruta raíz — devuelve información general y enlaces útiles."""
    return {
        "nombre": "Sistema de Inventario de Equipos TI",
        "version": "1.0.0",
        "descripcion": "API REST para gestión de inventario TI desplegada en AWS con Docker Swarm",
        "documentacion": "/docs",
        "redoc": "/redoc",
        "metricas": "/metrics",
        "salud": "/health",
        "repositorio": "https://github.com/Antonio-Sj04/ProyectoSistemas",
    }


@app.get("/health", tags=["Health"], summary="Health check para Docker Swarm")
def health_check():
    """
    Endpoint de salud usado por Docker Swarm y nginx.
    Retorna `200 OK` cuando la API está lista para recibir tráfico.
    Usado por el `healthcheck` definido en `production-stack.yml`.
    """
    return {
        "status": "healthy",
        "service": "inventario-api",
        "version": "1.0.0",
    }
