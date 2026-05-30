# 📋 HANDOFF — AWS DevOps Infrastructure Project
### Proyecto Final: Sistemas Operativos II (SO2)

---

## 📌 Información General

| Campo | Detalle |
|---|---|
| **Proyecto** | AWS DevOps Infrastructure — Sistema de Inventario de Equipos TI |
| **Curso** | Sistemas Operativos II (SO2) |
| **Responsable** | Antonio Samayoa |
| **Repositorio GitHub** | `https://github.com/Antonio-Sj04/ProyectoSistemas` |
| **Rama principal** | `main` |
| **Fecha de último avance** | 30 de mayo de 2026 |
| **Estado actual** | 🟡 En progreso — Fase de ejecución en Claude Code |

---

## 🎯 Objetivo del Proyecto

Construir una infraestructura DevOps completa en AWS que simula la migración de una empresa ficticia a la nube con CI/CD completamente automatizado. El proyecto cubre desde el desarrollo local hasta el despliegue en producción con monitoreo.

---

## 🛠️ Stack Tecnológico Definido

| Capa | Tecnología |
|---|---|
| **Backend** | Python 3.11 + FastAPI (Swagger UI) |
| **Base de Datos** | PostgreSQL 15 |
| **Containerización** | Docker (multi-stage build) |
| **Orquestación** | Docker Swarm |
| **IaC (Infraestructura como Código)** | Terraform |
| **Cloud** | AWS (us-east-1) — EC2, VPC, Security Groups |
| **CI/CD** | GitHub Actions |
| **DevSecOps** | Trivy (escaneo de vulnerabilidades) |
| **Monitoreo** | Prometheus + Grafana |
| **Balanceo de carga** | Nginx |
| **Registro de imágenes** | Docker Hub |

---

## 💻 Entorno Local Configurado

- ✅ Windows 11 + VS Code
- ✅ Python 3.11 + venv activado
- ✅ Docker Desktop (WSL2, AMD64)
- ✅ Git + GitHub conectado al repo `ProyectoSistemas` en rama `main`
- ✅ DBeaver instalado
- ✅ Claude Code instalado y operativo

---

## 📁 Estructura de Archivos Planificada

```
ProyectoSistemas/
├── app/
│   ├── main.py                  # Entrada FastAPI, CORS, metadata
│   ├── database.py              # Conexión SQLAlchemy + .env
│   ├── models.py                # Modelos ORM de las 4 tablas
│   ├── schemas.py               # Schemas Pydantic (request/response)
│   └── routers/
│       ├── departamentos.py     # CRUD completo
│       ├── equipos.py           # CRUD completo
│       └── asignaciones.py      # CRUD completo
├── sql/
│   └── schema.sql               # DDL + trigger + datos dummy
├── terraform/
│   └── main.tf                  # VPC, EC2 x2, SG, IGW, outputs
├── monitoring/
│   ├── prometheus.yml           # Scrape jobs: api, ec2, prometheus
│   └── grafana/
│       └── datasource.yml       # Provisioning automático
├── .github/
│   └── workflows/
│       └── deploy.yml           # Pipeline CI/CD de 3 jobs
├── requirements.txt
├── Dockerfile                   # Multi-stage build
├── docker-compose.yml           # Stack de desarrollo local
├── production-stack.yml         # Docker Swarm stack de producción
├── .env.example
├── .gitignore
└── README.md
```

---

## 🗄️ Base de Datos — Esquema SQL

### Tablas definidas

| Tabla | Campos principales |
|---|---|
| `departamentos` | id, nombre, ubicacion, created_at |
| `equipos` | id, nombre, tipo (ENUM), estado (ENUM), numero_serie, departamento_id, created_at, updated_at |
| `asignaciones` | id, equipo_id, responsable, fecha_asignacion, fecha_devolucion, notas |
| `historial_equipos` | id, equipo_id, estado_anterior, estado_nuevo, cambiado_en, cambiado_por |

