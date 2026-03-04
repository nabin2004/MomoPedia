# 🚀 Deployment Guide

**Production Deployment for MomoPedia**

---

## Overview

This guide covers deploying MomoPedia in production environments. The system is designed for scalability, reliability, and maintainability with support for multiple deployment strategies.

## Architecture Overview

```mermaid
graph TB
    subgraph "User Layer"
        Web[Web Interface]
        API[REST API]
        CLI[CLI Tool]
    end
    
    subgraph "Application Layer"
        LB[Load Balancer]
        App1[App Instance 1]
        App2[App Instance 2]
        App3[App Instance N]
    end
    
    subgraph "AI Layer"
        Author[Author Agent Pool]
        Reviewer[Reviewer Agent Pool]
        Chair[Editorial Chair]
    end
    
    subgraph "Data Layer"
        Redis[(Redis Cache)]
        DB[(PostgreSQL)]
        S3[(Article Storage)]
    end
    
    subgraph "Monitoring"
        Logs[Centralized Logging]
        Metrics[Prometheus/Grafana]
        Health[Health Checks]
    end
    
    Web --> LB
    API --> LB
    CLI --> LB
    LB --> App1
    LB --> App2
    LB --> App3
    App1 --> Author
    App2 --> Reviewer
    App3 --> Chair
    App1 --> Redis
    App2 --> DB
    App3 --> S3
    App1 --> Logs
    App2 --> Metrics
    App3 --> Health
```

## Quick Deployment Options

### 1. Docker Compose (Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  momopedia:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - DATABASE_URL=postgresql://postgres:password@db:5432/momopedia
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./reports:/app/reports
      - ./logs:/app/logs

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=momopedia
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - momopedia

volumes:
  postgres_data:
  redis_data:
```

**Deploy with:**
```bash
# Clone and configure
git clone https://github.com/nabin/MomoPedia.git
cd MomoPedia
cp .env.example .env
# Edit .env with your API keys

# Deploy
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f momopedia
```

### 2. Heroku Deployment

```bash
# Install Heroku CLI and login
heroku create your-momopedia-app

# Set environment variables
heroku config:set OPENROUTER_API_KEY=your_key
heroku config:set TAVILY_API_KEY=your_key
heroku config:set DATABASE_URL=postgresql://...

# Add Heroku addons
heroku addons:create heroku-postgresql:standard-0
heroku addons:create heroku-redis:premium-0

# Deploy
git push heroku main

# Scale workers
heroku ps:scale web=2 worker=1
```

**Procfile:**
```
web: uvicorn momopedia.api:app --host 0.0.0.0 --port $PORT
worker: python -m momopedia.workers.queue_processor
```

### 3. Kubernetes (Production)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: momopedia
  labels:
    app: momopedia
spec:
  replicas: 3
  selector:
    matchLabels:
      app: momopedia
  template:
    metadata:
      labels:
        app: momopedia
    spec:
      containers:
      - name: momopedia
        image: momopedia/momopedia:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: momopedia-secrets
              key: openrouter-api-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: momopedia-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: momopedia-service
spec:
  selector:
    app: momopedia
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

**Deploy to Kubernetes:**
```bash
# Create secrets
kubectl create secret generic momopedia-secrets \
  --from-literal=openrouter-api-key="your_key" \
  --from-literal=database-url="postgresql://..."

# Deploy application
kubectl apply -f k8s/

# Check deployment
kubectl get pods
kubectl get services
kubectl logs -f deployment/momopedia
```

## Environment Configuration

### Development Environment
```env
# .env.development
DEBUG=true
LOG_LEVEL=DEBUG
ENVIRONMENT=development
DATABASE_URL=sqlite:///./dev.db
REDIS_URL=redis://localhost:6379
OPENROUTER_API_KEY=your_dev_key
TAVILY_API_KEY=your_dev_key
MAX_WORKERS=2
ENABLE_MONITORING=false
```

### Staging Environment
```env
# .env.staging
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=staging
DATABASE_URL=postgresql://user:pass@staging-db:5432/momopedia
REDIS_URL=redis://staging-redis:6379
OPENROUTER_API_KEY=your_staging_key
TAVILY_API_KEY=your_staging_key
MAX_WORKERS=4
ENABLE_MONITORING=true
MONITORING_ENDPOINT=http://staging-prometheus:9090
```

### Production Environment
```env
# .env.production
DEBUG=false
LOG_LEVEL=WARNING
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@prod-db:5432/momopedia
REDIS_URL=redis://prod-redis:6379
OPENROUTER_API_KEY=your_prod_key
TAVILY_API_KEY=your_prod_key
MAX_WORKERS=8
ENABLE_MONITORING=true
MONITORING_ENDPOINT=http://prometheus:9090
SENTRY_DSN=https://your-sentry-dsn
RATE_LIMIT_ENABLED=true
CORS_ORIGINS=["https://momopedia.org"]
```

## Database Setup

### PostgreSQL Production Setup

```sql
-- Create database and user
CREATE DATABASE momopedia;
CREATE USER momopedia_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE momopedia TO momopedia_user;

