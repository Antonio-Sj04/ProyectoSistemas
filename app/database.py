# =============================================================================
# database.py — Configuración de la conexión a PostgreSQL
# Usa SQLAlchemy con variables de entorno para no exponer credenciales
# =============================================================================

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Motor de base de datos — se conecta a PostgreSQL usando la URL del .env
engine = create_engine(
    settings.DATABASE_URL,
    # Pool de conexiones: máximo 10 conexiones simultáneas
    pool_size=10,
    max_overflow=20,
    # Verifica la conexión antes de usar del pool (evita errores por timeout)
    pool_pre_ping=True,
)

# Fábrica de sesiones — cada request HTTP obtiene su propia sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para todos los modelos ORM
Base = declarative_base()


# Dependencia de FastAPI: genera una sesión de BD por request y la cierra al terminar
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