### ENUMs definidos
- `tipo`: `laptop`, `switch_poe`, `servidor`
- `estado`: `bodega`, `asignado`, `mantenimiento`

### Trigger obligatorio
```sql
-- Se dispara AFTER UPDATE en `equipos` cuando cambia el campo `estado`
-- Inserta automáticamente un registro en `historial_equipos`
TRIGGER: audit_cambio_estado
```

### Datos dummy requeridos
- Mínimo 4 departamentos (incluir **"Administración"** y **"Redes"**)
- Mínimo 10 equipos variados
- Al menos 3 asignaciones, incluyendo una a nombre de **"Ana Lucia Pérez"**

---

## 🔌 API Endpoints Planificados

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Metadata de la API |
| GET | `/health` | Health check para Docker Swarm |
| GET/POST | `/departamentos` | Listar y crear departamentos |
| GET/PUT/DELETE | `/departamentos/{id}` | Detalle, editar y eliminar |
| GET/POST | `/equipos` | Listar y crear equipos |
| GET/PUT/DELETE | `/equipos/{id}` | Detalle, editar y eliminar |
| GET/POST | `/asignaciones` | Listar y crear asignaciones |
| GET/PUT/DELETE | `/asignaciones/{id}` | Detalle, editar y eliminar |
| GET | `/historial/{equipo_id}` | Ver auditoría de cambios de estado |
| GET | `/metrics` | Métricas para Prometheus |

---

## ☁️ Infraestructura AWS — Terraform

### Recursos a crear (`terraform/main.tf`)

| Recurso | Detalle |
|---|---|
| **Provider** | AWS, región `us-east-1` |
| **VPC** | CIDR `10.0.0.0/16` |
| **Internet Gateway** | Adjunto a la VPC |
| **Subred pública** | `10.0.1.0/24` en AZ `us-east-1a` |
| **Route Table** | Ruta `0.0.0.0/0` al IGW |
| **Security Group** | Puertos: 22 (SSH), 80 (HTTP), 443 (HTTPS), 8000 (API-VPC), 9090 (Prometheus-VPC), 3000 (Grafana), 2377/7946/4789 (Docker Swarm interno) |
| **EC2 `swarm-manager`** | t2.micro, Amazon Linux 2023, IP pública, Docker auto-instalado |
| **EC2 `swarm-worker`** | t2.micro, Amazon Linux 2023, IP pública, Docker auto-instalado |
| **Key Pair** | Para acceso SSH |
| **Outputs** | IPs públicas de manager y worker |

---

## 🐳 Docker Swarm — Stack de Producción

### Servicios en `production-stack.yml`

| Servicio | Imagen | Réplicas | Puertos |
|---|---|---|---|
| `api` | `${DOCKER_HUB_USER}/inventario-ti:latest` | **2 réplicas** (zero-downtime) | 8000 (interno) |
| `db` | `postgres:15-alpine` | 1 (constraint: manager) | 5432 (interno) |
| `nginx` | `nginx:alpine` | 1 | **80 → público** |
| `prometheus` | `prom/prometheus:latest` | 1 | 9090 |
| `grafana` | `grafana/grafana:latest` | 1 | **3000 → público** |

- **Red overlay:** `red-produccion`
- **Volúmenes:** `postgres_data`, `grafana_data`, `prometheus_data`
- **Zero-Downtime:** `update_config: parallelism 1, delay 10s, order start-first`

---

## 🔄 Pipeline CI/CD — GitHub Actions

### Flujo del pipeline (`deploy.yml`)

```
Push a main
    │
    ▼
JOB 1: test
    ├── Checkout código
    ├── Setup Python 3.11
    ├── pip install -r requirements.txt
    └── pytest (tests básicos)
    │
    ▼ (needs: test)
JOB 2: build-and-scan
    ├── Login a Docker Hub
    ├── Build imagen :latest y :${{ github.sha }}
    ├── 🔒 Trivy scan (falla si severidad HIGH o CRITICAL)
    └── Push imagen a Docker Hub
    │
    ▼ (needs: build-and-scan)
JOB 3: deploy
    ├── SSH al EC2 Manager
    ├── docker service update --image nueva_imagen inventario_api
    └── docker service ps (verificación)
```

