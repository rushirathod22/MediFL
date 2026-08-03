<div align="center">

# 🏛️ MediFL — System Architecture Document

### 🏥 C4 Model Architecture & Architecture Decision Records

| **Document ID** | **Classification** | **Version** | **Status** |
|:---:|:---:|:---:|:---:|
| `MEDIFL-ARCH-007` | 🔒 Confidential | `v1.0.0` | ✅ Approved |

| **Prepared By** | **Architectural Pattern** | **Approved By** | **Date** |
|:---:|:---:|:---:|:---:|
| Software Architecture Board | C4 Model (Simon Brown) | CTO | August 2026 |

---

</div>

## 📑 Table of Contents

- [1. Level 1: System Context Diagram](#1-level-1-system-context-diagram)
- [2. Level 2: Container Diagram](#2-level-2-container-diagram)
- [3. Level 3: Component Diagram](#3-level-3-component-diagram)
- [4. Level 4: Deployment Diagram](#4-level-4-deployment-diagram)
- [5. Architecture Decision Records (ADRs)](#5-architecture-decision-records-adrs)
- [6. Network & Communication Flow Diagram](#6-network--communication-flow-diagram)

---

## 1. Level 1: System Context Diagram

> [!NOTE]
> The **System Context** diagram (C4 Level 1) shows MediFL as a single box and its relationships with external users, systems, and environments.

```mermaid
graph TD
    subgraph "🌍 External Users & Systems"
        Researcher["👨‍🔬 <b>Clinical AI Researcher</b><br/><i>Creates FL projects,<br/>uploads models,<br/>monitors training</i>"]
        
        CISO["🛡️ <b>Hospital CISO</b><br/><i>Reviews privacy budgets,<br/>inspects audit trails,<br/>approves compliance</i>"]
        
        TrialMgr["📋 <b>Clinical Trial Manager</b><br/><i>Invites hospital partners,<br/>manages campaigns,<br/>exports reports</i>"]
    end

    subgraph "🏥 MediFL Platform"
        System["<b>MediFL</b><br/><br/>🧠 Privacy-Preserving<br/>Medical Federated Learning<br/>Platform<br/><br/><i>Orchestrates collaborative AI<br/>training across hospital networks<br/>without centralizing patient data</i>"]
    end

    subgraph "🏥 Hospital Edge Infrastructure"
        H1["🏥 <b>Hospital Alpha</b><br/><i>PACS: 50K Chest X-Rays<br/>GPU: NVIDIA T4 16GB<br/>Network: 100 Mbps</i>"]
        H2["🏥 <b>Hospital Beta</b><br/><i>EHR: 120K Patient Records<br/>GPU: NVIDIA A100 40GB<br/>Network: 1 Gbps</i>"]
        H3["🏥 <b>Hospital Gamma</b><br/><i>PACS: 30K CT Volumes<br/>GPU: NVIDIA RTX 3090<br/>Network: 50 Mbps</i>"]
    end

    subgraph "🔧 External Services"
        SSO["🔑 <b>Enterprise SSO</b><br/><i>Azure AD / Okta<br/>OIDC Provider</i>"]
        Monitor["📊 <b>Monitoring Stack</b><br/><i>Prometheus + Grafana<br/>Alertmanager</i>"]
    end

    Researcher -->|"Configures & Monitors<br/>FL Projects"| System
    CISO -->|"Reviews Compliance<br/>& Privacy Budgets"| System
    TrialMgr -->|"Manages Campaigns<br/>& Hospital Partners"| System

    System <-->|"🔒 Encrypted Gradients<br/>(gRPC / mTLS)<br/>NO raw patient data"| H1
    System <-->|"🔒 Encrypted Gradients<br/>(gRPC / mTLS)<br/>NO raw patient data"| H2
    System <-->|"🔒 Encrypted Gradients<br/>(gRPC / mTLS)<br/>NO raw patient data"| H3

    System <-->|"OAuth2/OIDC"| SSO
    System -->|"Metrics Export"| Monitor

    style System fill:#6366f1,color:#fff,stroke:#4f46e5,stroke-width:3px
    style H1 fill:#10b981,color:#fff
    style H2 fill:#10b981,color:#fff
    style H3 fill:#10b981,color:#fff
```

---

## 2. Level 2: Container Diagram

> [!NOTE]
> The **Container Diagram** (C4 Level 2) zooms into MediFL and shows the major deployable containers (Docker/K8s pods) and their responsibilities.

```mermaid
graph TB
    subgraph "🖥️ Frontend Container"
        Web["🌐 <b>React SPA Portal</b><br/><i>Container: nginx:alpine</i><br/><i>Port: 3000</i><br/><br/>📊 Real-time telemetry charts<br/>📋 Project & round management<br/>🔍 Audit trail inspector<br/>📈 Privacy budget gauge"]
    end

    subgraph "☁️ MediFL Control Plane Containers"
        direction TB
        
        GW["🚪 <b>Envoy Gateway</b><br/><i>Container: envoyproxy/envoy</i><br/><i>Ports: 443, 8443, 50051</i><br/><br/>🔐 TLS 1.3 termination<br/>🔑 mTLS client cert validation<br/>⚡ Rate limiting (100 req/s)<br/>🔄 Load balancing (round-robin)"]
        
        API["⚙️ <b>FastAPI Backend Core</b><br/><i>Container: python:3.11-slim</i><br/><i>Port: 8000</i><br/><br/>📡 REST API endpoints<br/>🧠 Round state machine<br/>👥 User & node management<br/>📋 Audit logging"]
        
        WSvc["📊 <b>WebSocket Telemetry</b><br/><i>Container: python:3.11-slim</i><br/><i>Port: 8001</i><br/><br/>📈 Live metric broadcasting<br/>💓 Node heartbeat streaming<br/>🔔 Alert notifications"]
        
        Agg["🧮 <b>Aggregation Engine</b><br/><i>Container: python:3.11 + CUDA</i><br/><i>Port: 50051 (gRPC)</i><br/><br/>🔢 FedAvg / FedProx compute<br/>🎲 DP noise injection<br/>🔐 HE ciphertext processing<br/>📦 Checkpoint signing"]
    end

    subgraph "💾 Data Containers"
        direction LR
        DB["🐘 <b>PostgreSQL 15</b><br/><i>Container: postgres:15-alpine</i><br/><i>Port: 5432</i><br/><br/>📋 Projects, Rounds, Nodes<br/>📝 Audit Logs, Users<br/>🔄 Streaming Replication"]
        
        Redis["⚡ <b>Redis 7</b><br/><i>Container: redis:7-alpine</i><br/><i>Port: 6379</i><br/><br/>💓 Node heartbeats<br/>📡 Pub/Sub telemetry<br/>🔑 Session cache"]
        
        MinIO["📦 <b>MinIO Object Storage</b><br/><i>Container: minio/minio</i><br/><i>Port: 9000</i><br/><br/>🧠 Encrypted model weights<br/>📊 Checkpoint versioning<br/>🔒 AES-256 server-side"]
    end

    subgraph "🏥 Edge Containers"
        Edge["🐳 <b>Hospital Edge Agent</b><br/><i>Container: medifl/edge-agent</i><br/><i>Ports: None (outbound only)</i><br/><br/>🧠 PyTorch local training<br/>✂️ L2 clipping + DP noise<br/>📡 gRPC upload streaming<br/>💓 Heartbeat keepalive"]
    end

    Web <-->|"HTTPS/REST"| GW
    Web <-->|"WSS"| WSvc
    
    GW --> API
    GW --> Agg
    API --> DB
    API --> Redis
    API --> MinIO
    Agg --> MinIO
    WSvc --> Redis
    
    Edge <-->|"🔒 gRPC/mTLS<br/>(Outbound Only)"| GW

    style Web fill:#6366f1,color:#fff
    style GW fill:#ef4444,color:#fff
    style API fill:#0ea5e9,color:#fff
    style WSvc fill:#10b981,color:#fff
    style Agg fill:#8b5cf6,color:#fff
    style DB fill:#334155,color:#fff
    style Redis fill:#334155,color:#fff
    style MinIO fill:#334155,color:#fff
    style Edge fill:#16a34a,color:#fff
```

---

## 3. Level 3: Component Diagram

> [!NOTE]
> The **Component Diagram** (C4 Level 3) zooms into the **FastAPI Backend Core** container to reveal its internal components.

```mermaid
graph TB
    subgraph "⚙️ FastAPI Backend Core — Internal Components"
        direction TB
        
        subgraph Routes ["📡 API Route Layer"]
            R1["🔗 <b>/api/v1/auth/*</b><br/><i>Login, Token Refresh,<br/>User Registration</i>"]
            R2["🔗 <b>/api/v1/projects/*</b><br/><i>CRUD, Hyperparameters,<br/>Model Upload</i>"]
            R3["🔗 <b>/api/v1/rounds/*</b><br/><i>Start Round, Status,<br/>Metrics Query</i>"]
            R4["🔗 <b>/api/v1/nodes/*</b><br/><i>Registration, Health,<br/>Certificate Management</i>"]
            R5["🔗 <b>/api/v1/audit/*</b><br/><i>Lineage Query,<br/>Compliance Export</i>"]
        end

        subgraph Services ["🧠 Business Service Layer"]
            S1["🔑 <b>AuthService</b><br/><i>JWT validation<br/>RBAC enforcement<br/>Session management</i>"]
            S2["📋 <b>ProjectService</b><br/><i>Project lifecycle<br/>Hyperparameter config<br/>Model file management</i>"]
            S3["🔄 <b>RoundController</b><br/><i>State machine engine<br/>Node scheduling<br/>Straggler timeout</i>"]
            S4["🏥 <b>NodeRegistry</b><br/><i>X.509 cert validation<br/>Health check tracking<br/>Capacity reporting</i>"]
            S5["📝 <b>AuditService</b><br/><i>SHA-256 event signing<br/>Immutable log append<br/>Compliance report gen</i>"]
        end

        subgraph DAL ["💾 Data Access Layer (DAO Pattern)"]
            D1["<b>UserRepository</b>"]
            D2["<b>ProjectRepository</b>"]
            D3["<b>RoundRepository</b>"]
            D4["<b>NodeRepository</b>"]
            D5["<b>AuditRepository</b>"]
        end

        R1 --> S1
        R2 --> S2
        R3 --> S3
        R4 --> S4
        R5 --> S5

        S1 --> D1
        S2 --> D2
        S3 --> D3
        S4 --> D4
        S5 --> D5
    end

    style Routes fill:#eff6ff,stroke:#3b82f6,stroke-width:2px
    style Services fill:#f0fdf4,stroke:#16a34a,stroke-width:2px
    style DAL fill:#fefce8,stroke:#eab308,stroke-width:2px
```

---

## 4. Level 4: Deployment Diagram

```mermaid
graph TD
    subgraph "☁️ AWS Cloud Infrastructure"
        direction TB
        
        subgraph AZ1 ["🏢 Availability Zone A"]
            LB["⚖️ <b>Network Load Balancer</b><br/><i>TLS passthrough<br/>Health check: /healthz</i>"]
            
            subgraph K8s1 ["☸️ EKS Worker Node 1"]
                Pod1["⚙️ API Pod (x1)"]
                Pod2["🧮 Aggregator Pod (x1)"]
            end
        end

        subgraph AZ2 ["🏢 Availability Zone B"]
            subgraph K8s2 ["☸️ EKS Worker Node 2"]
                Pod3["⚙️ API Pod (x1)"]
                Pod4["📊 WebSocket Pod (x1)"]
            end
        end

        subgraph Managed ["🔧 AWS Managed Services"]
            RDS["🐘 <b>Amazon RDS</b><br/><i>PostgreSQL Multi-AZ</i>"]
            EC["⚡ <b>ElastiCache</b><br/><i>Redis Cluster</i>"]
            S3B["📦 <b>Amazon S3</b><br/><i>AES-256 Encrypted</i>"]
            HSM["🔐 <b>CloudHSM</b><br/><i>FIPS 140-2 Level 3</i>"]
        end
    end

    LB --> Pod1
    LB --> Pod3
    Pod1 & Pod3 --> RDS
    Pod1 & Pod3 --> EC
    Pod2 --> S3B
    Pod2 --> HSM

    style AZ1 fill:#eff6ff,stroke:#3b82f6,stroke-width:2px
    style AZ2 fill:#f0fdf4,stroke:#16a34a,stroke-width:2px
    style Managed fill:#fefce8,stroke:#eab308,stroke-width:2px
```

---

## 5. Architecture Decision Records (ADRs)

### ADR-001: gRPC over REST for Model Weight Exchange

| Field | Detail |
|:---|:---|
| **Status** | ✅ **Accepted** |
| **Context** | Model weight tensors are 50–500 MB binary objects. JSON/REST serialization causes 2–3x memory overhead and cannot stream. |
| **Decision** | Use **gRPC over HTTP/2** with Protocol Buffers and bidirectional streaming for all weight/gradient exchange. |
| **Consequences** | ✅ 65% payload reduction vs. JSON — ✅ Native streaming for large tensors — ⚠️ Requires protobuf schema management |

### ADR-002: Outbound-Only Connection Model

| Field | Detail |
|:---|:---|
| **Status** | ✅ **Accepted** |
| **Context** | Hospital firewalls prohibit opening inbound ports. No cloud service can initiate connections to hospital internal networks. |
| **Decision** | Edge agents initiate **outbound-only persistent mTLS gRPC connections** to the central gateway. Server sends commands via the established stream. |
| **Consequences** | ✅ Zero firewall changes at hospitals — ✅ Dramatically simplified IT approval — ⚠️ Requires keepalive heartbeat management |

### ADR-003: PostgreSQL over MongoDB for Primary Database

| Field | Detail |
|:---|:---|
| **Status** | ✅ **Accepted** |
| **Context** | Need ACID compliance for round state transitions, JSONB for flexible hyperparameter storage, and strong ecosystem for HA. |
| **Decision** | Use **PostgreSQL 15** with JSONB columns, PgBouncer connection pooling, and Patroni for HA failover. |
| **Consequences** | ✅ ACID guarantees for state machine — ✅ JSONB flexibility — ✅ Mature HA ecosystem — ⚠️ Requires schema migrations |

### ADR-004: Decorator Pattern for DP Integration

| Field | Detail |
|:---|:---|
| **Status** | ✅ **Accepted** |
| **Context** | Differential Privacy should be optional per project. Core aggregation algorithms (FedAvg, FedProx) should not be tightly coupled to DP logic. |
| **Decision** | Implement DP as a **Decorator** (`DPAggregatorDecorator`) that wraps any `BaseAggregator` implementation. |
| **Consequences** | ✅ DP enabled/disabled without modifying aggregation code — ✅ Single Responsibility Principle — ✅ Easy testing of aggregation in isolation |

---

## 6. Network & Communication Flow Diagram

```mermaid
graph LR
    subgraph "🏥 Hospital Firewall"
        Edge["🐳 Edge Agent"]
    end

    subgraph "🌐 Internet (Encrypted)"
        TLS["🔒 TLS 1.3<br/>AES-256-GCM"]
    end

    subgraph "☁️ MediFL Cloud DMZ"
        WAF["🛡️ AWS WAF<br/><i>DDoS Protection<br/>IP Allowlisting</i>"]
        NLB["⚖️ Network LB<br/><i>TLS Passthrough<br/>Health Checks</i>"]
        GW["🚪 Envoy Gateway<br/><i>mTLS Validation<br/>Certificate Pinning</i>"]
    end

    subgraph "☁️ MediFL Internal Network"
        Core["⚙️ Core Services"]
    end

    Edge -->|"1. Outbound gRPC<br/>(Client Cert + Server Cert)"| TLS
    TLS --> WAF
    WAF --> NLB
    NLB --> GW
    GW -->|"2. Validated &<br/>Authorized"| Core

    style Edge fill:#10b981,color:#fff
    style TLS fill:#6366f1,color:#fff
    style WAF fill:#ef4444,color:#fff
    style GW fill:#f59e0b,color:#fff
    style Core fill:#0ea5e9,color:#fff
```

---

<div align="center">

| ← [Phase 6: LLD](./06_LLD.md) | 📄 **Next Document** | [Phase 8: AI Architecture →](./08_AI_ARCHITECTURE.md) |
|:---:|:---:|:---:|

---

*© 2026 MediFL Platform — Confidential & Proprietary*

</div>
