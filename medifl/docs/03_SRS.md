<div align="center">

# 📋 MediFL — Software Requirements Specification (SRS)

### 🏥 IEEE Std 830-1998 Compliant

| **Document ID** | **Classification** | **Version** | **Status** |
|:---:|:---:|:---:|:---:|
| `MEDIFL-SRS-003` | 🔒 Confidential | `v1.0.0` | ✅ Approved |

| **Prepared By** | **Standard** | **Approved By** | **Date** |
|:---:|:---:|:---:|:---:|
| Software Architecture Team | IEEE 830-1998 | VP Engineering | August 2026 |

---

</div>

## 📑 Table of Contents

- [1. Introduction & Purpose](#1-introduction--purpose)
- [2. Overall System Description](#2-overall-system-description)
- [3. Functional Requirements](#3-functional-requirements)
- [4. Non-Functional Requirements](#4-non-functional-requirements)
- [5. External Interface Requirements](#5-external-interface-requirements)
- [6. Requirements Traceability Matrix](#6-requirements-traceability-matrix)

---

## 1. Introduction & Purpose

### 1.1 Document Conventions

| Convention | Meaning |
|:---|:---|
| `[FR-XX]` | Functional Requirement with unique identifier |
| `[NFR-XX]` | Non-Functional Requirement with unique identifier |
| 🔴 **High** | Must be implemented in v1.0 release |
| 🟡 **Medium** | Should be implemented in v1.1 release |
| 🔵 **Low** | Could be implemented in future releases |

> [!IMPORTANT]
> All requirements marked **🔴 High** are **mandatory** for v1.0 production release. The system SHALL NOT be deployed to production without 100% implementation of High-priority requirements.

---

## 2. Overall System Description

### 2.1 Three-Tier System Architecture Overview

```mermaid
graph TB
    subgraph "🌐 Tier 1: Presentation Layer"
        direction LR
        UI["🖥️ React SPA Web Dashboard<br/><i>Real-time telemetry, project management,<br/>audit log viewer, model export</i>"]
    end

    subgraph "⚙️ Tier 2: Application & Business Logic Layer"
        direction LR
        API["🔧 FastAPI REST Service<br/><i>Project CRUD, User Auth,<br/>Round Management</i>"]
        gRPC["📡 gRPC Streaming Service<br/><i>Weight distribution,<br/>update collection</i>"]
        Agg["🧮 Secure Aggregation Engine<br/><i>FedAvg, FedProx, DP noise,<br/>HE decryption</i>"]
        WS["📊 WebSocket Telemetry<br/><i>Live metric broadcasting<br/>to dashboard clients</i>"]
    end

    subgraph "💾 Tier 3: Data & Persistence Layer"
        direction LR
        PG["🐘 PostgreSQL 15<br/><i>Projects, Rounds, Nodes,<br/>Audit Logs, Users</i>"]
        Redis["⚡ Redis 7<br/><i>Heartbeats, Session Cache,<br/>Pub/Sub Telemetry</i>"]
        S3["📦 MinIO / S3<br/><i>Encrypted Model Checkpoints<br/>& Weight Tensors</i>"]
    end

    UI <-->|"HTTPS / REST"| API
    UI <-->|"WSS"| WS
    API --> PG
    API --> Redis
    API --> S3
    gRPC --> Agg
    Agg --> S3
    WS --> Redis

    style UI fill:#6366f1,color:#fff
    style API fill:#0ea5e9,color:#fff
    style gRPC fill:#0ea5e9,color:#fff
    style Agg fill:#ef4444,color:#fff
    style WS fill:#0ea5e9,color:#fff
    style PG fill:#334155,color:#fff
    style Redis fill:#334155,color:#fff
    style S3 fill:#334155,color:#fff
```

### 2.2 Edge Node Integration Architecture

```mermaid
graph LR
    subgraph "🏥 Hospital Intranet (Behind Firewall)"
        PACS["💾 PACS Server<br/><i>DICOM Images</i>"]
        EHR["📋 EHR System<br/><i>Clinical Records</i>"]
        Edge["🐳 MediFL Edge Agent<br/><i>Docker Container with<br/>PyTorch + CUDA GPU</i>"]
        
        PACS -->|"Read-Only<br/>Local RAM"| Edge
        EHR -->|"Read-Only<br/>Local RAM"| Edge
    end

    subgraph "☁️ MediFL Cloud (Central)"
        GW["🔐 Envoy mTLS<br/>Gateway"]
    end

    Edge -->|"🔒 Outbound-Only<br/>gRPC / mTLS<br/>(X.509 Client Cert)"| GW

    style Edge fill:#10b981,color:#fff
    style GW fill:#6366f1,color:#fff
```

---

## 3. Functional Requirements

### 3.1 🔐 Authentication & Authorization Module

```mermaid
graph TD
    subgraph "🔐 FR-01 to FR-04: Authentication & Authorization"
        FR01["<b>[FR-01]</b> 🔴 High<br/>JWT-based Authentication<br/><i>OAuth2/OIDC integration<br/>with Keycloak / Azure AD</i>"]
        FR02["<b>[FR-02]</b> 🔴 High<br/>Role-Based Access Control<br/><i>ADMIN, RESEARCHER,<br/>COMPLIANCE_OFFICER roles</i>"]
        FR03["<b>[FR-03]</b> 🔴 High<br/>Node X.509 Client Certs<br/><i>Hospital nodes authenticate<br/>via internal CA</i>"]
        FR04["<b>[FR-04]</b> 🔴 High<br/>Session Expiration Policy<br/><i>JWT: 60 min expiry<br/>Refresh: 24 hour expiry</i>"]
    end

    style FR01 fill:#fef2f2,stroke:#ef4444,stroke-width:2px
    style FR02 fill:#fef2f2,stroke:#ef4444,stroke-width:2px
    style FR03 fill:#fef2f2,stroke:#ef4444,stroke-width:2px
    style FR04 fill:#fef2f2,stroke:#ef4444,stroke-width:2px
```

| Req ID | Requirement Statement | Priority | Validation Criteria |
|:---:|:---|:---:|:---|
| **FR-01** | The system **SHALL** support JWT-based authentication integrated with OAuth2/OIDC supporting Enterprise SSO (Keycloak, Azure AD, Okta). | 🔴 High | Login flow returns valid JWT with user claims; SSO redirect works. |
| **FR-02** | The system **SHALL** enforce RBAC with three roles: `ADMIN` (full access), `RESEARCHER` (project management), `COMPLIANCE_OFFICER` (audit read-only). | 🔴 High | Unauthorized role access returns HTTP 403. |
| **FR-03** | Hospital edge nodes **SHALL** authenticate using X.509 client certificates generated by MediFL's internal Certificate Authority. | 🔴 High | Invalid certificate results in TLS handshake rejection. |
| **FR-04** | JWT access tokens **SHALL** expire after 60 minutes; refresh tokens **SHALL** expire after 24 hours. | 🔴 High | Expired tokens return HTTP 401 Unauthorized. |

---

### 3.2 📡 FL Project & Round Management Module

```mermaid
sequenceDiagram
    autonumber
    participant 👨‍🔬 as AI Scientist
    participant 🖥️ as Web Dashboard
    participant ⚙️ as Orchestrator API
    participant 💾 as PostgreSQL
    participant 📦 as MinIO S3

    👨‍🔬->>🖥️: Create New FL Project
    🖥️->>⚙️: POST /api/v1/projects
    ⚙️->>💾: INSERT INTO projects(...)
    💾-->>⚙️: project_id = UUID
    ⚙️->>📦: Create project model workspace bucket
    ⚙️-->>🖥️: 201 Created {project_id, status: CREATED}
    
    👨‍🔬->>🖥️: Upload PyTorch Model Architecture
    🖥️->>⚙️: POST /api/v1/projects/{id}/model
    ⚙️->>📦: Upload .py model definition file
    ⚙️-->>🖥️: 200 OK {model_hash: sha256:...}

    👨‍🔬->>🖥️: Configure Hyperparameters & Start Round
    🖥️->>⚙️: POST /api/v1/projects/{id}/start-round
    ⚙️->>💾: INSERT INTO rounds(round_number=1, status=DISTRIBUTING)
    Note over ⚙️: Broadcast W_t to all selected hospital nodes via gRPC
```

| Req ID | Requirement Statement | Priority | Validation Criteria |
|:---:|:---|:---:|:---|
| **FR-05** | The system **SHALL** allow Project Managers to create an FL project by uploading a Python model definition (`.py`) or ONNX structure file (`.onnx`). | 🔴 High | File upload succeeds; SHA-256 hash computed and stored. |
| **FR-06** | The system **SHALL** allow setting total FL rounds ($R$), local epochs ($E$), batch size ($B$), learning rate ($\eta$), and optimizer (`SGD`, `AdamW`). | 🔴 High | Parameters persisted in JSONB column; validated against allowed ranges. |
| **FR-07** | The system **SHALL** allow selecting specific registered hospital nodes based on availability status and minimum dataset size criteria. | 🔴 High | Only nodes with status `READY` and `sample_count >= min_samples` are selectable. |
| **FR-08** | The server **SHALL** broadcast global model weights $W_t$ to selected active nodes at the beginning of each round $t$ via gRPC streaming. | 🔴 High | All selected nodes receive complete weight tensor; SHA-256 integrity verified. |
| **FR-09** | The server **SHALL** implement a configurable round timeout $T_{max}$ (default: 600 seconds). Nodes exceeding $T_{max}$ **SHALL** be excluded from round aggregation. | 🔴 High | Straggler nodes marked as `STRAGGLER` in round_participants table. |
| **FR-10** | The server **SHALL** auto-evaluate global validation metric $\mathcal{L}_{val}$ after each round and halt training if loss delta $\Delta \le 10^{-4}$ for 3 consecutive rounds. | 🟡 Medium | Training status changes to `COMPLETED_CONVERGED`. |

---

### 3.3 🔒 Privacy & Security Enforcement Module

> [!CAUTION]
> These requirements are **critical for regulatory compliance**. Failure to implement any FR-11 through FR-15 requirement will result in HIPAA/GDPR violation risk and is a **release blocker**.

```mermaid
graph TD
    subgraph "🔒 Privacy Pipeline — Per Hospital Node Per Round"
        direction TB
        
        Raw["📊 Raw Local Gradient Update<br/><i>∇W from PyTorch backprop</i>"]
        -->|"Step 1"| Clip["✂️ L2 Norm Clipping<br/><i>||ΔW||₂ ≤ C<br/>(Bounds sensitivity)</i>"]
        -->|"Step 2"| Noise["🎲 Gaussian Noise Injection<br/><i>N(0, σ²C²I)<br/>(Differential Privacy)</i>"]
        -->|"Step 3"| Encrypt["🔐 Encrypt Update<br/><i>Homomorphic Encryption<br/>or Shamir Shares</i>"]
        -->|"Step 4"| Upload["📡 Upload via gRPC/mTLS<br/><i>Encrypted tensor chunks<br/>with integrity hash</i>"]
    end

    style Raw fill:#334155,color:#fff
    style Clip fill:#f59e0b,color:#fff
    style Noise fill:#ef4444,color:#fff
    style Encrypt fill:#6366f1,color:#fff
    style Upload fill:#10b981,color:#fff
```

| Req ID | Requirement Statement | Priority | Mathematical Specification |
|:---:|:---|:---:|:---|
| **FR-11** | Edge Agents **SHALL** clip local gradient updates such that $\|\| \Delta w_i \|\|_2 \le C$ | 🔴 High | $\bar{g}(x) = g(x) / \max(1, \frac{\|\|g(x)\|\|_2}{C})$ |
| **FR-12** | Edge Agents **SHALL** add calibrated Gaussian noise to clipped updates | 🔴 High | $\tilde{g} = \bar{g} + \mathcal{N}(0, \sigma^2 C^2 \mathbf{I})$ |
| **FR-13** | The system **SHALL** track cumulative $(\epsilon, \delta)$ privacy expenditure via Rényi DP | 🔴 High | $\epsilon_{RDP}(\alpha) = R \cdot \frac{\alpha}{2\sigma^2}$ |
| **FR-14** | The system **SHALL** auto-terminate experiments when $\epsilon \ge \epsilon_{max}$ | 🔴 High | Status → `TERMINATED_PRIVACY_LIMIT` |
| **FR-15** | The system **SHALL** support additive homomorphic encryption for weight tensor aggregation | 🟡 Medium | CKKS scheme with polynomial modulus degree $N = 8192$ |

---

## 4. Non-Functional Requirements

### 4.1 📊 Performance & Scalability Requirements

```mermaid
graph LR
    subgraph "⚡ Performance Targets"
        NFR01["<b>[NFR-01]</b><br/>500 concurrent<br/>edge nodes"]
        NFR02["<b>[NFR-02]</b><br/>≤ 45 sec weight<br/>transfer (500 MB)"]
        NFR03["<b>[NFR-03]</b><br/>≤ 1.0 sec dashboard<br/>telemetry refresh"]
        NFR04["<b>[NFR-04]</b><br/>≤ 5 sec API<br/>response time (P99)"]
        NFR05["<b>[NFR-05]</b><br/>≥ 70% gradient<br/>compression ratio"]
    end

    style NFR01 fill:#0ea5e9,color:#fff
    style NFR02 fill:#0ea5e9,color:#fff
    style NFR03 fill:#0ea5e9,color:#fff
    style NFR04 fill:#0ea5e9,color:#fff
    style NFR05 fill:#0ea5e9,color:#fff
```

| Req ID | Category | Requirement | Target Metric | Measurement Method |
|:---:|:---|:---|:---:|:---|
| **NFR-01** | Scalability | Central server **SHALL** support up to 500 concurrent active edge nodes | 500 nodes | K6 load test with 500 simulated gRPC clients |
| **NFR-02** | Performance | Model updates ≤ 500 MB **SHALL** transfer via gRPC within 45 seconds | $\le 45$ sec | Network telemetry measurement at 100 Mbps |
| **NFR-03** | Responsiveness | Dashboard telemetry **SHALL** reflect within 1 second of server emission | $\le 1.0$ sec | WebSocket latency measurement (P95) |
| **NFR-04** | Latency | REST API endpoints **SHALL** respond within 5 seconds (P99) | $\le 5.0$ sec | Application Performance Monitoring (APM) |
| **NFR-05** | Efficiency | Gradient compression **SHALL** reduce payload size by ≥ 70% | $\ge 70\%$ | Payload size comparison (compressed vs. raw) |

### 4.2 🔐 Security & Compliance Requirements

| Req ID | Category | Requirement | Target | Standard Reference |
|:---:|:---|:---|:---:|:---|
| **NFR-06** | Encryption | All external communications **MUST** use TLS 1.3 with AES-256-GCM | TLS 1.3 | NIST SP 800-52 Rev. 2 |
| **NFR-07** | Data Isolation | Edge Agent **MUST NEVER** write local dataset samples to persistent disk | Zero writes | HIPAA § 164.312(a)(1) |
| **NFR-08** | Audit Logging | System logs **MUST** scrub PHI; logs **MUST** have 7-year retention | 7 years | HIPAA § 164.530(j)(2) |
| **NFR-09** | Integrity | Every checkpoint $W_t$ **MUST** be SHA-256 signed with immutable timestamps | SHA-256 | NIST FIPS 180-4 |
| **NFR-10** | Authentication | All API endpoints **MUST** require valid JWT or X.509 certificate | 100% coverage | OWASP API Security Top 10 |

### 4.3 🛡️ Reliability & Availability Requirements

| Req ID | Category | Requirement | Target | Recovery Strategy |
|:---:|:---|:---|:---:|:---|
| **NFR-11** | Availability | Central Orchestrator **SHALL** maintain 99.9% uptime | 99.9% SLA | Multi-AZ Kubernetes deployment |
| **NFR-12** | Resilience | Edge Agents **SHALL** auto-retry reconnection (exponential backoff, max 10 attempts) | 10 retries | Exponential delay: $2^n$ seconds |
| **NFR-13** | Failover | PostgreSQL **MUST** use HA streaming replication with $\le 30$ sec failover | $\le 30$ sec | PostgreSQL Primary-Replica with Patroni |

---

## 5. External Interface Requirements

### 5.1 Communication Protocols

```mermaid
graph TB
    subgraph "🌐 External Interfaces"
        direction TB
        
        subgraph "REST API (HTTPS)"
            REST["📡 OpenAPI 3.0<br/><i>JSON over HTTPS<br/>Port 443</i>"]
        end
        
        subgraph "gRPC (HTTP/2)"
            GRPC["📡 Protocol Buffers<br/><i>Binary streaming<br/>Port 50051</i>"]
        end
        
        subgraph "WebSocket (WSS)"
            WSS["📊 JSON Events<br/><i>Real-time telemetry<br/>Port 443/ws</i>"]
        end
        
        subgraph "Database"
            DB["🐘 PostgreSQL Wire<br/><i>TCP connection<br/>Port 5432</i>"]
        end
    end

    style REST fill:#0ea5e9,color:#fff
    style GRPC fill:#6366f1,color:#fff
    style WSS fill:#10b981,color:#fff
    style DB fill:#334155,color:#fff
```

---

## 6. Requirements Traceability Matrix

> [!TIP]
> This matrix maps every functional requirement to its corresponding Epic (from PRD), Test Case (from Test Plan), and Architecture Component (from HLD).

| Req ID | PRD Epic | Test Case ID | Architecture Component | Implementation File |
|:---:|:---:|:---:|:---|:---|
| FR-01 | EP-1.3 | TC-AUTH-001 | Auth Service / Keycloak | `src/auth/oauth_handler.py` |
| FR-05 | EP-1.1 | TC-PROJ-001 | Orchestrator Core | `src/api/projects.py` |
| FR-08 | EP-1.4 | TC-ROUND-003 | gRPC Streaming Service | `src/grpc/weight_broadcaster.py` |
| FR-11 | EP-2.1 | TC-PRIV-001 | Edge Agent DP Module | `edge/privacy/dp_clipper.py` |
| FR-13 | EP-2.2 | TC-PRIV-003 | Privacy Engine | `src/privacy/rdp_accountant.py` |
| NFR-01 | EP-4.1 | TC-PERF-001 | Kubernetes HPA Config | `k8s/hpa-api.yaml` |

---

<div align="center">

| ← [Phase 2: PRD](./02_PRD.md) | 📄 **Next Document** | [Phase 4: BRD →](./04_BRD.md) |
|:---:|:---:|:---:|

---

*© 2026 MediFL Platform — Confidential & Proprietary*

</div>
