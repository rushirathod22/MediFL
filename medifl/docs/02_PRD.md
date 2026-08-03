<div align="center">

# 📋 MediFL — Product Requirements Document (PRD)

### 🏥 Enterprise Medical Federated Learning Platform

| **Document ID** | **Classification** | **Version** | **Status** |
|:---:|:---:|:---:|:---:|
| `MEDIFL-PRD-002` | 🔒 Confidential | `v1.0.0` | ✅ Approved |

| **Prepared By** | **Reviewed By** | **Approved By** | **Date** |
|:---:|:---:|:---:|:---:|
| Product Management Team | Lead AI Scientist & CISO | VP Product & Engineering | August 2026 |

---

</div>

## 📑 Table of Contents

- [1. Product Overview & Strategic Goal](#1-product-overview--strategic-goal)
- [2. Target User Personas](#2-target-user-personas)
- [3. Epics & Feature Capability Map](#3-epics--feature-capability-map)
- [4. User Journey & Workflow Mapping](#4-user-journey--workflow-mapping)
- [5. Feature Prioritization (MoSCoW)](#5-feature-prioritization-moscow)
- [6. Non-Functional Product Requirements](#6-non-functional-product-requirements)
- [7. Release Strategy & Versioning](#7-release-strategy--versioning)

---

## 1. Product Overview & Strategic Goal

MediFL transforms multi-center clinical AI research from a **12+ month legal negotiation process** into a **2-week technical onboarding workflow** by eliminating the need to transfer any raw patient data between institutions.

```mermaid
graph TB
    subgraph "📊 MediFL Product Value Chain"
        direction LR
        
        Input["🏥 Siloed Hospital<br/>Clinical Data<br/><i>(EHR, DICOM, Genomic)</i>"] 
        --> Process["🧠 MediFL<br/>Federated Training<br/><i>(Privacy-Preserved)</i>"]
        --> Output["🤖 Superior Global<br/>Diagnostic AI Model<br/><i>(Multi-Center Validated)</i>"]
        --> Impact["❤️ Improved Patient<br/>Outcomes & Faster<br/>Clinical Decisions"]
    end

    style Input fill:#334155,color:#fff
    style Process fill:#6366f1,color:#fff
    style Output fill:#0ea5e9,color:#fff
    style Impact fill:#10b981,color:#fff
```

---

## 2. Target User Personas

### 👨‍🔬 Persona A: Dr. Aris Thorne — Chief Medical AI Scientist

```mermaid
graph LR
    subgraph "👨‍🔬 Dr. Aris Thorne — AI Research Lead"
        direction TB
        Bio["<b>Demographics</b><br/>Age: 38 | PhD Biomedical AI<br/>Hospital: Academic Medical Center<br/>Team: 5 ML Engineers"]
        Goal["<b>Primary Goal</b><br/>Train a multi-class chest CT<br/>diagnostic model across 15<br/>hospital networks"]
        Pain["<b>Key Pain Points</b><br/>❌ Cannot access raw CT scans<br/>from partner institutions<br/>❌ Privacy tools degrade accuracy<br/>❌ No reproducibility guarantees"]
        Need["<b>What They Need from MediFL</b><br/>✅ Custom PyTorch model uploads<br/>✅ DP budget fine-tuning controls<br/>✅ Real-time convergence metrics<br/>✅ ONNX model export capability"]
    end

    style Bio fill:#eff6ff,stroke:#3b82f6
    style Goal fill:#f0fdf4,stroke:#16a34a
    style Pain fill:#fef2f2,stroke:#ef4444
    style Need fill:#fefce8,stroke:#eab308
```

### 🛡️ Persona B: Elena Rostova — Hospital CISO

| Attribute | Detail |
|:---|:---|
| **Role** | Chief Information Security Officer, Regional Hospital Chain (12 sites) |
| **Primary Goal** | Ensure all hospital compute jobs adhere to HIPAA & GDPR without risk of data leaks |
| **Pain Points** | ❌ Cloud AI providers demand data upload — ❌ No visibility into what leaves hospital — ❌ Audit trail gaps |
| **Needs from MediFL** | ✅ Transparent edge agent source code — ✅ Outbound-only mTLS connections — ✅ Verifiable DP audit logs — ✅ Real-time privacy budget monitoring |

### 🔧 Persona C: Mark Vance — Enterprise DevOps Engineer

| Attribute | Detail |
|:---|:---|
| **Role** | Senior Infrastructure Engineer, Pharmaceutical Company IT Division |
| **Primary Goal** | Deploy and maintain MediFL edge nodes across 20 remote hospital K8s clusters |
| **Pain Points** | ❌ Fragmented hardware specs across hospitals — ❌ Unpredictable network disconnects — ❌ Manual certificate management |
| **Needs from MediFL** | ✅ Helm charts & automated deployment — ✅ Auto-reconnection logic — ✅ Health check dashboards — ✅ Certificate auto-rotation |

---

## 3. Epics & Feature Capability Map

```mermaid
graph TD
    subgraph "🎯 MediFL Product Epic Breakdown"
        direction TB
        
        subgraph E1 ["📡 Epic 1: FL Orchestration & Scheduling"]
            F1["EP-1.1 🆕 Create FL Project<br/><i>Upload model architecture,<br/>set domain & objectives</i>"]
            F2["EP-1.2 ⚙️ Configure Hyperparameters<br/><i>Rounds, epochs, LR, batch size,<br/>aggregation algorithm</i>"]
            F3["EP-1.3 👥 Participant Recruitment<br/><i>Token-auth invitations<br/>to hospital nodes</i>"]
            F4["EP-1.4 🔄 Round State Machine<br/><i>IDLE → DISTRIBUTING →<br/>COLLECTING → AGGREGATING</i>"]
        end

        subgraph E2 ["🔐 Epic 2: Privacy & Security Engine"]
            F5["EP-2.1 ✂️ DP-SGD Implementation<br/><i>L2 gradient clipping &<br/>Gaussian noise injection</i>"]
            F6["EP-2.2 📊 RDP Budget Accountant<br/><i>Rényi DP tracking per<br/>node and experiment</i>"]
            F7["EP-2.3 🔒 Secure Aggregation<br/><i>HE (Paillier/CKKS) or<br/>Shamir Secret Sharing</i>"]
        end

        subgraph E3 ["🐳 Epic 3: Hospital Edge Node SDK"]
            F8["EP-3.1 📦 Containerized Runtime<br/><i>Docker + CUDA GPU<br/>support for Linux</i>"]
            F9["EP-3.2 💾 Data Connectors<br/><i>DICOM PACS, CSV EHR,<br/>NIfTI volumes</i>"]
            F10["EP-3.3 📡 Outbound mTLS<br/><i>No inbound ports needed<br/>inside hospital firewall</i>"]
        end

        subgraph E4 ["📊 Epic 4: Observability & Governance"]
            F11["EP-4.1 📈 Live Round Telemetry<br/><i>Loss curves, accuracy, gradient<br/>norms, GPU utilization</i>"]
            F12["EP-4.2 🔏 Cryptographic Checkpoints<br/><i>SHA-256 signed model<br/>versions with lineage</i>"]
            F13["EP-4.3 📤 Model Export<br/><i>ONNX, PyTorch .pt,<br/>TorchScript formats</i>"]
        end
    end

    style E1 fill:#eff6ff,stroke:#3b82f6,stroke-width:2px
    style E2 fill:#fef2f2,stroke:#ef4444,stroke-width:2px
    style E3 fill:#f0fdf4,stroke:#16a34a,stroke-width:2px
    style E4 fill:#fefce8,stroke:#eab308,stroke-width:2px
```

### 3.1 Epic Detail Specifications

> [!IMPORTANT]
> Each Epic has been decomposed into **User Stories** following the format:
> *"As a [persona], I want to [action], so that [outcome]."*

#### 📡 Epic 1: FL Orchestration & Scheduling

| Story ID | User Story | Acceptance Criteria | Priority |
|:---:|:---|:---|:---:|
| `US-101` | As an **AI Scientist**, I want to create a new FL project by uploading my PyTorch model file | Model file validated, project workspace initialized, registration tokens generated | 🔴 P0 |
| `US-102` | As an **AI Scientist**, I want to configure FL hyperparameters (rounds $R$, epochs $E$, LR $\eta$, batch size $B$) | All parameters persisted in project config, validated against allowed ranges | 🔴 P0 |
| `US-103` | As a **Trial Manager**, I want to invite specific hospitals by sending token-authenticated invitations | Invitation tokens generated with 72-hour expiry, logged in audit trail | 🔴 P0 |
| `US-104` | As the **System**, I want to manage a round state machine (IDLE → DISTRIBUTING → COLLECTING → AGGREGATING → COMPLETED) | State transitions enforced atomically with PostgreSQL row-level locking | 🔴 P0 |
| `US-105` | As the **System**, I want to handle straggler nodes that exceed timeout $T_{max}$ | Straggler nodes excluded from aggregation; round proceeds with available updates | 🟡 P1 |

#### 🔐 Epic 2: Privacy & Security Engine

| Story ID | User Story | Acceptance Criteria | Priority |
|:---:|:---|:---|:---:|
| `US-201` | As an **AI Scientist**, I want to set L2 clipping bound $C$ and noise multiplier $\sigma$ for my experiment | Parameters validated and applied to every local update before aggregation | 🔴 P0 |
| `US-202` | As the **System**, I want to track cumulative $(\epsilon, \delta)$ privacy expenditure via Rényi DP | RDP accountant updated after every round; budget displayed on dashboard | 🔴 P0 |
| `US-203` | As the **System**, I want to **auto-terminate** an experiment when $\epsilon \ge \epsilon_{max}$ | Experiment status set to `TERMINATED_PRIVACY_LIMIT`; all stakeholders notified | 🔴 P0 |

---

## 4. User Journey & Workflow Mapping

```mermaid
journey
    title End-to-End FL Campaign User Journey
    section Project Setup
      Login to Web Portal: 5: AI Scientist
      Create New FL Campaign: 4: AI Scientist
      Upload PyTorch Model File: 4: AI Scientist
      Configure DP Privacy Parameters: 3: AI Scientist, CISO
    section Hospital Onboarding
      Generate Registration Tokens: 5: Trial Manager
      Send Invitations to Hospitals: 4: Trial Manager
      Deploy Edge Agent Container: 3: Hospital IT Admin
      Verify Node Status (READY): 5: Hospital IT Admin
    section Training Execution
      Trigger First Training Round: 5: AI Scientist
      Monitor Live Loss Curves: 4: AI Scientist
      Review Privacy Budget Gauge: 4: CISO
      Handle Straggler Timeout: 3: System
    section Model Delivery
      Evaluate Final Model Metrics: 5: AI Scientist
      Download Audit Report PDF: 4: CISO, IRB
      Export ONNX Model File: 5: AI Scientist
```

### 4.1 Critical User Flow: Round Execution Lifecycle

```mermaid
stateDiagram-v2
    [*] --> IDLE: Project Created

    IDLE --> DISTRIBUTING: Trigger Round
    DISTRIBUTING --> COLLECTING: All Nodes Downloaded Weights
    
    COLLECTING --> AGGREGATING: Min Nodes Responded OR Timeout
    COLLECTING --> COLLECTING: Waiting for Node Updates...
    
    AGGREGATING --> EVALUATED: FedAvg/FedProx Computed
    EVALUATED --> IDLE: Continue to Next Round
    EVALUATED --> COMPLETED: Final Round Reached
    EVALUATED --> TERMINATED: Privacy Budget Exhausted

    COMPLETED --> [*]
    TERMINATED --> [*]

    note right of DISTRIBUTING
        Server broadcasts global
        model weights W_t via
        gRPC streaming to all
        selected hospital nodes
    end note

    note right of COLLECTING
        Nodes perform local training,
        apply L2 clipping & DP noise,
        encrypt gradients, upload
        via mTLS gRPC stream
    end note

    note right of AGGREGATING
        Secure Aggregator computes
        weighted FedAvg/FedProx,
        generates W_{t+1}, saves
        SHA-256 signed checkpoint
    end note
```

---

## 5. Feature Prioritization (MoSCoW)

```mermaid
quadrantChart
    title MediFL Feature Priority vs. Implementation Effort
    x-axis Low Effort --> High Effort
    y-axis Low Priority --> High Priority
    quadrant-1 Must Have (v1.0)
    quadrant-2 Should Have (v1.1)
    quadrant-3 Won't Have (v1.0)
    quadrant-4 Could Have (v1.2)
    FedAvg Algorithm: [0.3, 0.95]
    DP-SGD Privacy: [0.4, 0.9]
    mTLS Auth: [0.35, 0.88]
    WebSocket Dashboard: [0.5, 0.82]
    PyTorch Adapter: [0.25, 0.85]
    Homomorphic Encryption: [0.75, 0.7]
    DICOM PACS Connector: [0.65, 0.6]
    Straggler Auto-Scaling: [0.6, 0.65]
    SCAFFOLD Algorithm: [0.7, 0.5]
    Multi-Cloud Deploy: [0.8, 0.45]
    Patient Diagnostics: [0.9, 0.2]
```

### 5.1 MoSCoW Classification Table

| Priority | Feature | Target Release | Justification |
|:---:|:---|:---:|:---|
| 🔴 **Must Have** | FedAvg & FedProx aggregation | v1.0 | Core FL algorithms required for MVP |
| 🔴 **Must Have** | DP-SGD with RDP accountant | v1.0 | Privacy is the platform's core value proposition |
| 🔴 **Must Have** | mTLS X.509 edge authentication | v1.0 | Zero-Trust security is non-negotiable for hospital adoption |
| 🔴 **Must Have** | Real-time WebSocket telemetry dashboard | v1.0 | Operators must monitor training progress in real-time |
| 🔴 **Must Have** | PyTorch local training adapter | v1.0 | PyTorch dominates medical AI research (85%+ market share) |
| 🟡 **Should Have** | Homomorphic Encryption (CKKS) for aggregation | v1.1 | Additional security layer for highest-sensitivity deployments |
| 🟡 **Should Have** | DICOM PACS native connector | v1.1 | Direct integration eliminates manual data export steps |
| 🟡 **Should Have** | Automated straggler timeout & dynamic cohort scaling | v1.1 | Improves robustness in unreliable hospital network environments |
| 🔵 **Could Have** | SCAFFOLD & FedOpt algorithms | v1.2 | Advanced convergence optimization for extreme non-IID scenarios |
| ⚪ **Won't Have** | Automated direct-to-patient diagnostic reporting | Never | Requires licensed physician oversight — regulatory restriction |

---

## 6. Non-Functional Product Requirements

| NFR Category | Requirement | Target Metric |
|:---|:---|:---|
| ⚡ **Performance** | Dashboard telemetry refresh latency | $\le 1.0$ second |
| 📈 **Scalability** | Maximum concurrent edge hospital nodes | 500 nodes |
| 🔒 **Security** | Transport encryption standard | TLS 1.3 / AES-256-GCM |
| 🛡️ **Privacy** | Maximum allowed privacy budget per experiment | $\epsilon \le 8.0$, $\delta \le 10^{-5}$ |
| 🕐 **Availability** | Central orchestrator uptime SLA | $\ge 99.9\%$ |
| 📱 **Usability** | New user time-to-first-FL-round | $\le 30$ minutes |

---

## 7. Release Strategy & Versioning

```mermaid
timeline
    title MediFL Product Release Timeline
    section v1.0 (MVP)
        August 2026 : FedAvg + FedProx
                    : DP-SGD Privacy Engine
                    : mTLS Edge Authentication
                    : Real-time Web Dashboard
    section v1.1 (Security+)
        November 2026 : Homomorphic Encryption (CKKS)
                      : DICOM PACS Native Connector
                      : Dynamic Straggler Handling
    section v1.2 (Advanced FL)
        February 2027 : SCAFFOLD Algorithm
                      : FedOpt Adaptive Optimizer
                      : Multi-Cloud Deployment
    section v2.0 (Platform)
        Q2 2027 : Federated Analytics
                : Vertical FL Support
                : Blockchain Audit Ledger
```

---

<div align="center">

| ← [Phase 1: Vision & Scope](./01_VISION_AND_SCOPE.md) | 📄 **Next Document** | [Phase 3: SRS →](./03_SRS.md) |
|:---:|:---:|:---:|

---

*© 2026 MediFL Platform — Confidential & Proprietary*

</div>
