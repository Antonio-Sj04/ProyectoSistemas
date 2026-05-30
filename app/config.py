# =============================================================================
# config.py — Configuración centralizada con pydantic-settings
# Lee variables de entorno y del archivo .env automáticamente
# =============================================================================

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # URL de conexión a PostgreSQL (construida por docker-compose o .env)
    DATABASE_URL: str = "postgresql://usuario:password@localhost:5432/inventario_ti"

    # Clave secreta para tokens (no se usa en este proyecto pero es buena práctica)
    SECRET_KEY: str = "cambia_esto_en_produccion"

    # Nombre de la aplicación
    APP_NAME: str = "Sistema de Inventario de Equipos TI"
    APP_VERSION: str = "1.0.0"

    class Config:
        # Busca el archivo .env en el directorio donde se ejecuta la app
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instancia global de configuración — se importa desde otros módulos
settings = Settings()
