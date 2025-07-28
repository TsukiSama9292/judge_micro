# Deployment Guide

## Overview

This guide covers deployment strategies for the Judge MicroService system, including local development, production deployment, and cloud-based setups.

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ or Debian 11+ recommended)
- **Container Runtime**: Docker Engine 20.10+ and Docker Compose 2.0+
- **Python**: 3.8+ for SDK usage
- **Hardware**: Minimum 2GB RAM, 10GB storage
- **Network**: Internet access for Docker image pulls

### Docker Installation

#### Ubuntu/Debian

```bash
# Update package index
sudo apt update

# Install required packages
sudo apt install apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose --version
```

#### CentOS/RHEL

```bash
# Install required packages
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# Add Docker repository
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker Engine
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
```

## Local Development Setup

### Quick Start with Docker Compose

1. **Clone the repository:**

```bash
git clone https://github.com/TsukiSama9292/judge_micro.git
cd judge_micro
```

2. **Configure environment:**

```bash
# Copy environment template
cp .env.local.example .env.local

# Edit configuration (optional)
nano .env.local
```

3. **Start services:**

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Manual Development Setup

1. **Install Python dependencies:**

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

2. **Build Docker images:**

```bash
# Build C compiler image
docker build -t tsukisama9292/judge_micro:c ./docker/c/

# Build C++ compiler image
docker build -t tsukisama9292/judge_micro:c_plus_plus ./docker/c++/
```

3. **Run tests:**

```bash
# Run unit tests
pytest

# Run specific language tests
pytest tests/test_c.py
pytest tests/test_cpp.py
```

## Production Deployment

### Environment Configuration

Create production environment file:

```bash
# /opt/judge_micro/.env.local
CONTAINER_CPU=2.0
CONTAINER_MEM=1g
DOCKER_SSH_REMOTE=false

# Security settings
COMPOSE_PROJECT_NAME=judge_micro_prod
DOCKER_BUILDKIT=1
```

### Docker Compose Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  judge-api:
    build: 
      context: .
      dockerfile: docker/main/Dockerfile
    environment:
      - CONTAINER_CPU=2.0
      - CONTAINER_MEM=1g
      - DOCKER_SSH_REMOTE=false
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./results:/app/results
    ports:
      - "8000:8000"
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - judge-api
    restart: unless-stopped

volumes:
  redis_data:
```

### Systemd Service

Create a systemd service for automatic startup:

```bash
# /etc/systemd/system/judge-micro.service
[Unit]
Description=Judge MicroService
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/judge_micro
ExecStart=/usr/bin/docker compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable judge-micro.service
sudo systemctl start judge-micro.service
sudo systemctl status judge-micro.service
```

## Remote Docker Deployment

### SSH Key Setup

1. **Generate SSH key pair:**

```bash
# On the client machine
ssh-keygen -t rsa -b 4096 -f ~/.ssh/judge_micro_key
```

2. **Copy public key to remote server:**

```bash
ssh-copy-id -i ~/.ssh/judge_micro_key.pub user@remote-docker-server
```

3. **Configure environment:**

```bash
# .env.local
DOCKER_SSH_REMOTE=true
DOCKER_SSH_HOST=remote-docker-server.example.com
DOCKER_SSH_PORT=22
DOCKER_SSH_KEY_PATH=/home/user/.ssh/judge_micro_key
DOCKER_SSH_USER=docker_user
```

### Remote Server Setup

1. **Install Docker on remote server:**

```bash
# Follow Docker installation steps above
# Ensure user is in docker group
sudo usermod -aG docker $USER
```

2. **Configure Docker daemon:**

```bash
# /etc/docker/daemon.json
{
  "hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2376"],
  "tls": true,
  "tlscert": "/etc/docker/server-cert.pem",
  "tlskey": "/etc/docker/server-key.pem",
  "tlsverify": true,
  "tlscacert": "/etc/docker/ca.pem"
}
```

3. **Start Docker daemon:**

```bash
sudo systemctl restart docker
sudo systemctl enable docker
```

## Cloud Deployment

### AWS EC2 Deployment

#### Instance Setup

```bash
# Launch EC2 instance (Ubuntu 20.04)
# Instance type: t3.medium or larger
# Security group: Allow SSH (22), HTTP (80), HTTPS (443)

# Connect to instance
ssh -i your-key.pem ubuntu@ec2-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Clone repository
git clone https://github.com/TsukiSama9292/judge_micro.git
cd judge_micro
```

#### Application Deployment

```bash
# Configure environment
cp .env.local.example .env.local

# Edit for production
nano .env.local
# Set CONTAINER_CPU=2.0, CONTAINER_MEM=2g

# Deploy with Docker Compose
docker compose -f docker-compose.prod.yml up -d
```

#### Load Balancer Configuration

```yaml
# docker-compose.lb.yml
version: '3.8'

