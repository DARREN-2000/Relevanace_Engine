# 🚀 Deployment Guide — Consentinel

## Free Demo Deployment (Render Blueprint)

For the fastest no-cost demo deploy, use the included `render.yaml`.

```bash
# 1. Fork this repository
# 2. In Render: New + -> Blueprint
# 3. Select your fork (Render auto-detects render.yaml)
```

What this blueprint does:

- Deploys the backend as a single Docker web service (`plan: free`)
- Uses SQLite at `/tmp/consentinel.db` so no separate DB is needed (ephemeral)
- Generates secure `SECRET_KEY` and `JWT_SECRET_KEY` automatically
- Sets permissive CORS for fast demo setup

After deploy:

- Health check: `https://<your-service>.onrender.com/api/health`
- Swagger UI: `https://<your-service>.onrender.com/docs`

> ⚠️ Demo-only defaults: `/tmp` storage is non-persistent and CORS is wide open. For production environments, move to PostgreSQL and set `CORS_ORIGINS` to trusted domains only.

---

## Docker Compose Deployment

### Prerequisites

- Docker 24+
- Docker Compose v2+
- At least 2 GB RAM available

### Production Deployment

```bash
# 1. Clone the repository
git clone https://github.com/DARREN-2000/Consentinel.git
cd Consentinel

# 2. Configure environment
cp .env.example .env
# Edit .env — change ALL secret values for production:
#   POSTGRES_PASSWORD, SECRET_KEY, JWT_SECRET_KEY

# 3. Start the stack
make up
# or: docker compose up --build -d

# 4. Verify
curl http://localhost:8000/api/health
curl http://localhost:8000/api/ready
```

### Services Started

| Service   | Port            | Description         |
| --------- | --------------- | ------------------- |
| `backend` | 8000            | FastAPI application |
| `db`      | 5432 (internal) | PostgreSQL 16       |
| `redis`   | 6379 (internal) | Redis 7             |

### Monitoring with Docker

```bash
# View logs
make logs                         # Tail backend logs
docker compose logs -f            # All services
docker compose logs -f db         # Database only

# Service health
docker compose ps
docker compose exec backend curl localhost:8000/api/health

# Database access
make db-shell

# Redis access
make redis-cli
```

### Stopping the Stack

```bash
make down          # Stop containers (keep data)
make clean         # Stop and remove all data
```

---

## Kubernetes / Helm Deployment

### Prerequisites

- Kubernetes 1.28+
- Helm 3.12+
- kubectl configured for your cluster

### Install

```bash
# 1. Add dependency charts (PostgreSQL, Redis)
cd helm/consentinel

# 2. Create namespace
kubectl create namespace consentinel

# 3. Create secrets
kubectl create secret generic consentinel-secrets \
  --namespace consentinel \
  --from-literal=postgresql-password='your-db-password' \
  --from-literal=SECRET_KEY='your-secret-key' \
  --from-literal=JWT_SECRET_KEY='your-jwt-secret'

# 4. Install the chart
helm install consentinel ./helm/consentinel \
  --namespace consentinel \
  --values helm/consentinel/values.yaml

# 5. Verify
kubectl get pods -n consentinel
kubectl get svc -n consentinel
```

### Custom Values

Create a `values-production.yaml`:

```yaml
replicaCount: 3

image:
  repository: ghcr.io/darren-2000/consentinel/backend
  tag: v1.0.0

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: api.consentinel.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: consentinel-tls
      hosts:
        - api.consentinel.example.com

resources:
  limits:
    cpu: "1"
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
```

```bash
helm install consentinel ./helm/consentinel \
  --namespace consentinel \
  --values values-production.yaml
```

### Upgrade

```bash
helm upgrade consentinel ./helm/consentinel \
  --namespace consentinel \
  --values values-production.yaml
```

### Rollback

```bash
helm rollback consentinel 1 --namespace consentinel
```

---

## Environment Variables

### Required

