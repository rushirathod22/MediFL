# 🧠 MediFL — Second Project Review Guide

> **Document Purpose**: Presentation guide and technical summary for **Review Phase 2** (Mentored by C-DAC Project Engineer).

---

## 📄 1. Problem Statement & Proposed Solution

### ❌ The Problem in Healthcare AI
* Healthcare institutions (hospitals) want to build accurate diagnostic AI models (e.g., Chest X-Ray disease classification).
* However, medical privacy regulations (**HIPAA** in US, **GDPR** in EU, **ABDM** in India) **strictly forbid sharing or uploading private patient records and X-rays to central servers**.
* As a result, hospital data remains trapped in isolated "data silos", leading to biased or low-accuracy AI models.

### 💡 Our Proposed Solution: MediFL Platform
* **MediFL** is a **Privacy-Preserving Federated Learning Platform**.
* Instead of moving private patient data to a central cloud, **we send the AI model to the hospital edge nodes**.
* Hospitals train the model on local GPUs and send **only mathematical model updates (weights)** back to the server.
* **Zero raw patient data ever leaves the hospital network!**

---

## 🛠️ 2. What We Have Implemented Till Now (Current Deliverables)

In this review phase, we transitioned from initial design to functional implementation of the core FL pipeline:

```text
[ Private Hospital Data ] ──> [ Local PyTorch Training ] ──> [ DP-SGD Noise Injection ]
                                                                       │
[ Live Web Dashboard UI ] <── [ FastAPI Control Server ] <── [ Send Encrypted Weights ]
                                       │
                         [ FedAvg / FedProx Aggregation ]
```

### Key Modules Implemented:
1. **Federated Aggregation Engine (`src/aggregator/`)**:
   * **FedAvg**: Sample-weighted parameter aggregation ($W_{\text{global}} = \sum \frac{n_k}{N} W_k$).
   * **FedProx**: Proximal penalty ($\mu$) to handle imbalanced or Non-IID hospital datasets.
   * **FL Simulator**: Multi-node orchestration engine for simulated hospital rounds.

2. **Differential Privacy & Security Engine (`src/common/privacy.py`)**:
   * **DP-SGD**: $L_2$ gradient norm clipping + Gaussian noise injection to prevent model inversion attacks.
   * **Privacy Accountant**: Real-time tracking of cumulative $(\epsilon, \delta)$ privacy budget expenditure.
   * **SHA-256 Hash Verification**: Generates digital fingerprints for weight integrity auditing.

3. **FastAPI Backend Server (`src/server/main.py`)**:
   * REST endpoints (`/healthz`, `/api/v1/trigger-round`) managing state transitions and round triggers.

4. **Live Control Plane Dashboard (`frontend/index.html`)**:
   * Interactive cyber dark-mode interface with Chart.js accuracy/loss curves, strategy switcher tabs, $\epsilon$-budget progress gauge, SHA-256 terminal log stream, and hospital node telemetry cards.

5. **PyTorch ML Pipeline on Colab (`colab_training/`)**:
   * `MobileNetV2` diagnostic classification script with automated 3-hospital dataset partitioning (50% / 30% / 20%).

> [!NOTE]
> **Important Clarification for Review**: In this phase, we implemented and validated the **initial proof-of-concept rounds (Rounds 1–2)** to demonstrate mathematical aggregation, DP noise injection, and API integration. Full multi-epoch deep training will be executed in the final benchmark phase.

---

## 🏛️ 3. Architecture We Follow

MediFL follows a **Microservice & Zero-Trust C4 Container Architecture**:

```text
                    ┌──────────────────────────┐
                    │  🖥️ Live Web Dashboard    │
                    │   (Chart.js + Audit UI)  │
                    └────────────┬─────────────┘
                                 │ HTTPS / REST
                                 ▼
                    ┌──────────────────────────┐
                    │ ☁️ MediFL Control Plane   │
                    │  ├── FastAPI Orchestrator│
                    │  ├── FedAvg / FedProx    │
                    │  └── DP Privacy Engine   │
                    └────────────▲─────────────┘
                                 │ 🔒 gRPC / mTLS
              ┌──────────────────┼──────────────────┐
              │                  │                  │
        ┌──────────┐       ┌──────────┐       ┌──────────┐
        │ Node A   │       │ Node B   │       │ Node C   │
        │Hospital A│       │Hospital B│       │Hospital C│
        └────┬─────┘       └────┬─────┘       └────┬─────┘
             │                  │                  │
       Local X-Rays       Local X-Rays       Local X-Rays
```

* **Core Principle**: Data remains 100% isolated inside hospital intranets. Only encrypted weight matrices transit across the network.

---

## 📊 4. Current Implementation Status Matrix

| Component                     | Status    | Location / Implementation Details             |
| :------------------------------| :---------:| :----------------------------------------------|
| **Problem Statement & Scope** | ✅ Done    | Documented & Validated                        |
| **FedAvg Aggregation**        | ✅ Done    | `src/aggregator/fedavg.py`                    |
| **FedProx Strategy**          | ✅ Done    | `src/aggregator/fedprox.py`                   |
| **Multi-Hospital Simulator**  | ✅ Done    | `src/aggregator/simulator.py`                 |
| **DP-SGD Noise Injection**    | ✅ Done    | `src/common/privacy.py`                       |
| **Privacy Accountant**        | ✅ Done    | `src/common/privacy.py`                       |
| **SHA-256 Weight Hashes**     | ✅ Done    | Integrity verification audit trail            |
| **FastAPI Backend Core**      | ✅ Done    | `src/server/main.py`                          |
| **Live Web Operations UI**    | ✅ Done    | `frontend/index.html`                         |
| **PyTorch Colab Pipeline**    | ✅ Done    | `colab_training/MediFL_NIH_Colab_Training.py` |
| **Standalone Edge Daemon**    | ⏳ Phase 3 | Planned for Next Review (`src/edge_agent/`)   |
| **PostgreSQL & Redis DB**     | ⏳ Phase 3 | Planned for Next Review                       |
| **Docker Multi-Container**    | ⏳ Phase 3 | Planned for Next Review                       |

---

## 🔮 5. What We Will Build in the Next Review (Future Roadmap)

In the upcoming Phase 3 / Final Review, we will implement:

1. **Standalone Hospital Edge Agent Daemon (`src/edge_agent/`)**:
   * Background client service for automatic local PyTorch training and outbound gRPC streaming.
2. **PostgreSQL 15 & Redis 7 Database Persistence**:
   * Replacing in-memory server state with persistent database models for hospitals, FL rounds, and audit logs.
3. **Full Docker Compose Containerization**:
   * One-command deployment (`docker-compose up`) launching FastAPI, PostgreSQL, Redis, MinIO S3, and Envoy mTLS proxy.
4. **Homomorphic Encryption (TenSEAL)**:
   * Ciphertext aggregation ensuring the central server computes FedAvg without ever decrypting weight parameters.

---

## 🗣️ 6. Core Architecture Summary in One Line

> **Hospital Local Data $\rightarrow$ Local PyTorch Training $\rightarrow$ DP-SGD Noise $\rightarrow$ SHA-256 Hash $\rightarrow$ FastAPI Control Plane $\rightarrow$ FedAvg / FedProx Aggregation $\rightarrow$ Global Model $\rightarrow$ Live Web Dashboard UI**