-- Connect to momopedia database
\c momopedia

-- Create tables
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    quality_score FLOAT NOT NULL,
    region VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'active'
);

CREATE TABLE generation_logs (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id),
    agent_type VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE quality_metrics (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id),
    cultural_authenticity FLOAT,
    factual_accuracy FLOAT,
    writing_quality FLOAT,
    completeness FLOAT,
    citation_quality FLOAT,
    overall_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_articles_region ON articles(region);
CREATE INDEX idx_articles_quality_score ON articles(quality_score);
CREATE INDEX idx_articles_created_at ON articles(created_at);
CREATE INDEX idx_generation_logs_article_id ON generation_logs(article_id);
```

### Database Migration

```python
# migrations/001_initial_schema.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=False),
        sa.Column('region', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('articles')
```

Run migrations:
```bash
# Initialize alembic
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

## Load Balancing & Nginx

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/momopedia
upstream momopedia_backend {
    least_conn;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name momopedia.org www.momopedia.org;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name momopedia.org www.momopedia.org;
    
    ssl_certificate /etc/ssl/certs/momopedia.crt;
    ssl_certificate_key /etc/ssl/private/momopedia.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # API endpoints
    location /api/ {
        proxy_pass http://momopedia_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for AI processing
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    # Static files
    location /static/ {
        alias /var/www/momopedia/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Health checks
    location /health {
        proxy_pass http://momopedia_backend;
        access_log off;
    }
    
    # Rate limiting
    location /api/generate {
        limit_req zone=api_generate burst=5 nodelay;
        proxy_pass http://momopedia_backend;
    }
}

# Rate limiting zones
http {
    limit_req_zone $binary_remote_addr zone=api_generate:10m rate=10r/m;
}
```

## Monitoring & Observability

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'momopedia'
    static_configs:
      - targets: ['momopedia:8000']
    metrics_path: /metrics
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
      
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "MomoPedia AI System",
    "panels": [
      {
        "title": "Article Generation Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(momopedia_articles_generated_total[5m])",
            "legend": "Articles/sec"
          }
        ]
      },
      {
        "title": "Quality Score Distribution",
        "type": "histogram",
        "targets": [
          {
            "expr": "momopedia_quality_score_bucket",
            "legend": "Quality Scores"
          }
        ]
      },
      {
        "title": "Agent Performance",
        "type": "table",
        "targets": [
          {
            "expr": "momopedia_agent_processing_time",
            "legend": "{{agent_type}}"
          }
        ]
      }
    ]
  }
}
```

### Logging Configuration

```python
# logging_config.py
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'detailed'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/momopedia/app.log',
            'level': 'DEBUG',
            'formatter': 'json'
        },
        'sentry': {
            'class': 'sentry_sdk.integrations.logging.SentryHandler',
            'level': 'ERROR'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file', 'sentry']
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

## Security Configuration

### SSL/TLS Setup

```bash
# Generate SSL certificate with Let's Encrypt
sudo certbot --nginx -d momopedia.org -d www.momopedia.org

# Auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### API Security

```python
# security.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import jwt

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://momopedia.org"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Security dependencies
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.post("/api/articles/generate")
@limiter.limit("10/minute")
async def generate_article(request: Request, token=Depends(verify_token)):
    # Implementation
    pass
```

## Backup & Recovery

### Database Backups

```bash
# Daily backup script
#!/bin/bash
# backup_db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/momopedia"
DB_NAME="momopedia"

# Create backup
pg_dump -h localhost -U momopedia_user -d $DB_NAME > "$BACKUP_DIR/momopedia_$DATE.sql"

# Compress
gzip "$BACKUP_DIR/momopedia_$DATE.sql"

# Remove backups older than 30 days
find $BACKUP_DIR -name "momopedia_*.sql.gz" -mtime +30 -delete

# Upload to S3
aws s3 cp "$BACKUP_DIR/momopedia_$DATE.sql.gz" s3://momopedia-backups/database/
```

### Application State Backup

```bash
# backup_app.sh
#!/bin/bash

# Backup configuration
tar -czf /backups/config_$(date +%Y%m%d).tar.gz /etc/momopedia/

# Backup logs (last 7 days)
find /var/log/momopedia -name "*.log" -mtime -7 -exec tar -rf /backups/logs_$(date +%Y%m%d).tar {} \;

# Backup generated reports
tar -czf /backups/reports_$(date +%Y%m%d).tar.gz /var/lib/momopedia/reports/
```

## Performance Optimization

### Redis Caching

```python
# cache.py
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            
            return result
        return wrapper
    return decorator

@cache_result(expiration=1800)  # 30 minutes
def generate_article(topic: str, style: str):
    # Expensive AI generation
    pass
```

### Database Optimization

```sql
-- Performance indexes
CREATE INDEX CONCURRENTLY idx_articles_region_quality 
ON articles(region, quality_score DESC);

CREATE INDEX CONCURRENTLY idx_generation_logs_created_at 
ON generation_logs(created_at DESC);

-- Partitioning for large tables
CREATE TABLE generation_logs_2024 PARTITION OF generation_logs
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy MomoPedia

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        pip install -e .[dev]
        
    - name: Run tests
      run: |
        pytest tests/ --cov=momopedia --cov-report=xml
        
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t momopedia:${{ github.sha }} .
        
    - name: Push to registry
      run: |
        docker tag momopedia:${{ github.sha }} ${{ secrets.DOCKER_REGISTRY }}/momopedia:latest
        docker push ${{ secrets.DOCKER_REGISTRY }}/momopedia:latest
        
    - name: Deploy to production
      run: |
        kubectl set image deployment/momopedia momopedia=${{ secrets.DOCKER_REGISTRY }}/momopedia:latest
```

## Health Checks & Monitoring

### Health Check Endpoints

```python
# health.py
from fastapi import APIRouter, status
from pydantic import BaseModel
import asyncio

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    checks: dict
    
@router.get("/health", response_model=HealthResponse)
async def health_check():
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "ai_agents": await check_ai_agents(),
        "external_apis": await check_external_apis()
    }
    
    status_code = "healthy" if all(checks.values()) else "unhealthy"
    
    return HealthResponse(status=status_code, checks=checks)

async def check_database():
    try:
        # Test database connection
        await db.execute("SELECT 1")
        return True
    except Exception:
        return False
```

### Alerting Rules

```yaml
# alerting_rules.yml
groups:
- name: momopedia_alerts
  rules:
  - alert: HighErrorRate
    expr: rate(momopedia_errors_total[5m]) > 0.1
    for: 5m
    annotations:
      summary: "High error rate detected"
      
  - alert: LowQualityScores
    expr: avg(momopedia_quality_score) < 0.7
    for: 10m
    annotations:
      summary: "Article quality scores dropping"
      
  - alert: DatabaseConnectionsHigh
    expr: pg_stat_activity_count > 80
    for: 2m
    annotations:
      summary: "Database connection pool exhausted"
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   ```bash
   # Check memory usage
   docker stats momopedia
   
   # Adjust container limits
   docker update --memory=2g momopedia
   ```

2. **Slow Article Generation**
   ```bash
   # Check AI agent performance
   curl http://localhost:8000/metrics | grep agent_processing_time
   
   # Scale up agent pools
   kubectl scale deployment momopedia --replicas=5
   ```

3. **Database Connection Issues**
   ```bash
   # Check connection pool
   psql -c "SELECT count(*) FROM pg_stat_activity;"
   
   # Adjust pool settings
   export DATABASE_POOL_SIZE=20
   ```

### Log Analysis

```bash
# Search for errors in logs
grep -i "error" /var/log/momopedia/app.log | tail -50

# Monitor real-time logs
tail -f /var/log/momopedia/app.log | grep -E "(ERROR|CRITICAL)"

# Analyze performance
awk '/agent_processing_time/ {sum+=$NF; count++} END {print "Avg:", sum/count}' logs/performance.log
```

---

**Ready for Production! 🚀**

*Need help? Check our [Support Resources](../README.md#support--contact) or join the [Developer Community](https://discord.gg/momopedia)*