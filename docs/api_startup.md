# Judge Micro API Startup Guide

## ✅ Status: Ready to Use

Both development and production modes are working perfectly without warnings!

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Using pip
pip install -e .

# Or using Makefile
make install
```

### 2. Start Service

#### Development Mode (Recommended for development)
```bash
# Using Python script
python3 main.py dev

# Using Makefile
make dev

# Custom port
python3 main.py dev --port 8080
PORT=8080 make dev
```

**Features:**
- ✅ Auto-reload on code changes
- ✅ API documentation at `/docs` and `/redoc`
- ✅ Detailed logging for debugging
- ✅ Single process for easy development

#### Production Mode (Recommended for production)
```bash
# Using Python script
python3 main.py prod

# Using Makefile
make prod

# Custom workers and port
python3 main.py prod --workers 4 --port 8080
WORKERS=4 PORT=8080 make prod
```

**Features:**
- ✅ Multiple workers for high performance (default: 16)
- ✅ Production-optimized logging
- ✅ No API documentation exposed (security)
- ✅ Process management via Gunicorn
- ✅ Automatic worker restart on failure

## 📊 Mode Comparison

| Mode | Purpose | Workers | Docs | Performance | Use Case |
|------|---------|---------|------|-------------|----------|
| **dev** | Development | 1 | ✅ Available | Medium | Code development, testing |
| **prod** | Production | 16 (configurable) | ❌ Hidden | High | Live deployment |

## 🔧 Configuration

All Gunicorn settings are now integrated directly into `main.py` for easier management. The production mode includes optimized settings for:

- **Worker Configuration**: 16 workers with Uvicorn worker class
- **Connection Settings**: 1000 worker connections with 2048 backlog
- **Timeout Settings**: 120s timeout with 30s keep-alive
- **Request Limits**: Optimized for security and performance
- **Logging**: Structured access logs with detailed format

### Environment Variables

All settings are configured in `.env` or `.env.local` files:

### Basic Configuration
```bash
# Server settings
JUDGE_HOST=0.0.0.0
JUDGE_PORT=8000
JUDGE_WORKERS=16
JUDGE_LOG_LEVEL=info

# Container resource limits
CONTAINER_CPU=1.0
CONTAINER_MEM=512m

# Timeout settings
COMPILE_TIMEOUT=10
CONTAINER_TIMEOUT=10
```

### Docker Configuration
```bash
# Local Docker (default)
DOCKER_SSH_REMOTE=false

# Remote Docker via SSH
DOCKER_SSH_REMOTE=true
DOCKER_SSH_HOST=192.168.1.100
DOCKER_SSH_USER=docker
DOCKER_SSH_KEY_PATH=~/.ssh/id_rsa
```

## 📚 API Documentation

### Development Mode
- **Swagger UI**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Production Mode
- Documentation is disabled for security
- Only OpenAPI JSON endpoint available: http://localhost:8000/openapi.json

## 🛠️ Common Commands

```bash
# Show help
python3 main.py --help

# Skip environment check (faster startup)
python3 main.py dev --no-check
python3 main.py prod --no-check

# Clean cache files
make clean

# Check service health
curl http://localhost:8000/health

# Stop running server
# For development: Ctrl+C
# For production: pkill -f gunicorn
```

## 🐳 Docker Deployment

You can also use Docker Compose for containerized deployment:

```bash
# Start service
docker compose up -d

# View logs
docker compose logs -f judge_micro

# Stop service
docker compose down
```

## ⚡ Performance Recommendations

### Development Environment
- Use `dev` mode for auto-reload
- Set `JUDGE_LOG_LEVEL=debug` for detailed logs
- Use lower resource limits: `CONTAINER_CPU=0.5`, `CONTAINER_MEM=256m`

### Production Environment
- Use `prod` mode with multiple workers
- Set worker count to 2-4 times CPU core count
- Increase resource limits based on load
- Use reverse proxy (nginx) for SSL and load balancing
- Monitor resource usage and adjust accordingly

### Example Production Setup
```bash
# High-performance production config
export JUDGE_WORKERS=8
export CONTAINER_CPU=2.0
export CONTAINER_MEM=1g
export JUDGE_LOG_LEVEL=warning

python3 main.py prod
```

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Use different port
   python3 main.py dev --port 8080
   ```

2. **Docker not available**
   ```bash
   # Check Docker status
   docker info
   
   # Skip Docker check for testing
   python3 main.py dev --no-check
   ```

3. **Permission denied**
   ```bash
   # Make sure script is executable
   chmod +x main.py
   ```

4. **Module not found**
   ```bash
   # Install in development mode
   pip install -e .
   ```

## 🎯 Next Steps

- Configure your environment variables in `.env.local`
- Test the API endpoints using the `/docs` interface in dev mode
- Set up reverse proxy for production deployment
- Configure monitoring and logging for production use
