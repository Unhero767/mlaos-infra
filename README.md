# MLAOS ML Infrastructure - Containerized Deployment

A production-grade FastAPI ML serving platform with feature logging, training-serving skew detection, and feature lifecycle management.

## 📋 Overview

This containerized setup includes:

- **API Service**: FastAPI inference endpoint with Uvicorn
- **Database**: PostgreSQL 15 with feature registry and serving logs
- **Feature Extraction**: Shared code between training and serving (Rule #32)
- **Serving Logger**: Logs features at inference time for skew detection (Rule #29)
- **Skew Auditor**: Detects training/serving distribution drift (Rule #37)
- **Pruning Automation**: Identifies unused features for cleanup (Rule #22)

## 🚀 Quick Start

### Development

```bash
# Start all services
make up

# View logs
make logs

# Run tests
make test

# Open shell in API container
make shell
```

### Production

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with production credentials

# Start production stack
make prod-up

# View logs
make prod-logs
```

## 📁 Project Structure

```
.
├── Dockerfile                 # Multi-stage production-grade image
├── docker-compose.yml         # Development environment
├── docker-compose.prod.yml    # Production environment
├── docker-entrypoint.sh       # Database initialization script
├── .dockerignore              # Files excluded from image
├── .env.example               # Environment variable template
├── Makefile                   # CLI commands
├── requirements.txt           # Python dependencies
├── api.py                     # Main FastAPI application
├── conftest.py                # Pytest configuration
│
├── src/
│   ├── mlaos_infra/           # ML infrastructure modules
│   │   ├── api.py             # API implementation
│   │   ├── serving_logger.py  # Feature logging at serving time
│   │   ├── skew_auditor.py    # Training/serving skew detection
│   │   └── main.py            # Entry point
│   │
│   └── mlaos_features/        # Feature extraction (shared code)
│       └── feature_extractor.py
│
├── audits/                    # Analytics and audits
│   ├── pruning_automation.py  # Identify unused features
│   └── skew_analysis.py       # Weekly skew reports
│
├── sql/                       # Database migrations
│   ├── 001_feature_registry.sql
│   └── 002_serving_logs.sql
│
└── tests/                     # Test suite
    ├── test_feature_extractor.py
    ├── test_serving_logger.py
    ├── test_infrastructure.py
    └── paraconsistent_stress_test.py
```

## 🐳 Docker Commands

### Build Image

```bash
make docker-build
```

### View All Available Commands

```bash
make help
```

### Development Compose

```bash
# Start services
docker compose up

# Run tests (separate profile)
docker compose --profile test up test

# Run audits
docker compose --profile audits up pruning
docker compose --profile audits up skew-analysis

# Stop all
docker compose down
```

### Production Compose

```bash
# Start with production config
docker compose -f docker-compose.prod.yml up -d

# Scale API service (if using orchestration)
docker compose -f docker-compose.prod.yml up -d --scale api=3

# View logs
docker compose -f docker-compose.prod.yml logs -f api
```

## 📊 Services

### API Service (`mlaos-api`)

**Endpoint**: `http://localhost:8080`

```bash
curl -X POST http://localhost:8080/inference \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": "inst-001",
    "features": {"resonance_raw": 0.8, "light_intensity": 100},
    "model_version": "AURELIA-v2.3"
  }'
```

**Health Check**: `http://localhost:8080/docs` (Swagger UI)

### PostgreSQL Database

**Host**: `localhost:5432`
**User**: `mlaos`
**Password**: `mlaos_dev_password` (dev) / `${DB_PASSWORD}` (prod)
**Database**: `mlaos_db`

```bash
# Connect via shell
make db-shell

# Or manually
docker compose exec postgres psql -U mlaos -d mlaos_db
```

### Pruning Service (`mlaos-pruning`)

Identifies features unused for >30 days (configurable via `PRUNING_THRESHOLD_DAYS`)

```bash
make pruning
```

### Skew Analysis Service (`mlaos-skew-analysis`)

Detects training/serving distribution drift

```bash
make skew
```

## 🔧 Configuration

### Environment Variables

Create `.env` from template:

```bash
cp .env.example .env
```

Key variables:

```env
# Database
DATABASE_URL=postgresql://mlaos:password@postgres:5432/mlaos_db
DB_USER=mlaos
DB_PASSWORD=your_secure_password
DB_NAME=mlaos_db

# Model
MODEL_VERSION=AURELIA-v2.3

# Feature Extraction
FEATURE_CONFIG_PATH=/app/config/features.yaml

# Pruning
PRUNING_THRESHOLD_DAYS=30

# Server
PORT=8080
LOG_LEVEL=INFO
```

### Database Migrations

SQL migrations run automatically on container startup via `docker-entrypoint.sh`:

1. `sql/001_feature_registry.sql` - Feature registry schema
2. `sql/002_serving_logs.sql` - Serving logs and skew analysis view

## 🧪 Testing

```bash
# Run full test suite
make test

# View coverage report
docker compose --profile test up test

# Run specific test
docker compose exec api pytest tests/test_feature_extractor.py -v
```

## 📈 Monitoring

### Logs

```bash
# API logs
make logs

# Database logs
docker compose logs postgres

# All services
docker compose logs -f
```

### Health Checks

Services include health checks:
- API: HTTP health check every 30s
- PostgreSQL: `pg_isready` every 10s

Check status:

```bash
docker compose ps
```

## 🔒 Security Best Practices Included

✅ Non-root user (appuser, UID 1000)
✅ Multi-stage build (reduced image size)
✅ Environment-based secrets (no hardcoded credentials)
✅ Resource limits (CPU/memory in production)
✅ Health checks for orchestration
✅ Logging with rotation (10MB max)
✅ .dockerignore to exclude unnecessary files

## 📦 Image Details

- **Base**: `python:3.11-slim`
- **Size**: ~300-350MB (optimized with multi-stage build)
- **Layers**: 2 stages (build + runtime)
- **User**: `appuser` (non-root, UID 1000)

## 🚨 Troubleshooting

### Database connection fails

```bash
# Check postgres is healthy
docker compose ps

# View postgres logs
docker compose logs postgres

# Reset database
make db-reset
```

### API won't start

```bash
# Check logs
make logs

# Verify database connectivity
docker compose exec api python -c \
  "import psycopg2; psycopg2.connect('$DATABASE_URL')"
```

### Port conflicts

If port 8080 or 5432 are in use:

```yaml
# In docker-compose.yml, change ports:
services:
  api:
    ports:
      - "8888:8080"  # Changed from 8080:8080
  postgres:
    ports:
      - "5433:5432"  # Changed from 5432:5432
```

## 📚 Documentation

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Compose Reference](https://docs.docker.com/compose/reference/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 📝 License

See LICENSE file in project root.

## 👤 Author

Kenneth Dallmier (kennydallmier@gmail.com)
