# MLAOS Docker Quick Reference

## Essential Commands

### Start Development
```bash
cd mlaos-infra
make up            # Start API + PostgreSQL
make logs          # Watch logs
curl http://localhost:8080/docs  # Open Swagger UI
```

### Run Tests
```bash
make test          # Run pytest suite
```

### Database
```bash
make db-shell      # Connect to PostgreSQL
make db-reset      # Reset database (dev only)
```

### Production
```bash
cp .env.example .env
nano .env          # Configure
make prod-up       # Deploy
make prod-logs     # Monitor
```

### Audits
```bash
make pruning       # Identify unused features
make skew          # Detect training/serving drift
```

### Other
```bash
make shell         # Shell in API container
make help          # All commands
make clean         # Remove generated files
```

## Docker Compose Profiles

Development (default):
```bash
docker compose up           # All services
```

With tests:
```bash
docker compose --profile test up test
```

With audits:
```bash
docker compose --profile audits up     # All audit services
docker compose --profile audits up pruning  # Just pruning
docker compose --profile audits up skew-analysis  # Just skew
```

## File Locations

```
./mlaos-infra/
├── Dockerfile              # Build image
├── docker-compose.yml      # Dev config
├── docker-compose.prod.yml # Prod config
├── .env.example            # Copy to .env
├── README.md               # Start here
├── DEPLOYMENT.md           # Production guide
├── Makefile                # Commands
└── sql/                    # Database migrations
```

## Environment Setup

```bash
# Copy template
cp .env.example .env

# Essential variables
DATABASE_URL=postgresql://user:pass@postgres:5432/db
DB_PASSWORD=your_secure_password
MODEL_VERSION=AURELIA-v2.3
```

## Common Tasks

### View Logs
```bash
make logs              # API logs (dev)
make prod-logs         # API logs (prod)
docker compose logs db # Database logs
```

### Connect to Database
```bash
make db-shell
# Or manually
docker compose exec postgres psql -U mlaos -d mlaos_db
```

### Run SQL Query
```bash
docker compose exec postgres psql -U mlaos -d mlaos_db \
  -c "SELECT * FROM feature_registry;"
```

### Scale API (Production)
```bash
docker compose -f docker-compose.prod.yml up -d --scale api=5
```

### Export Database Backup
```bash
docker compose exec postgres pg_dump -U mlaos mlaos_db > backup.sql
```

### Restore Database
```bash
docker compose exec postgres psql -U mlaos mlaos_db < backup.sql
```

## Troubleshooting

### Ports in Use
```bash
# Check what's using ports 8080 and 5432
lsof -i :8080
lsof -i :5432

# Edit docker-compose.yml to use different ports
```

### Container Won't Start
```bash
# Check logs
docker compose logs api

# Verify database is ready
docker compose logs postgres
```

### Database Connection Error
```bash
# Test connection
docker compose exec api python -c \
  "import psycopg2; psycopg2.connect('$DATABASE_URL')"
```

### Clean Up
```bash
# Stop containers
docker compose down

# Remove volumes (DEV ONLY - deletes data!)
docker compose down -v

# Remove all Docker resources
docker system prune -a
```

## API Testing

### Health Check
```bash
curl http://localhost:8080/
```

### Swagger UI
```bash
open http://localhost:8080/docs  # macOS
xdg-open http://localhost:8080/docs  # Linux
start http://localhost:8080/docs  # Windows
```

### Inference Request
```bash
curl -X POST http://localhost:8080/inference \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": "inst-001",
    "features": {"resonance_raw": 0.8},
    "model_version": "AURELIA-v2.3"
  }'
```

## Documentation

- **README.md** - Overview and services
- **DEPLOYMENT.md** - Production (Docker + K8s)
- **CONTAINERIZATION_SUMMARY.md** - Full summary
- **Dockerfile** - Image configuration
- **docker-compose.yml** - Service definitions

## For Help

```bash
make help   # All commands with descriptions
cat README.md  # Full documentation
cat DEPLOYMENT.md  # Production guide
```

---

For detailed guides, see README.md and DEPLOYMENT.md in ./mlaos-infra/
