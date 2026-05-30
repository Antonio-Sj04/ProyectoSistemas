# =============================================================================
# terraform/main.tf — Infraestructura AWS para el cluster Docker Swarm
# Proyecto Final SO2 — Antonio Samayoa
# Región: us-east-1 | Instancias: 2x EC2 t2.micro (capa gratuita)
#
# COMANDOS:
#   terraform init        → descarga proveedores
#   terraform plan        → previsualiza cambios
#   terraform apply       → crea la infraestructura
#   terraform destroy     → elimina todo (¡cuidado!)
# =============================================================================

# -----------------------------------------------------------------------------
# Proveedor AWS — usa credenciales de ~/.aws/credentials o variables de entorno
# Configurar con: aws configure
# -----------------------------------------------------------------------------
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# -----------------------------------------------------------------------------
# Variables de entrada — modifica terraform.tfvars para personalizar
# -----------------------------------------------------------------------------
variable "aws_region" {
  description = "Región de AWS donde se desplegará la infraestructura"
  type        = string
  default     = "us-east-1"
}

variable "proyecto" {
  description = "Nombre del proyecto (usado en tags de recursos)"
  type        = string
  default     = "inventario-ti"
}

variable "mi_ip" {
  description = "Tu IP pública para restricción del puerto SSH (ej: 190.1.2.3/32)"
  type        = string
  default     = "0.0.0.0/0"   # Cambiar a tu IP real para mayor seguridad
}

variable "key_pair_name" {
  description = "Nombre del Key Pair creado en la consola AWS para SSH"
  type        = string
  default     = "clave-inventario"
}

# -----------------------------------------------------------------------------
# DATA SOURCE: AMI de Amazon Linux 2023 (más reciente, 64-bit x86)
# Esto busca automáticamente la AMI más actualizada en la región
# -----------------------------------------------------------------------------
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# =============================================================================
# RED: VPC + Subred + Gateway + Routing
# =============================================================================

# VPC principal del proyecto
resource "aws_vpc" "principal" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true    # Permite nombres DNS dentro de la VPC
  enable_dns_support   = true

  tags = {
    Name     = "${var.proyecto}-vpc"
    Proyecto = var.proyecto
  }
}

# Internet Gateway — permite tráfico desde/hacia Internet
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.principal.id

  tags = {
    Name     = "${var.proyecto}-igw"
    Proyecto = var.proyecto
  }
}

# Subred pública donde vivirán las instancias EC2
resource "aws_subnet" "publica" {
  vpc_id                  = aws_vpc.principal.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true    # Asigna IP pública automáticamente a las EC2

  tags = {
    Name     = "${var.proyecto}-subred-publica"
    Proyecto = var.proyecto
  }
}

# Tabla de rutas: todo el tráfico externo (0.0.0.0/0) pasa por el IGW
resource "aws_route_table" "publica" {
  vpc_id = aws_vpc.principal.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name     = "${var.proyecto}-rt-publica"
    Proyecto = var.proyecto
  }
}

# Asociar la tabla de rutas con la subred pública
resource "aws_route_table_association" "publica" {
  subnet_id      = aws_subnet.publica.id
  route_table_id = aws_route_table.publica.id
}

