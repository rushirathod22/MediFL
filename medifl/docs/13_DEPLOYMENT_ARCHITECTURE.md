<div align="center">

# 🚀 MediFL — Deployment Architecture Document

### 🏥 Kubernetes, Docker & Cloud Infrastructure

| **Document ID** | `MEDIFL-DEPLOY-013` | **Version** | `v1.0.0` | **Status** | ✅ Approved |
|:---:|:---:|:---:|:---:|:---:|:---:|

---

</div>

## 1. Kubernetes Cluster Topology

```mermaid
graph TD
    subgraph "☁️ AWS Cloud Infrastructure"
        direction TB
        
        subgraph Ingress ["🌐 Ingress Layer"]
            R53["🌍 Route 53 DNS<br/><i>*.medifl.health</i>"]
            NLB["⚖️ Network Load Balancer<br/><i>TLS passthrough<br/>Cross-AZ distribution</i>"]
        end

        subgraph AZ_A ["🏢 AZ-A (us-east-1a)"]
            W1["☸️ <b>Worker Node 1</b><br/><i>c6i.4xlarge (16 vCPU, 32GB)</i>"]
            
            subgraph W1_Pods ["Pods"]
                P1["⚙️ API Pod x1"]
                P2["🧮 Aggregator Pod x1"]
                P3["📊 WebSocket Pod x1"]
            end
        end

        subgraph AZ_B ["🏢 AZ-B (us-east-1b)"]
            W2["☸️ <b>Worker Node 2</b><br/><i>c6i.4xlarge (16 vCPU, 32GB)</i>"]
            
            subgraph W2_Pods ["Pods"]
                P4["⚙️ API Pod x1"]
                P5["🧮 Aggregator Pod x1"]
            end
        end

        subgraph Managed ["🔧 AWS Managed Services"]
            RDS["🐘 <b>RDS PostgreSQL 15</b><br/><i>Multi-AZ, db.r6g.xlarge<br/>100 GB gp3 SSD</i>"]
            EC["⚡ <b>ElastiCache Redis</b><br/><i>cache.r6g.large<br/>Cluster mode enabled</i>"]
            S3["📦 <b>S3 Encrypted Bucket</b><br/><i>SSE-KMS (AES-256)<br/>Versioning enabled</i>"]
            HSM["🔐 <b>CloudHSM</b><br/><i>FIPS 140-2 Level 3</i>"]
        end
    end

    R53 --> NLB
    NLB --> P1 & P4
    P1 & P4 --> RDS & EC
    P2 & P5 --> S3 & HSM

    style AZ_A fill:#eff6ff,stroke:#3b82f6,stroke-width:2px
    style AZ_B fill:#f0fdf4,stroke:#16a34a,stroke-width:2px
    style Managed fill:#fefce8,stroke:#eab308,stroke-width:2px
```

## 2. Docker Multi-Stage Build

```dockerfile
# ================================================================
# MediFL Aggregator Service — Multi-Stage Dockerfile
# ================================================================

# Stage 1: Build & Dependency Resolution
FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Minimal Production Runtime
FROM python:3.11-slim AS final
WORKDIR /app

# Security: Non-root user with minimal permissions
RUN addgroup --system medifl && adduser --system --group medifl

COPY --from=builder /root/.local /home/medifl/.local
COPY --chown=medifl:medifl ./src /app/src

ENV PATH=/home/medifl/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Security: Read-only filesystem, drop capabilities
USER medifl
EXPOSE 8000 50051

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/healthz || exit 1

ENTRYPOINT ["python", "-m", "src.main"]
```

## 3. Helm Chart Values (`values.yaml`)

```yaml
global:
  environment: production
  domain: medifl.health
  imagePullSecrets: [name: medifl-registry-secret]

apiService:
  replicaCount: 3
  image:
    repository: registry.medifl.health/control-plane/api
    tag: v1.0.0
  resources:
    limits: { cpu: 2000m, memory: 4Gi }
    requests: { cpu: 500m, memory: 1Gi }
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPU: 75

aggregatorService:
  replicaCount: 2
  image:
    repository: registry.medifl.health/control-plane/aggregator
    tag: v1.0.0
  resources:
    limits: { cpu: 4000m, memory: 16Gi }
    requests: { cpu: 2000m, memory: 4Gi }

postgresql:
  enabled: true
  architecture: replication
  auth: { database: medifl_db, username: medifl_admin }
  primary:
    persistence: { size: 100Gi, storageClass: gp3 }

redis:
  architecture: replication
  master:
    persistence: { size: 20Gi }
```

---

<div align="center">

| ← [Phase 12: UI/UX](./12_UI_UX_DESIGN_GUIDE.md) | 📄 **Next** | [Phase 14: DevOps →](./14_DEVOPS_GUIDE.md) |
|:---:|:---:|:---:|

*© 2026 MediFL Platform — Confidential & Proprietary*

</div>