### GitHub Secrets requeridos (configurar manualmente)

| Secret | Valor |
|---|---|
| `DOCKER_USERNAME` | Tu usuario de Docker Hub |
| `DOCKER_TOKEN` | Token de acceso de Docker Hub |
| `EC2_HOST` | IP pública del EC2 Manager |
| `EC2_USER` | `ec2-user` |
| `EC2_SSH_KEY` | Contenido completo del archivo `.pem` |

---

## 📊 Monitoreo — Prometheus + Grafana

### Scrape jobs de Prometheus
- `prometheus` (el propio servicio)
- `api` — endpoint `/metrics` con `prometheus-fastapi-instrumentator`
- `node` — métricas de los nodos EC2 (con `node_exporter`)

### Grafana
- Provisioning automático del datasource de Prometheus
- Dashboard accesible en `http://<ec2-manager-ip>:3000`

---

## 📐 Diagramas Mermaid (obligatorios)

Se deben generar 4 diagramas:

1. **Arquitectura Cloud AWS** — Usuario → Internet → IGW → VPC → EC2 Manager/Worker → Volumes
2. **Pipeline CI/CD** — Developer Push → GitHub → Actions → Test → Build → Trivy → DockerHub → SSH → Swarm Update
3. **Diagrama de Red** — Internet → Security Group → VPC 10.0.0.0/16 → Subred → EC2 Manager ↔ EC2 Worker
4. **Contenedores/Servicios Swarm** — Nginx → [API x2] → PostgreSQL | Prometheus → API/Node | Grafana → Prometheus

---

## ✅ Lo Que Está Hecho

| Ítem | Estado |
|---|---|
| Definición completa del stack tecnológico | ✅ Listo |
| Esquema de base de datos (tablas, ENUMs, trigger) | ✅ Definido |
| Datos dummy especificados (Ana Lucia, Administración, Redes) | ✅ Definido |
| Estructura completa de archivos planificada | ✅ Definida |
| Especificación de todos los endpoints API | ✅ Definida |
| Especificación de infraestructura Terraform | ✅ Definida |
| Especificación del stack Swarm de producción | ✅ Definida |
| Especificación del pipeline CI/CD (3 jobs + Trivy) | ✅ Definida |
| Especificación de monitoreo Prometheus/Grafana | ✅ Definida |
| Prompt maestro generado para Claude Code | ✅ `PROMPT_CLAUDE_CODE.md` |
| Entorno local configurado (Docker, Git, Python) | ✅ Confirmado |

---

## 🚧 Lo Que Falta Por Hacer

### Inmediato — Resolver el problema de Claude Code
- [ ] Resolver el error de rate limiting / créditos de contexto 1M (ver sección de problemas)
- [ ] Usar `claude --model claude-sonnet-4-20250514` para contexto estándar

### Fase 1 — Desarrollo Local
- [ ] Ejecutar Claude Code con el prompt maestro para generar todos los archivos
- [ ] Verificar que `sql/schema.sql` se ejecuta correctamente en DBeaver
- [ ] Probar la API localmente: `docker-compose up --build`
- [ ] Verificar Swagger en `http://localhost:8000/docs`
- [ ] Hacer primer commit y push a `main`

### Fase 2 — Infraestructura AWS
- [ ] Crear cuenta/configurar AWS CLI con credenciales
- [ ] `terraform init` → `terraform plan` → `terraform apply`
- [ ] Anotar las IPs públicas de `swarm-manager` y `swarm-worker` del output

### Fase 3 — Docker Swarm
- [ ] SSH al manager: `ssh -i clave.pem ec2-user@<manager-ip>`
- [ ] Inicializar Swarm: `docker swarm init --advertise-addr <manager-ip>`
- [ ] Unir worker: ejecutar el token en el nodo worker
- [ ] Deploy del stack: `docker stack deploy -c production-stack.yml inventario`
- [ ] Verificar servicios: `docker service ls`