# =============================================================================
# SEGURIDAD: Security Group — Firewall de las instancias EC2
# =============================================================================
resource "aws_security_group" "swarm_sg" {
  name        = "${var.proyecto}-sg"
  description = "Security Group para el cluster Docker Swarm"
  vpc_id      = aws_vpc.principal.id

  # SSH — solo desde tu IP (o 0.0.0.0/0 para el proyecto)
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.mi_ip]
  }

  # HTTP — acceso público al nginx balanceador
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS — para cuando agregues certificado SSL
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # API FastAPI — solo desde dentro de la VPC (nginx actúa de proxy)
  ingress {
    description = "FastAPI desde VPC"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  # Prometheus — solo desde la VPC (no exponer al exterior)
  ingress {
    description = "Prometheus desde VPC"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  # Grafana — público temporal para el proyecto (restringir en producción real)
  ingress {
    description = "Grafana publico temporal"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Docker Swarm — puerto de gestión del cluster (solo entre nodos de la VPC)
  ingress {
    description = "Docker Swarm management"
    from_port   = 2377
    to_port     = 2377
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  # Docker Swarm — comunicación entre nodos (TCP y UDP)
  ingress {
    description = "Docker Swarm node comm TCP"
    from_port   = 7946
    to_port     = 7946
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  ingress {
    description = "Docker Swarm node comm UDP"
    from_port   = 7946
    to_port     = 7946
    protocol    = "udp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  # Docker Swarm — red overlay (VXLAN, solo UDP)
  ingress {
    description = "Docker Swarm overlay UDP"
    from_port   = 4789
    to_port     = 4789
    protocol    = "udp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  # Salida: permitir todo el tráfico saliente (actualizaciones, pulls de Docker Hub, etc.)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name     = "${var.proyecto}-sg"
    Proyecto = var.proyecto
  }
}

# =============================================================================
# SCRIPT DE INICIO: instala Docker automáticamente en cada EC2 al crearla
# =============================================================================
locals {
  user_data_script = <<-EOF
    #!/bin/bash
    # Actualizar paquetes del sistema
    yum update -y

    # Instalar Docker en Amazon Linux 2023
    yum install -y docker

    # Habilitar e iniciar el servicio Docker
    systemctl enable docker
    systemctl start docker

    # Agregar el usuario ec2-user al grupo docker (evita usar sudo)
    usermod -aG docker ec2-user

    # Instalar docker compose plugin (versión moderna)
    mkdir -p /usr/local/lib/docker/cli-plugins
    curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" \
         -o /usr/local/lib/docker/cli-plugins/docker-compose
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

    # Marcar que la inicialización fue exitosa
    echo "Docker instalado correctamente en $(date)" >> /var/log/user-data.log
  EOF
}

# =============================================================================
# INSTANCIAS EC2
# =============================================================================

# EC2 Manager — nodo principal del Swarm (coordina los workers)
resource "aws_instance" "swarm_manager" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = "t2.micro"            # Capa gratuita de AWS
  subnet_id              = aws_subnet.publica.id
  vpc_security_group_ids = [aws_security_group.swarm_sg.id]
  key_name               = var.key_pair_name
  user_data              = local.user_data_script

  # Volumen raíz de 20GB (suficiente para Docker images)
  root_block_device {
    volume_size           = 20
    volume_type           = "gp3"
    delete_on_termination = true
  }

  tags = {
    Name     = "${var.proyecto}-swarm-manager"
    Rol      = "manager"
    Proyecto = var.proyecto
  }
}

# EC2 Worker — nodo secundario que ejecuta contenedores
resource "aws_instance" "swarm_worker" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.publica.id
  vpc_security_group_ids = [aws_security_group.swarm_sg.id]
  key_name               = var.key_pair_name
  user_data              = local.user_data_script

  root_block_device {
    volume_size           = 20
    volume_type           = "gp3"
    delete_on_termination = true
  }

  tags = {
    Name     = "${var.proyecto}-swarm-worker"
    Rol      = "worker"
    Proyecto = var.proyecto
  }
}

# =============================================================================
# OUTPUTS — IPs mostradas al terminar el terraform apply
# =============================================================================

output "ip_publica_manager" {
  description = "IP pública del Swarm Manager — usa esta para SSH y para el GitHub Secret EC2_HOST"
  value       = aws_instance.swarm_manager.public_ip
}

output "ip_publica_worker" {
  description = "IP pública del Swarm Worker"
  value       = aws_instance.swarm_worker.public_ip
}

output "ip_privada_manager" {
  description = "IP privada del Manager (para comunicación interna del Swarm)"
  value       = aws_instance.swarm_manager.private_ip
}

output "ip_privada_worker" {
  description = "IP privada del Worker (para el comando docker swarm join)"
  value       = aws_instance.swarm_worker.private_ip
}

output "comando_ssh_manager" {
  description = "Comando listo para conectarte por SSH al Manager"
  value       = "ssh -i ${var.key_pair_name}.pem ec2-user@${aws_instance.swarm_manager.public_ip}"
}

output "comando_ssh_worker" {
  description = "Comando listo para conectarte por SSH al Worker"
  value       = "ssh -i ${var.key_pair_name}.pem ec2-user@${aws_instance.swarm_worker.public_ip}"
}
