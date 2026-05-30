# =============================================================================
# Dockerfile — Multi-stage build para la API FastAPI
# Proyecto Final SO2 — Antonio Samayoa
#
# Stage 1 (builder): instala todas las dependencias en un entorno aislado
# Stage 2 (runtime): imagen final ligera con solo lo necesario para ejecutar
# =============================================================================

# ---- Stage 1: Builder ----
# Usamos la imagen completa para poder compilar dependencias nativas (psycopg2)
FROM python:3.11-slim AS builder

WORKDIR /build

# Copiar solo el archivo de dependencias primero (optimiza cache de Docker)
COPY requirements.txt .

# Instalar dependencias en un directorio local (no en el sistema)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---- Stage 2: Runtime ----
# Imagen final ligera — no contiene compiladores ni herramientas de desarrollo
FROM python:3.11-slim AS runtime

# Metadatos de la imagen
LABEL maintainer="Antonio Samayoa"
LABEL description="Sistema de Inventario de Equipos TI - API FastAPI"
LABEL version="1.0.0"

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/install/bin:$PATH" \
    PYTHONPATH="/install/lib/python3.11/site-packages:$PYTHONPATH"

WORKDIR /app

# Copiar dependencias compiladas desde el stage builder
COPY --from=builder /install /install

# Copiar el código fuente de la aplicación
COPY app/ ./app/

# Copiar el archivo .env.example como referencia (el real se monta en runtime)
COPY .env.example .env.example

# Crear usuario no-root por seguridad (principio de mínimo privilegio)
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app

# Ejecutar como usuario no-root
USER appuser

# Puerto en el que escucha uvicorn
EXPOSE 8000

# Comando de inicio — workers=1 para contenedores (el Swarm escala con réplicas)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
