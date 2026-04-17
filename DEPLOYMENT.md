# MLAOS Deployment Guide

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- PostgreSQL 15+ (for data persistence)
- 2GB+ RAM available
- Internet access for base image pulls

## Single-Host Deployment (Docker Compose)

### 1. Prepare Environment

```bash
cd mlaos-infra

# Copy and customize environment
cp .env.example .env

# Edit with production values
nano .env
```

Critical variables to set:

```env
DATABASE_URL=postgresql://mlaos:YOUR_SECURE_PASSWORD@postgres:5432/mlaos_db
DB_PASSWORD=YOUR_SECURE_PASSWORD
MODEL_VERSION=AURELIA-v2.3
ENVIRONMENT=production
```

### 2. Build and Deploy

```bash
# Build image (optional, compose will auto-build)
docker build -t mlaos-api:latest .

# Start services
docker compose -f docker-compose.prod.yml up -d

# Verify all services are running
docker compose -f docker-compose.prod.yml ps
```

### 3. Initialize Database

Database migrations run automatically via `docker-entrypoint.sh` on first start.

Verify tables exist:

```bash
docker compose exec postgres psql -U mlaos -d mlaos_db -c "\dt"
```

### 4. Verify API is Running

```bash
# Check health
curl http://localhost:8080/docs

# Test inference endpoint
curl -X POST http://localhost:8080/inference \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": "test-001",
    "features": {"resonance_raw": 0.5},
    "model_version": "AURELIA-v2.3"
  }'
```

## Kubernetes Deployment

### Generate Manifests

Create `k8s/` directory with deployment manifests:

```bash
mkdir -p k8s
```

**k8s/namespace.yaml:**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: mlaos
```

**k8s/configmap.yaml:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mlaos-config
  namespace: mlaos
data:
  MODEL_VERSION: "AURELIA-v2.3"
  PRUNING_THRESHOLD_DAYS: "30"
  LOG_LEVEL: "INFO"
```

**k8s/secret.yaml:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mlaos-db-secret
  namespace: mlaos
type: Opaque
stringData:
  DATABASE_URL: "postgresql://mlaos:YOUR_PASSWORD@postgres:5432/mlaos_db"
  DB_USER: "mlaos"
  DB_PASSWORD: "YOUR_SECURE_PASSWORD"
  DB_NAME: "mlaos_db"
```

**k8s/postgres-pvc.yaml:**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
  namespace: mlaos
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

**k8s/postgres-deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: mlaos
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        envFrom:
        - secretRef:
            name: mlaos-db-secret
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U mlaos
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: postgres-data
        persistentVolumeClaim:
          claimName: postgres-data
```

**k8s/postgres-service.yaml:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: mlaos
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  clusterIP: None  # Headless service
```

**k8s/api-deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mlaos-api
  namespace: mlaos
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: mlaos-api
  template:
    metadata:
      labels:
        app: mlaos-api
    spec:
      containers:
      - name: api
        image: mlaos-api:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
        envFrom:
        - configMapRef:
            name: mlaos-config
        - secretRef:
            name: mlaos-db-secret
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
        readinessProbe:
          httpGet:
            path: /
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
```

**k8s/api-service.yaml:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mlaos-api
  namespace: mlaos
spec:
  type: LoadBalancer
  selector:
    app: mlaos-api
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets and config
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Deploy database
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml

# Wait for postgres
kubectl wait --for=condition=ready pod -l app=postgres -n mlaos --timeout=60s

# Deploy API
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml

# Verify
kubectl get all -n mlaos
kubectl logs -n mlaos deployment/mlaos-api
```

## Scaling

### Docker Compose

Scale API service:

```bash
docker compose -f docker-compose.prod.yml up -d --scale api=5
```

Use a reverse proxy (nginx/traefik) in front for load balancing.

### Kubernetes

Update replicas:

```bash
kubectl scale deployment mlaos-api -n mlaos --replicas=5
```

## Monitoring

### Logs

```bash
# Docker Compose
docker compose -f docker-compose.prod.yml logs -f api

# Kubernetes
kubectl logs -n mlaos deployment/mlaos-api -f
kubectl logs -n mlaos deployment/mlaos-api --all-containers=true --timestamps=true
```

### Health Checks

```bash
# Docker Compose
curl http://localhost:8080/docs

# Kubernetes
kubectl get endpoints -n mlaos
kubectl describe service mlaos-api -n mlaos
```

### Database Queries

```bash
# View served features
docker compose exec postgres psql -U mlaos -d mlaos_db -c \
  "SELECT feature_name, COUNT(*) FROM serving_logs GROUP BY feature_name;"

# Check feature registry
docker compose exec postgres psql -U mlaos -d mlaos_db -c \
  "SELECT * FROM feature_registry WHERE status='ACTIVE';"
```

## Backup & Recovery

### Database Backup

```bash
docker compose exec postgres pg_dump -U mlaos mlaos_db > backup.sql
```

### Database Restore

```bash
# Stop API
docker compose -f docker-compose.prod.yml stop api

# Restore
docker compose exec postgres psql -U mlaos mlaos_db < backup.sql

# Restart
docker compose -f docker-compose.prod.yml up -d api
```

## Troubleshooting

### API Container Won't Start

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs api

# Verify database is ready
docker compose -f docker-compose.prod.yml logs postgres
```

### Database Connection Error

```bash
# Verify DATABASE_URL format
grep DATABASE_URL .env

# Test connection manually
docker compose exec api python -c \
  "import psycopg2; psycopg2.connect('$DATABASE_URL')"
```

### Out of Disk Space

```bash
# Check
docker system df

# Clean up
docker system prune -a  # WARNING: Removes all unused images/containers
```

## Security Hardening

For production:

1. ✅ Use strong passwords (set `DB_PASSWORD`)
2. ✅ Restrict database access to internal network only
3. ✅ Use environment-based secrets (not in code)
4. ✅ Enable SSL/TLS for API (use reverse proxy)
5. ✅ Regular backups (daily for production)
6. ✅ Monitor resource usage
7. ✅ Enable audit logging

Example with Traefik for HTTPS:

```yaml
# Add to docker-compose.prod.yml
traefik:
  image: traefik:latest
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
  labels:
    - traefik.enable=true
    - traefik.http.routers.mlaos.rule=Host(`api.example.com`)
    - traefik.http.routers.mlaos.entrypoints=websecure
    - traefik.http.routers.mlaos.tls.certresolver=letsencrypt
    - traefik.http.services.mlaos.loadbalancer.server.port=8080
```

## Maintenance

### Scheduled Tasks

Use cron or Kubernetes CronJob for audits:

```bash
# Pruning (weekly)
0 0 * * 0 docker compose -f docker-compose.prod.yml run pruning

# Skew analysis (weekly)
0 1 * * 0 docker compose -f docker-compose.prod.yml run skew-analysis
```

Kubernetes CronJob example:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: pruning-job
  namespace: mlaos
spec:
  schedule: "0 0 * * 0"  # Weekly
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: pruning
            image: mlaos-api:latest
            command: ["python", "audits/pruning_automation.py"]
            envFrom:
            - secretRef:
                name: mlaos-db-secret
          restartPolicy: OnFailure
```

## Support

For issues or questions, contact: kennydallmier@gmail.com
