# Judge Micro API Makefile
.PHONY: help dev prod install clean docs

# Default target
help:
	@echo "Judge Micro API Management Tool"
	@echo ""
	@echo "Available commands:"
	@echo "  dev      Start development server (Uvicorn with reload)"
	@echo "  prod     Start production server (Gunicorn + Uvicorn workers)"
	@echo "  install  Install dependencies"
	@echo "  clean    Clean cache files"
	@echo "  docs     Start API documentation server"
	@echo ""
	@echo "Environment variables:"
	@echo "  PORT     Specify port (default: 8000)"
	@echo "  WORKERS  Specify worker count (prod mode only)"
	@echo ""
	@echo "Examples:"
	@echo "  make dev                    # Development mode"
	@echo "  make prod                   # Production mode"
	@echo "  PORT=8080 make dev          # Custom port"
	@echo "  WORKERS=4 make prod         # Custom worker count"

# Development mode
dev:
	@echo "🚀 Starting development server..."
	@python3 main.py dev $(if $(PORT),--port $(PORT))

# Production mode (default)
prod:
	@echo "🚀 Starting production server..."
	@python3 main.py prod $(if $(PORT),--port $(PORT)) $(if $(WORKERS),--workers $(WORKERS))

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@pip install -e .

# Clean cache
clean:
	@echo "🧹 Cleaning cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Documentation server
docs:
	@echo "📚 Starting API documentation server..."
	@echo "Visit: http://localhost:60280/docs"
	@python3 main.py dev
