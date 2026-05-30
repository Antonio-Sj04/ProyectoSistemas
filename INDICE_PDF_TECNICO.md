# Índice del Informe Técnico — Proyecto Final SO2
# "Infraestructura DevOps en AWS para Sistema de Inventario de Equipos TI"
# Antonio Samayoa | Mínimo 20 páginas

---

## PORTADA (1 página)
- Nombre del proyecto
- Materia: Sistemas Operativos II
- Nombre del estudiante: Antonio Samayoa
- Fecha de entrega
- Logo de la universidad

---

## ÍNDICE DE CONTENIDOS (1 página)

---

## 1. INTRODUCCIÓN (2 páginas)
### 1.1 Descripción del Problema
- Situación actual de la empresa ficticia (gestión manual de equipos)
- Problemas identificados: falta de trazabilidad, despliegue manual, sin monitoreo

### 1.2 Objetivos del Proyecto
- Objetivo general: migrar la infraestructura a la nube con automatización completa
- Objetivos específicos: CI/CD, alta disponibilidad, seguridad DevSecOps, monitoreo

### 1.3 Stack Tecnológico Justificado
- Por qué FastAPI vs Django/Flask
- Por qué PostgreSQL vs MySQL
- Por qué Docker Swarm vs Kubernetes (simplicidad, capa gratuita AWS)
- Por qué GitHub Actions vs Jenkins

---

## 2. ARQUITECTURA DEL SISTEMA (3 páginas)
### 2.1 Visión General
- Insertar Diagrama 1 (Arquitectura Cloud AWS en Mermaid/imagen)
- Descripción de cada componente y su rol

### 2.2 Diseño de Red en AWS
- Insertar Diagrama 3 (Diagrama de Red)
- Explicar VPC, subredes, routing tables, Internet Gateway
- Justificación de reglas del Security Group (principio de mínimo privilegio)

### 2.3 Orquestación con Docker Swarm
- Insertar Diagrama 4 (Servicios Swarm)
- Diferencia entre manager y worker nodes
- Red overlay y service discovery interno
- Rolling updates y zero-downtime deploys

---

## 3. BASE DE DATOS (2 páginas)
### 3.1 Modelo Entidad-Relación
- Diagrama ER con las 4 tablas (captura de DBeaver o draw.io)
- Descripción de cada entidad y sus atributos
- Relaciones y cardinalidades

### 3.2 Diseño DDL y ENUMs
- Explicar el uso de tipos ENUM en PostgreSQL para `tipo_equipo` y `estado_equipo`
- Mostrar fragmento clave del schema.sql

### 3.3 Trigger de Auditoría (OBLIGATORIO)
- Explicar qué es un trigger en PostgreSQL y cuándo se usa
- Mostrar el código completo del trigger `audit_cambio_estado`
- Demostrar con captura: ejecutar UPDATE en equipos → registro automático en historial_equipos
- Explicar la función PL/pgSQL `fn_audit_cambio_estado()`

### 3.4 Datos de Prueba
- Mostrar los datos dummy insertados
- Destacar las asignaciones a "Ana Lucia Pérez"
- Mostrar captura de DBeaver con los datos

---

## 4. DESARROLLO DE LA API REST (3 páginas)
### 4.1 Estructura de la Aplicación FastAPI
- Explicar la arquitectura en capas: routers → schemas → models → database
- Ventajas de separar responsabilidades

### 4.2 Endpoints Implementados
- Tabla con todos los endpoints (método, ruta, descripción)
- Captura de Swagger UI en funcionamiento

### 4.3 Validación con Pydantic
- Explicar cómo Pydantic v2 valida datos de entrada
- Ejemplo de schema con validación automática

### 4.4 Configuración con Variables de Entorno
- Por qué no hardcodear credenciales
- Uso de pydantic-settings para leer .env
- Cadena de conexión SQLAlchemy

### 4.5 Health Check y Métricas
- Endpoint /health para Docker Swarm
- prometheus-fastapi-instrumentator: métricas automáticas

---

## 5. CONTAINERIZACIÓN CON DOCKER (2 páginas)
### 5.1 Dockerfile Multi-Stage
- Explicar por qué multi-stage (imagen final más pequeña)
- Stage builder vs stage runtime
- Usuario no-root por seguridad
- Mostrar el Dockerfile completo con comentarios

### 5.2 Docker Compose (Desarrollo Local)
- Explicar cada servicio y sus configuraciones
- Volúmenes persistentes y su importancia
- Healthchecks: qué son y por qué son esenciales
- Cómo dependen los servicios entre sí (depends_on + condition)

---

## 6. INFRAESTRUCTURA COMO CÓDIGO — TERRAFORM (2 páginas)
### 6.1 ¿Qué es IaC y por qué usarla?
- Reproducibilidad: mismo comando = misma infraestructura
- Control de versiones de infraestructura
- Ventajas sobre crear recursos manualmente en la consola AWS

