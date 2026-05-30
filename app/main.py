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

# -----------------------------------------------------------------------------
# Crear todas las tablas en la BD (si no existen aún)
# En producción se usa Alembic para migraciones controladas,
# pero para desarrollo local esto es suficiente.
# -----------------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

# -----------------------------------------------------------------------------
# Instancia principal de FastAPI con metadata para Swagger UI
# Acceder a la documentación en: http://localhost:8000/docs
# -----------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Sistema de Inventario de Equipos TI

API REST para gestionar el inventario de equipos tecnológicos de la empresa.

### Funcionalidades principales:
* **Departamentos** — CRUD completo de departamentos
* **Equipos** — Gestión de laptops, switches y servidores
* **Asignaciones** — Control de qué empleado tiene qué equipo
* **Historial** — Auditoría automática de cambios de estado (vía trigger SQL)

### Credenciales de acceso:
No requiere autenticación en esta versión (agregar JWT en producción).
    """,
    contact={
        "name": "Antonio Samayoa",
        "url": "https://github.com/Antonio-Sj04/ProyectoSistemas",
    },
    license_info={
        "name": "MIT",
    },
)

# -----------------------------------------------------------------------------
# Middleware CORS: permite que frontends externos accedan a la API
# En producción, reemplazar "*" con el dominio específico del frontend
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # En prod: ["https://mi-frontend.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Registro de routers — cada uno maneja un grupo de endpoints
# -----------------------------------------------------------------------------
app.include_router(departamentos.router)
app.include_router(equipos.router)
app.include_router(asignaciones.router)

# -----------------------------------------------------------------------------
# Métricas Prometheus — expone /metrics para que Prometheus las recolecte
# El middleware instrumenta automáticamente latencia, conteo de requests, etc.
# -----------------------------------------------------------------------------
Instrumentator().instrument(app).expose(app)

# -----------------------------------------------------------------------------
# Endpoints raíz y health check
# -----------------------------------------------------------------------------

@app.get("/", tags=["Root"], summary="Bienvenida de la API")
def root():
    """Ruta raíz — confirma que la API está corriendo."""
    return {
        "mensaje": "Bienvenido al Sistema de Inventario de Equipos TI",
        "version": settings.APP_VERSION,
        "documentacion": "/docs",
        "metricas": "/metrics",
    }


@app.get("/health", tags=["Health"], summary="Health check para Docker Swarm")
def health_check():
    """
    Endpoint de salud usado por Docker Swarm y load balancers.
    Devuelve 200 OK cuando la API está lista para recibir tráfico.
    """
    return {"status": "healthy", "service": "inventario-api"}
