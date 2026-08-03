<div align="center">

# 🏗️ MediFL — High Level Design (HLD)

### 🏥 Enterprise Medical Federated Learning Platform

| **Document ID** | **Classification** | **Version** | **Status** |
|:---:|:---:|:---:|:---:|
| `MEDIFL-HLD-005` | 🔒 Confidential | `v1.0.0` | ✅ Approved |

| **Prepared By** | **Architectural Pattern** | **Approved By** | **Date** |
|:---:|:---:|:---:|:---:|
| Principal Software Architect | Distributed Microservices + Edge Agents | VP Engineering | August 2026 |

---

</div>

## 📑 Table of Contents

- [1. System Context & Macro Architecture](#1-system-context--macro-architecture)
- [2. Microservice Decomposition](#2-microservice-decomposition)
- [3. High-Level Data Flow & Protocol Design](#3-high-level-data-flow--protocol-design)
- [4. Technology Stack Selection](#4-technology-stack-selection)
- [5. Cross-Cutting Concerns](#5-cross-cutting-concerns)

---

## 1. System Context & Macro Architecture

### 1.1 Complete System Topology

```mermaid
graph TB
    subgraph "🌐 Client Layer"
        Web["🖥️ <b>React Web Portal</b><br/><i>Dashboard, Project Mgmt,<br/>Audit Trail Viewer</i>"]
    end

    subgraph cloud ["☁️ MediFL Central Control Plane"]
        direction TB
        
        subgraph gateway ["🔐 Security & Routing Layer"]
            GW["🚪 <b>Envoy API Gateway</b><br/><i>TLS 1.3 Termination<br/>mTLS Certificate Validation<br/>Rate Limiting & WAF</i>"]
            Auth["🔑 <b>Auth Service (Keycloak)</b><br/><i>OAuth2/OIDC Provider<br/>JWT Token Issuance<br/>MFA Enforcement</i>"]
        end

        subgraph core ["⚙️ Business Logic Layer"]
            Orch["🧠 <b>FL Orchestrator Core</b><br/><i>Round State Machine<br/>Project Management<br/>Node Coordination</i>"]
            Agg["🧮 <b>Secure Aggregation Engine</b><br/><i>FedAvg / FedProx<br/>DP Noise Injection<br/>HE Decryption</i>"]
            Audit["📋 <b>Audit & Lineage Service</b><br/><i>Cryptographic Hashing<br/>Immutable Event Log<br/>Compliance Reporting</i>"]
            Tele["📊 <b>Telemetry Gateway</b><br/><i>WebSocket Broadcasting<br/>Real-time Metrics<br/>Node Health Streaming</i>"]
        end

        subgraph data ["💾 Data & Persistence Layer"]
            DB["🐘 <b>PostgreSQL 15 (HA)</b><br/><i>Primary + Read Replica<br/>PgBouncer Connection Pool</i>"]
            Cache["⚡ <b>Redis 7 Cluster</b><br/><i>Heartbeats, Session State<br/>Pub/Sub Telemetry Channel</i>"]
            S3["📦 <b>MinIO / S3</b><br/><i>AES-256 Encrypted<br/>Model Weight Checkpoints</i>"]
        end
    end

    subgraph edge ["🏥 Hospital Edge Layer (Behind Firewalls)"]
        direction LR
        NodeA["🏥 <b>Hospital Alpha</b><br/><i>Edge Agent + T4 GPU<br/>Chest X-Ray Dataset</i>"]
        NodeB["🏥 <b>Hospital Beta</b><br/><i>Edge Agent + A100 GPU<br/>Clinical EHR Data</i>"]
        NodeC["🏥 <b>Hospital Gamma</b><br/><i>Edge Agent + RTX 3090<br/>Pathology Slides</i>"]
    end

    Web <-->|"HTTPS/REST<br/>+ WSS Telemetry"| GW
    GW <--> Auth
    GW <--> Orch
    GW <--> Tele

    Orch <--> Agg
    Orch <--> Audit
    Orch <--> DB
    Orch <--> Cache
    Agg <--> S3
    Tele <--> Cache

    NodeA <-->|"🔒 gRPC / mTLS<br/>(Outbound Only)"| GW
    NodeB <-->|"🔒 gRPC / mTLS<br/>(Outbound Only)"| GW
    NodeC <-->|"🔒 gRPC / mTLS<br/>(Outbound Only)"| GW

    style cloud fill:#f8fafc,stroke:#6366f1,stroke-width:3px
    style edge fill:#f0fdf4,stroke:#16a34a,stroke-width:3px
    style gateway fill:#fef2f2,stroke:#ef4444,stroke-width:2px
    style core fill:#eff6ff,stroke:#3b82f6,stroke-width:2px
    style data fill:#fefce8,stroke:#eab308,stroke-width:2px
```

---

## 2. Microservice Decomposition

### 2.1 Service Specifications

```mermaid
graph LR
    subgraph "⚙️ MediFL Microservice Architecture"
        direction TB
        
        subgraph S1 ["🚪 API Gateway (Envoy)"]
            S1D["<b>Port:</b> 443 / 8443<br/><b>Tech:</b> Envoy Proxy v1.27<br/><b>Protocol:</b> HTTPS + gRPC<br/><b>Function:</b><br/>• TLS 1.3 termination<br/>• mTLS certificate validation<br/>• IP rate limiting (100 req/s)<br/>• WebSocket upgrade handling<br/>• Request routing & load balancing"]
        end

        subgraph S2 ["🔑 Auth Service"]
            S2D["<b>Port:</b> 8080<br/><b>Tech:</b> Keycloak 22 (OIDC)<br/><b>Protocol:</b> HTTP REST<br/><b>Function:</b><br/>• User login & SSO (Azure AD, Okta)<br/>• JWT access token issuance<br/>• MFA enforcement<br/>• X.509 cert chain validation<br/>• RBAC role management"]
        end

        subgraph S3 ["🧠 FL Orchestrator"]
            S3D["<b>Port:</b> 8000<br/><b>Tech:</b> Python 3.11 + FastAPI<br/><b>Protocol:</b> REST + Internal gRPC<br/><b>Function:</b><br/>• Project CRUD operations<br/>• Round state machine controller<br/>• Node selection & scheduling<br/>• Straggler timeout management<br/>• Convergence detection"]
        end

        subgraph S4 ["🧮 Aggregation Engine"]
            S4D["<b>Port:</b> 50051<br/><b>Tech:</b> Python + PyTorch C++<br/><b>Protocol:</b> gRPC (HTTP/2)<br/><b>Function:</b><br/>• FedAvg weighted averaging<br/>• FedProx proximal aggregation<br/>• DP Gaussian noise injection<br/>• HE ciphertext decryption<br/>• Checkpoint SHA-256 signing"]
        end

        subgraph S5 ["📊 Telemetry Gateway"]
            S5D["<b>Port:</b> 8001<br/><b>Tech:</b> FastAPI WebSockets<br/><b>Protocol:</b> WSS (JSON events)<br/><b>Function:</b><br/>• Real-time metric broadcasting<br/>• Node heartbeat visualization<br/>• Privacy budget live gauge<br/>• Training loss curve streaming"]
        end
    end

    style S1 fill:#ef4444,color:#fff
    style S2 fill:#f59e0b,color:#fff
    style S3 fill:#0ea5e9,color:#fff
    style S4 fill:#6366f1,color:#fff
    style S5 fill:#10b981,color:#fff
```

### 2.2 Edge Agent Runtime Architecture

```mermaid
graph TD
    subgraph "🐳 Hospital Edge Agent Container"
        direction TB
        
        CLI["🖥️ <b>Agent CLI & Config Loader</b><br/><i>Reads medifl-config.json<br/>Validates mTLS certificates</i>"]
        
        Conn["📡 <b>gRPC Connection Manager</b><br/><i>Outbound mTLS to Gateway<br/>Auto-reconnect (exp backoff)<br/>Heartbeat keepalive stream</i>"]
        
        Data["💾 <b>Data Connector Module</b><br/><i>DICOM PACS reader<br/>CSV/Parquet EHR loader<br/>NIfTI volume processor<br/>PyTorch DataLoader wrapper</i>"]
        
        Train["🧠 <b>Local Training Engine</b><br/><i>PyTorch 2.x runtime<br/>CUDA GPU acceleration<br/>Mixed precision (FP16)<br/>Local SGD/AdamW optimizer</i>"]
        
        Privacy["🔐 <b>Privacy Module</b><br/><i>L2 gradient clipping<br/>DP-SGD noise injection<br/>Opacus integration<br/>Local ε tracking</i>"]
        
        Upload["📤 <b>Secure Upload Handler</b><br/><i>Tensor serialization<br/>Chunk streaming (gRPC)<br/>SHA-256 integrity hash<br/>Optional HE encryption</i>"]
        
        CLI --> Conn
        Conn --> Data
        Data --> Train
        Train --> Privacy
        Privacy --> Upload
        Upload --> Conn
    end

    style CLI fill:#334155,color:#fff
    style Conn fill:#0ea5e9,color:#fff
    style Data fill:#f59e0b,color:#fff
    style Train fill:#6366f1,color:#fff
    style Privacy fill:#ef4444,color:#fff
    style Upload fill:#10b981,color:#fff
```

---

## 3. High-Level Data Flow & Protocol Design

### 3.1 Complete FL Round Execution Flow

```mermaid
sequenceDiagram
    autonumber
    
    participant 👨‍🔬 as AI Scientist
    participant 🖥️ as Web Dashboard
    participant ⚙️ as FL Orchestrator
    participant 📦 as MinIO S3
    participant 🧮 as Aggregation Engine
    participant 🏥 as Edge Agent (Hospital)
    participant 📊 as Telemetry WS
    participant 💾 as PostgreSQL

    rect rgb(239, 246, 255)
        Note over 👨‍🔬, 💾: 📡 Phase 1: Round Initialization
        👨‍🔬->>🖥️: Click "Start Round"
        🖥️->>⚙️: POST /api/v1/projects/{id}/start-round
        ⚙️->>💾: INSERT rounds (status: DISTRIBUTING)
        ⚙️->>📦: Fetch Global Model Weights W_t
        📦-->>⚙️: Return Binary Tensor W_t (98 MB)
    end

    rect rgb(240, 253, 244)
        Note over ⚙️, 🏥: 📡 Phase 2: Weight Distribution
        ⚙️->>🏥: gRPC Stream: StartRound(round_id, W_t, hyperparams)
        🏥-->>⚙️: ACK: Weights Downloaded ✅
        ⚙️->>📊: Broadcast: "ROUND_STARTED" event
        📊->>🖥️: WSS: Real-time status update
    end

    rect rgb(254, 252, 232)
        Note over 🏥, 🏥: 🧠 Phase 3: Local Training at Hospital
        activate 🏥
        🏥->>🏥: Load local dataset into RAM (zero disk writes)
        🏥->>🏥: PyTorch local SGD training (E epochs, B batch size)
        🏥->>🏥: Apply L2 gradient clipping: ||ΔW||₂ ≤ C
        🏥->>🏥: Inject DP Gaussian noise: N(0, σ²C²I)
        🏥->>🏥: Serialize & optionally encrypt update tensor
        deactivate 🏥
    end

    rect rgb(254, 242, 242)
        Note over 🏥, 🧮: 📡 Phase 4: Secure Upload & Aggregation
        🏥->>🧮: gRPC Stream: SubmitUpdate(encrypted_ΔW, sample_count)
        Note over 🧮: Wait for min_nodes OR timeout T_max
        🧮->>🧮: Compute FedAvg: W_{t+1} = W_t + Σ(n_k/N)·ΔW_k
        🧮->>📦: Save W_{t+1} Checkpoint (SHA-256 signed)
        🧮->>💾: UPDATE rounds SET status = COMPLETED, metrics = {...}
    end

    rect rgb(245, 243, 255)
        Note over 🧮, 📊: 📊 Phase 5: Results & Telemetry
        🧮->>⚙️: Report: Aggregation Complete
        ⚙️->>📊: Broadcast: Round metrics (loss, accuracy, ε spent)
        📊->>🖥️: WSS: Live chart update
        🖥️->>👨‍🔬: Updated loss curve & privacy budget gauge
    end
```

---

## 4. Technology Stack Selection

### 4.1 Complete Stack Overview

```mermaid
graph TB
    subgraph "🛠️ MediFL Technology Stack"
        direction TB
        
        subgraph Frontend ["🖥️ Frontend Layer"]
            FE1["⚛️ React 18<br/><i>TypeScript</i>"]
            FE2["🎨 TailwindCSS<br/><i>Utility-First CSS</i>"]
            FE3["📈 Recharts<br/><i>D3-based Charts</i>"]
            FE4["🔌 Socket.io<br/><i>WebSocket Client</i>"]
        end

        subgraph Backend ["⚙️ Backend Layer"]
            BE1["🐍 Python 3.11<br/><i>FastAPI Framework</i>"]
            BE2["📡 gRPC + Protobuf<br/><i>HTTP/2 Streaming</i>"]
            BE3["🔑 Keycloak 22<br/><i>OAuth2/OIDC</i>"]
            BE4["🚪 Envoy Proxy<br/><i>L7 API Gateway</i>"]
        end

        subgraph AI ["🧠 AI & Privacy Layer"]
            AI1["🔥 PyTorch 2.x<br/><i>CUDA GPU Training</i>"]
            AI2["🔒 Opacus<br/><i>DP-SGD Engine</i>"]
            AI3["🌸 Flower / PySyft<br/><i>FL Framework</i>"]
            AI4["🔐 TenSEAL<br/><i>Homomorphic Encryption</i>"]
        end

        subgraph Data ["💾 Data Layer"]
            DA1["🐘 PostgreSQL 15<br/><i>ACID Relational DB</i>"]
            DA2["⚡ Redis 7<br/><i>Pub/Sub & Cache</i>"]
            DA3["📦 MinIO<br/><i>S3-Compatible Storage</i>"]
            DA4["🔑 Vault<br/><i>Secret Management</i>"]
        end

        subgraph Infra ["🏗️ Infrastructure Layer"]
            IN1["🐳 Docker<br/><i>Multi-Stage Builds</i>"]
            IN2["☸️ Kubernetes<br/><i>EKS / GKE / K3s</i>"]
            IN3["📊 Prometheus<br/><i>Metrics Collection</i>"]
            IN4["📈 Grafana<br/><i>Observability Dashboards</i>"]
        end
    end

    style Frontend fill:#6366f1,color:#fff
    style Backend fill:#0ea5e9,color:#fff
    style AI fill:#ef4444,color:#fff
    style Data fill:#f59e0b,color:#fff
    style Infra fill:#10b981,color:#fff
```

### 4.2 Technology Selection Justification

| Layer | Component | Selected Technology | Alternatives Considered | Selection Rationale |
|:---|:---|:---|:---|:---|
| 🖥️ **Frontend** | Web Dashboard | React 18 + TypeScript | Vue 3, Angular 17, Svelte | Largest ecosystem for medical data visualization; Recharts/D3 integration |
| ⚙️ **Backend** | REST API | FastAPI (Python 3.11) | Django REST, Go Gin, Node Express | Native PyTorch compatibility; async performance; auto-OpenAPI docs |
| 📡 **Transport** | Model Weight Exchange | gRPC (HTTP/2 + Protobuf) | REST + JSON, GraphQL, WebSocket | 65% smaller payload than JSON; native streaming for 500 MB tensors |
| 🧠 **ML Runtime** | Local Training | PyTorch 2.x + CUDA | TensorFlow 2.x, JAX | 85%+ medical AI research uses PyTorch; torch.compile() JIT optimization |
| 🔒 **Privacy** | Differential Privacy | Opacus (Meta) + Custom RDP | TF Privacy, PySyft DP | PyTorch-native; per-sample gradient clipping; production-tested at Meta |
| 💾 **Database** | Relational Store | PostgreSQL 15 | MySQL 8, CockroachDB | JSONB column support for FL hyperparams; pgvector for future embedding search |
| ⚡ **Cache** | Real-time State | Redis 7 | Memcached, KeyDB | Pub/Sub for WebSocket broadcasting; sorted sets for leaderboard metrics |

---

## 5. Cross-Cutting Concerns

### 5.1 Observability, Logging & Monitoring Architecture

```mermaid
graph LR
    subgraph "📊 Observability Stack"
        direction TB
        
        Apps["🐳 MediFL Pods<br/><i>API, Aggregator,<br/>Edge Agents</i>"]
        -->|"Prometheus<br/>Metrics Scrape<br/>(/metrics)"| Prom["📊 <b>Prometheus</b><br/><i>Time-Series DB<br/>Alert Rules</i>"]
        -->|"PromQL<br/>Data Source"| Graf["📈 <b>Grafana</b><br/><i>Visual Dashboards<br/>SLA Tracking</i>"]
        
        Apps -->|"Structured JSON<br/>Log Streams"| Loki["📝 <b>Grafana Loki</b><br/><i>Log Aggregation<br/>& Search</i>"]
        -->|"LogQL"| Graf
        
        Prom -->|"Alert Rules<br/>Trigger"| Alert["🚨 <b>Alertmanager</b><br/><i>PagerDuty, Slack,<br/>Email Notifications</i>"]
    end

    style Apps fill:#334155,color:#fff
    style Prom fill:#e6522c,color:#fff
    style Graf fill:#f46800,color:#fff
    style Loki fill:#f46800,color:#fff
    style Alert fill:#ef4444,color:#fff
```

### 5.2 Error Handling Strategy

| Error Category | Example | Handling Strategy | User Notification |
|:---|:---|:---|:---|
| 🔴 **Critical** | Database connection failure | Circuit breaker pattern; automatic failover to replica | ❌ Service degraded banner |
| 🟠 **Recoverable** | Edge node straggler timeout | Exclude node from round; proceed with available updates | ⚠️ Straggler warning toast |
| 🟡 **Warning** | Privacy budget at 80% | Dashboard gauge turns amber; notification sent to CISO | 🔔 Budget warning alert |
| 🔵 **Informational** | New node successfully registered | Log event; update node status to READY | ✅ Success confirmation |

---

<div align="center">

| ← [Phase 4: BRD](./04_BRD.md) | 📄 **Next Document** | [Phase 6: LLD →](./06_LLD.md) |
|:---:|:---:|:---:|

---

*© 2026 MediFL Platform — Confidential & Proprietary*

</div>