| Variable         | Description                  | Example                               |
| ---------------- | ---------------------------- | ------------------------------------- |
| `DATABASE_URL`   | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY`     | Application secret key       | Random 32+ char string                |
| `JWT_SECRET_KEY` | JWT signing key              | Random 32+ char string                |

### Optional

| Variable                          | Default                     | Description                       |
| --------------------------------- | --------------------------- | --------------------------------- |
| `REDIS_URL`                       | `redis://localhost:6379/0`  | Redis connection string           |
| `BACKEND_PORT`                    | `8000`                      | API server port                   |
| `CORS_ORIGINS`                    | `["http://localhost:3000"]` | Allowed CORS origins (JSON array) |
| `DEBUG`                           | `false`                     | Enable debug mode                 |
| `CONSENTHUB_API_URL`              | _(empty)_                   | ConsentHub integration URL        |
| `CONSENTHUB_API_KEY`              | _(empty)_                   | ConsentHub API key                |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                        | JWT token expiry                  |

### Production Checklist

- [ ] Change `POSTGRES_PASSWORD` to a strong password
- [ ] Change `SECRET_KEY` to a random 32+ character string
- [ ] Change `JWT_SECRET_KEY` to a random 32+ character string
- [ ] Set `DEBUG=false`
- [ ] Configure `CORS_ORIGINS` with your actual frontend domain
- [ ] Enable TLS/HTTPS via ingress or load balancer
- [ ] Set up database backups
- [ ] Configure monitoring and alerting

---

## Scaling

### Horizontal Scaling

The backend is stateless and can be horizontally scaled:

**Docker Compose:**

```bash
docker compose up --scale backend=3 -d
```

**Kubernetes:**
The Helm chart includes an HPA (HorizontalPodAutoscaler) that automatically scales based on CPU and memory utilization.

```yaml
# values.yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
```

### Database Scaling

- **Read replicas**: Configure PostgreSQL streaming replication for read-heavy workloads
- **Connection pooling**: Use PgBouncer in front of PostgreSQL for connection management
- **Partitioning**: The `events` and `message_decisions` tables benefit from time-based partitioning

### Redis Scaling

- **Sentinel**: Use Redis Sentinel for high availability
- **Cluster**: Use Redis Cluster for horizontal sharding

---

## Monitoring

### Health Endpoints

| Endpoint          | Purpose                                      |
| ----------------- | -------------------------------------------- |
| `GET /api/health` | Liveness probe — is the process running?     |
| `GET /api/ready`  | Readiness probe — is the database connected? |

### Recommended Monitoring Stack

- **Prometheus**: Scrape application metrics
- **Grafana**: Dashboards and alerting
- **Loki**: Log aggregation
- **Jaeger/Tempo**: Distributed tracing

### Key Metrics to Monitor

| Metric                | Alert Threshold | Description                  |
| --------------------- | --------------- | ---------------------------- |
| Request latency (p99) | > 500ms         | API response time            |
| Error rate            | > 1%            | 5xx error percentage         |
| Decision throughput   | < baseline      | NBA decisions per second     |
| Suppression rate      | > 50%           | Actions suppressed vs. total |
| Database connections  | > 80% pool      | Connection pool utilization  |
| CPU utilization       | > 80%           | Pod CPU usage                |
| Memory utilization    | > 85%           | Pod memory usage             |

---

## CI/CD Pipeline

### Continuous Integration (`.github/workflows/ci.yml`)

Runs on every push and PR to `main`:

1. **Lint**: Ruff code linting
2. **Test**: pytest with coverage reporting
3. **Docker Build**: Verify Docker image builds
4. **Helm Lint**: Validate Helm chart

### Continuous Deployment (`.github/workflows/cd.yml`)

Triggered on version tags (`v*`):

1. Build Docker image
2. Push to GitHub Container Registry (GHCR)
3. Tag with version and `latest`

### Release Workflow

```bash
# Tag a release
git tag v1.0.0
git push origin v1.0.0
# CD pipeline builds and pushes automatically
```