### 6.2 Recursos Creados en AWS
- VPC y componentes de red (subredes, IGW, route tables)
- Security Group: explicar cada regla y por qué existe
- EC2 Manager y Worker: t2.micro en capa gratuita
- User Data script: instalación automática de Docker

### 6.3 Outputs de Terraform
- IPs públicas usadas para SSH y GitHub Secrets
- Comandos SSH generados automáticamente

---

## 7. PIPELINE CI/CD CON GITHUB ACTIONS (3 páginas)
### 7.1 ¿Qué es CI/CD?
- Integración Continua: detectar errores rápido
- Despliegue Continuo: automatizar el camino al servidor
- Beneficio: de código en el laptop al servidor en minutos

### 7.2 Estructura del Pipeline
- Insertar Diagrama 2 (Pipeline CI/CD)
- Descripción de cada job y sus dependencias

### 7.3 Job 1 — Testing
- Ejecución de pytest en cada push
- Por qué testear antes de construir la imagen

### 7.4 Job 2 — Build, Scan & Push (DevSecOps)
- Build multi-plataforma con Docker Buildx
- Login seguro a Docker Hub usando Secrets (nunca credenciales en código)
- **Escaneo Trivy**: qué es, por qué es importante, qué detecta
- Política: fallar si hay vulnerabilidades HIGH o CRITICAL
- Push con doble tag (:latest y :SHA para trazabilidad)

### 7.5 Job 3 — Deploy Zero-Downtime
- SSH al Manager con clave privada desde GitHub Secrets
- `docker service update --image` con rolling update
- `order: start-first`: nueva réplica arranca ANTES de detener la vieja
- Verificación automática de réplicas en estado Running
- Limpieza de clave SSH del runner

### 7.6 GitHub Secrets
- Tabla de secrets requeridos y su propósito
- Cómo crearlos en la interfaz de GitHub

---

## 8. MONITOREO — PROMETHEUS + GRAFANA (2 páginas)
### 8.1 Stack de Observabilidad
- Qué es Prometheus y cómo funciona el scraping
- Qué es Grafana y para qué sirve
- Métricas que expone FastAPI automáticamente

### 8.2 Configuración de Prometheus
- Explicar prometheus.yml y los scrape_configs
- Jobs configurados: prometheus, API, node-exporter

### 8.3 Grafana con Provisioning Automático
- datasource.yml: configuración automática al arrancar
- Cómo crear un dashboard de latencia de la API
- Captura de pantalla del dashboard funcionando (opcional)

---

## 9. DEMOSTRACIÓN DEL SISTEMA (2 páginas)
### 9.1 Evidencias del Entorno Local
- Captura: `docker-compose up --build` exitoso
- Captura: Swagger UI con todos los endpoints
- Captura: DBeaver mostrando tablas con datos dummy
- Captura: trigger funcionando (UPDATE → historial)

### 9.2 Evidencias de AWS
- Captura: terraform apply exitoso con outputs de IPs
- Captura: consola AWS mostrando instancias EC2 running
- Captura: `docker node ls` mostrando manager + worker

### 9.3 Evidencias del Pipeline CI/CD
- Captura: pipeline GitHub Actions ejecutándose
- Captura: Trivy scan sin vulnerabilidades críticas
- Captura: Docker Hub con la imagen publicada
- Captura: `docker service ps inventario_api` con réplicas Running

---

## 10. CONCLUSIONES Y APRENDIZAJES (1 página)
### 10.1 Objetivos Logrados
- Resumen de todo lo implementado

### 10.2 Desafíos Encontrados
- Problemas técnicos específicos y cómo se resolvieron
  (ej: troubleshooting de networking en Swarm, configuración de Terraform)

### 10.3 Aprendizajes Clave
- Concepto de Zero-Downtime Deployment
- Importancia de nunca exponer credenciales
- IaC como buena práctica profesional
- DevSecOps: la seguridad como parte del pipeline

### 10.4 Mejoras Futuras
- Agregar autenticación JWT a la API
- Kubernetes en lugar de Swarm para mayor escala
- Base de datos RDS en lugar de contenedor
- HTTPS con Let's Encrypt + Nginx

---

## 11. BIBLIOGRAFÍA (1 página)
- Documentación oficial FastAPI: https://fastapi.tiangolo.com
- Documentación Docker Swarm: https://docs.docker.com/engine/swarm/
- Documentación Terraform AWS Provider: https://registry.terraform.io/providers/hashicorp/aws
- Documentación GitHub Actions: https://docs.github.com/en/actions
- Trivy scanner: https://aquasecurity.github.io/trivy/
- Prometheus: https://prometheus.io/docs/
- PostgreSQL Triggers: https://www.postgresql.org/docs/current/plpgsql-trigger.html

---

**Total estimado: ~20-25 páginas**
(Cada sección principal con capturas de pantalla y fragmentos de código puede extenderse fácilmente)