services:
  judge-api-1:
    extends:
      file: docker-compose.prod.yml
      service: judge-api
    ports:
      - "8001:8000"

  judge-api-2:
    extends:
      file: docker-compose.prod.yml
      service: judge-api
    ports:
      - "8002:8000"

  nginx-lb:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
    depends_on:
      - judge-api-1
      - judge-api-2
```

### Google Cloud Platform (GCP)

#### Compute Engine Setup

```bash
# Create VM instance
gcloud compute instances create judge-micro-vm \
    --zone=us-central1-a \
    --machine-type=e2-standard-2 \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=50GB \
    --tags=http-server,https-server

# SSH to instance
gcloud compute ssh judge-micro-vm --zone=us-central1-a
```

#### Container Registry Deployment

```bash
# Build and push images
docker build -t gcr.io/PROJECT_ID/judge-micro-c ./docker/c/
docker build -t gcr.io/PROJECT_ID/judge-micro-cpp ./docker/c++/

docker push gcr.io/PROJECT_ID/judge-micro-c
docker push gcr.io/PROJECT_ID/judge-micro-cpp
```

### Kubernetes Deployment

#### Deployment Configuration

```yaml
# k8s/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: judge-micro
  labels:
    app: judge-micro
spec:
  replicas: 3
  selector:
    matchLabels:
      app: judge-micro
  template:
    metadata:
      labels:
        app: judge-micro
    spec:
      containers:
      - name: judge-api
        image: judge-micro:latest
        ports:
        - containerPort: 8000
        env:
        - name: CONTAINER_CPU
          value: "1.0"
        - name: CONTAINER_MEM
          value: "512m"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        volumeMounts:
        - name: docker-sock
          mountPath: /var/run/docker.sock
      volumes:
      - name: docker-sock
        hostPath:
          path: /var/run/docker.sock
---
apiVersion: v1
kind: Service
metadata:
  name: judge-micro-service
spec:
  selector:
    app: judge-micro
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

#### Apply Configuration

```bash
# Apply deployment
kubectl apply -f k8s/deployment.yml

# Check status
kubectl get pods
kubectl get services

# View logs
kubectl logs -l app=judge-micro
```

## Security Considerations

### Container Security

1. **Run containers as non-root:**

```dockerfile
# In Dockerfile
USER 1000:1000
```

2. **Use security profiles:**

```yaml
# docker-compose.yml
services:
  judge-api:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
```

3. **Network isolation:**

```yaml
networks:
  judge-network:
    driver: bridge
    internal: true
```

### SSH Security

1. **Key-based authentication only:**

```bash
# /etc/ssh/sshd_config
PasswordAuthentication no
PubkeyAuthentication yes
```

2. **Restrict SSH access:**

```bash
# Allow only specific users
AllowUsers docker_user

# Limit connection attempts
MaxAuthTries 3
```

### Firewall Configuration

```bash
# UFW firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

## Monitoring and Logging

### Application Monitoring

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

### Log Management

```bash
# Configure Docker logging
# /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### Health Checks

```python
# health_check.py
import requests
import sys

def check_health():
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("Service is healthy")
            return 0
        else:
            print(f"Service unhealthy: {response.status_code}")
            return 1
    except Exception as e:
        print(f"Health check failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(check_health())
```

## Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application data
docker compose exec redis redis-cli BGSAVE
docker cp judge_micro_redis_1:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz .env.local docker-compose.yml

# Clean old backups (keep 7 days)
find $BACKUP_DIR -name "*.rdb" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### Disaster Recovery

```bash
#!/bin/bash
# restore.sh
BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Stop services
docker compose down

# Restore configuration
tar -xzf $BACKUP_FILE

# Start services
docker compose up -d

echo "Recovery completed"
```

## Performance Optimization

### Resource Tuning

```bash
# System-level optimizations
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
echo 'vm.max_map_count = 262144' >> /etc/sysctl.conf
sysctl -p
```

### Container Optimization

```yaml
# Optimized configuration
services:
  judge-api:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '1.0'
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
```

### Scaling Strategies

1. **Horizontal Scaling:**

```bash
# Scale service replicas
docker compose up -d --scale judge-api=3
```

2. **Load Distribution:**

```nginx
# nginx.conf
upstream judge_backend {
    least_conn;
    server judge-api-1:8000;
    server judge-api-2:8000;
    server judge-api-3:8000;
}
```

## Troubleshooting

### Common Issues

1. **Docker Socket Permission:**

```bash
sudo chown root:docker /var/run/docker.sock
sudo chmod 660 /var/run/docker.sock
```

2. **Memory Issues:**

```bash
# Increase Docker memory limits
docker system prune -f
docker container prune -f
docker image prune -f
```

3. **Network Connectivity:**

```bash
# Test Docker network
docker network ls
docker network inspect bridge
```

### Debug Mode

```bash
# Enable debug logging
export DOCKER_DEBUG=1
export PYTHONPATH=/opt/judge_micro/src

# Run with verbose output
python -m judge_micro.services.efficient --debug
```

For detailed API usage, see the [API Documentation](api.md).  
For configuration options, see the [Configuration Guide](configuration.md).