### Fase 4 — GitHub Actions / CI/CD
- [ ] Configurar los 5 GitHub Secrets en el repositorio
- [ ] Hacer push para disparar el pipeline por primera vez
- [ ] Verificar los 3 jobs en la pestaña Actions de GitHub
- [ ] Confirmar que el escaneo Trivy pasa

### Fase 5 — UI / Frontend (pendiente solicitado)
- [ ] Agregar funcionalidad de **editar** en departamentos y asignaciones
- [ ] Agregar funcionalidad de **agregar** en departamentos y asignaciones
- [ ] Subir UI junto con el resto del proyecto (integrar con base de datos y demás)

### Fase 6 — Documentación Final
- [ ] Generar los 4 diagramas Mermaid en Draw.io o similar
- [ ] Redactar el README.md profesional con badges de Actions
- [ ] Escribir el PDF técnico (mínimo 20 páginas, según rúbrica)
- [ ] Preparar presentación final del proyecto

---

## ⚠️ Problemas Conocidos

### Error actual en Claude Code
```
API Error: Usage credits required for 1M context
turn on usage credits at claude.ai/settings/usage,
or use --model to switch to standard context
```

**Causa:** Claude Code está intentando usar el contexto extendido de 1M tokens, que requiere créditos de uso pagados.

**Solución recomendada:**
```bash
# Usar contexto estándar (200K tokens, suficiente para este proyecto)
claude --model claude-sonnet-4-20250514
```

O activar créditos en: [claude.ai/settings/usage](https://claude.ai/settings/usage)

---

## 🔑 Variables de Entorno (.env)

```env
DATABASE_URL=postgresql://usuario:password@db:5432/inventario_ti
POSTGRES_USER=usuario
POSTGRES_PASSWORD=password
POSTGRES_DB=inventario_ti
SECRET_KEY=cambia_esto_en_produccion
```

---

## 📋 Reglas y Buenas Prácticas del Proyecto

1. **Seguridad:** Nunca hardcodear credenciales — siempre `.env` o GitHub Secrets
2. **Comentarios:** Todo el código debe tener comentarios explicativos en español
3. **.gitignore:** Incluir `.env`, `*.pem`, `__pycache__/`, `.terraform/`, `*.tfstate`
4. **Zero-Downtime:** El `update_config` del Swarm garantiza réplicas disponibles durante el deploy
5. **Health Checks:** Todos los servicios deben tener healthchecks definidos
6. **Imágenes ligeras:** Usar variantes `-slim` o `-alpine`
7. **DevSecOps:** El pipeline debe fallar si Trivy encuentra vulnerabilidades HIGH o CRITICAL

---

## 📎 Archivos de Referencia

| Archivo | Ubicación | Descripción |
|---|---|---|
| `PROMPT_CLAUDE_CODE.md` | `/mnt/user-data/outputs/` | Prompt maestro para ejecutar en Claude Code |
| `handoff.md` | Este archivo | Documento de traspaso del proyecto |

---

## 🧭 Próximos Pasos Inmediatos (Orden de Ejecución)

```bash
# 1. Abrir VS Code en la carpeta del proyecto
cd ProyectoSistemas

# 2. Iniciar Claude Code con modelo estándar
claude --model claude-sonnet-4-20250514

# 3. Pegar el contenido del PROMPT_CLAUDE_CODE.md como primer mensaje
# Claude Code creará todos los archivos automáticamente

# 4. Si Claude Code se detiene, continuar con:
"Continúa con la Fase 2 — Terraform"
"Ahora genera el production-stack.yml"
"Genera los diagramas Mermaid"

# 5. Una vez generados los archivos, levantar local:
docker-compose up --build

# 6. Verificar en el navegador:
# API: http://localhost:8000/docs
# Grafana: http://localhost:3000
```

---

*Documento generado el 30 de mayo de 2026 — Antonio Samayoa / Proyecto Final SO2*
