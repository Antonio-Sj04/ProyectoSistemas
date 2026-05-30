# =============================================================================
# main.py — Punto de entrada de la API FastAPI
# Sistema de Inventario de Equipos TI — Proyecto Final SO2
# Antonio Samayoa
# =============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import HTMLResponse
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
        "syntaxHighlight.theme": "monokai",
        "tryItOutEnabled": True,
        "displayRequestDuration": True,
        "filter": True,
        "defaultModelsExpandDepth": 2,
        "layout": "BaseLayout",
        "docExpansion": "list",
    },
    # Desactivar docs por defecto para usar versión personalizada con modo oscuro
    docs_url=None,
    redoc_url=None,
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


@app.get("/docs", include_in_schema=False)
async def swagger_ui_dark() -> HTMLResponse:
    """Swagger UI con modo oscuro personalizado."""
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Inventario TI — API Docs</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    <style>
        /* ── Modo oscuro completo ── */
        body { margin: 0; background: #1a1a2e; }
        .swagger-ui { background: #1a1a2e; }
        .swagger-ui .topbar { background: #16213e; padding: 8px 0; }
        .swagger-ui .topbar-wrapper img { display: none; }
        .swagger-ui .topbar-wrapper::before {
            content: "🖥️  Sistema de Inventario de Equipos TI";
            color: #00d4ff; font-size: 1.3rem; font-weight: bold;
            font-family: 'Segoe UI', sans-serif; padding-left: 20px;
        }
        .swagger-ui .info { background: #16213e; border-radius: 12px; padding: 24px; margin: 20px; border-left: 4px solid #00d4ff; }
        .swagger-ui .info .title { color: #00d4ff; font-size: 2rem; }
        .swagger-ui .info p, .swagger-ui .info li, .swagger-ui .info td, .swagger-ui .info th { color: #c8d6e5; }
        .swagger-ui .info a { color: #00d4ff; }
        .swagger-ui .info table { border-collapse: collapse; width: 100%; }
        .swagger-ui .info th { background: #0f3460; color: #00d4ff; padding: 8px 12px; }
        .swagger-ui .info td { background: #1a1a2e; color: #c8d6e5; padding: 8px 12px; border: 1px solid #2d3561; }
        .swagger-ui .opblock-tag { color: #e2e8f0; background: #16213e; border: 1px solid #2d3561; border-radius: 8px; margin: 8px 20px; }
        .swagger-ui .opblock-tag:hover { background: #0f3460; }
        .swagger-ui .opblock-tag small { color: #94a3b8; }
        .swagger-ui .opblock { border-radius: 8px; margin: 4px 20px; border: none; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
        .swagger-ui .opblock .opblock-summary-description { color: #94a3b8; }
        .swagger-ui .opblock.opblock-get { background: #0d2137; border-left: 4px solid #3b82f6; }
        .swagger-ui .opblock.opblock-post { background: #0d2b1a; border-left: 4px solid #22c55e; }
        .swagger-ui .opblock.opblock-put { background: #2b1f0d; border-left: 4px solid #f59e0b; }
        .swagger-ui .opblock.opblock-delete { background: #2b0d0d; border-left: 4px solid #ef4444; }
        .swagger-ui .opblock-body, .swagger-ui .opblock-description-wrapper { background: #111827; color: #e2e8f0; }
        .swagger-ui .opblock-section-header { background: #1f2937; border-bottom: 1px solid #374151; }
        .swagger-ui .opblock-section-header label { color: #9ca3af; }
        .swagger-ui textarea, .swagger-ui input[type=text], .swagger-ui input[type=number] {
            background: #1f2937; color: #e2e8f0; border: 1px solid #374151; border-radius: 6px; padding: 8px;
        }
        .swagger-ui select { background: #1f2937; color: #e2e8f0; border: 1px solid #374151; }
        .swagger-ui .btn { border-radius: 6px; font-weight: 600; }
        .swagger-ui .btn.execute { background: #2563eb; border-color: #2563eb; }
        .swagger-ui .btn.execute:hover { background: #1d4ed8; }
        .swagger-ui .btn.cancel { background: #374151; border-color: #374151; color: #e2e8f0; }
        .swagger-ui .response-col_status { color: #22c55e; }
        .swagger-ui .response-col_description { color: #94a3b8; }
        .swagger-ui .model-box { background: #1f2937; border-radius: 8px; }
        .swagger-ui .model { color: #e2e8f0; }
        .swagger-ui .prop-type { color: #60a5fa; }
        .swagger-ui .prop-format { color: #a78bfa; }
        .swagger-ui table.model tr.property-row td { color: #c8d6e5; border-color: #374151; }
        .swagger-ui .parameter__name { color: #f0abfc; font-weight: bold; }
        .swagger-ui .parameter__type { color: #60a5fa; }
        .swagger-ui .parameter__in { color: #86efac; }
        .swagger-ui .markdown p, .swagger-ui .markdown li { color: #c8d6e5; }
        .swagger-ui .scheme-container { background: #16213e; box-shadow: none; padding: 12px 20px; }
        .swagger-ui section.models { background: #16213e; border-radius: 8px; margin: 20px; border: 1px solid #2d3561; }
        .swagger-ui section.models h4 { color: #00d4ff; }
        .swagger-ui .filter-container { background: #16213e; padding: 12px 20px; }
        .swagger-ui .filter-container input { background: #1f2937; color: #e2e8f0; border: 1px solid #374151; border-radius: 6px; }
        .swagger-ui .loading-container .loading::after { color: #00d4ff; }
        ::-webkit-scrollbar { width: 8px; } ::-webkit-scrollbar-track { background: #1a1a2e; }
        ::-webkit-scrollbar-thumb { background: #374151; border-radius: 4px; }
    </style>
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>
    SwaggerUIBundle({
        url: "/openapi.json",
        dom_id: '#swagger-ui',
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
        layout: "BaseLayout",
        tryItOutEnabled: true,
        displayRequestDuration: true,
        filter: true,
        syntaxHighlight: { theme: "monokai" },
        defaultModelsExpandDepth: 2,
        requestSnippetsEnabled: true,
    })
</script>
</body>
</html>
""")


@app.get("/redoc", include_in_schema=False)
async def redoc_ui() -> HTMLResponse:
    return get_redoc_html(openapi_url="/openapi.json", title="Inventario TI — Referencia API")


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
