<div align="center">

# 🧠 MediFL — AI Architecture Document

### 🏥 Federated Learning Pipeline, Differential Privacy & Model Lineage

| **Document ID** | **Classification** | **Version** | **Status** |
|:---:|:---:|:---:|:---:|
| `MEDIFL-AI-008` | 🔒 Confidential | `v1.0.0` | ✅ Approved |

| **Prepared By** | **Focus Area** | **Approved By** | **Date** |
|:---:|:---:|:---:|:---:|
| Lead AI Research Scientist | FL Algorithms, DP-SGD, Secure Aggregation | CTO & Chief AI Officer | August 2026 |

---

</div>

## 📑 Table of Contents

- [1. Federated Learning Mathematical Framework](#1-federated-learning-mathematical-framework)
- [2. Aggregation Algorithm Engine](#2-aggregation-algorithm-engine)
- [3. Differential Privacy (DP-SGD) & Budget Accounting](#3-differential-privacy-dp-sgd--budget-accounting)
- [4. Supported Medical AI Model Architectures](#4-supported-medical-ai-model-architectures)
- [5. Model Lineage & Reproducibility Ledger](#5-model-lineage--reproducibility-ledger)

---

## 1. Federated Learning Mathematical Framework

### 1.1 Problem Formulation

MediFL coordinates distributed optimization across $K$ heterogeneous hospital nodes, each with local dataset $\mathcal{D}_k$ of size $n_k$:

```mermaid
graph LR
    subgraph "🧮 Federated Optimization Objective"
        Obj["<b>Global Objective:</b><br/><br/>min<sub>w ∈ ℝᵈ</sub> f(w)<br/><br/>where f(w) = Σ<sub>k=1</sub><sup>K</sup> (n<sub>k</sub>/N) · F<sub>k</sub>(w)<br/><br/>F<sub>k</sub>(w) = (1/n<sub>k</sub>) Σ<sub>i ∈ D<sub>k</sub></sub> ℓ(w; x<sub>i</sub>, y<sub>i</sub>)<br/><br/><i>N = Σn<sub>k</sub> (total samples across all hospitals)</i>"]
    end

    style Obj fill:#6366f1,color:#fff
```

> [!IMPORTANT]
> Each hospital's local loss function $F_k(w)$ is computed entirely within the hospital intranet. Only the **resulting model parameter updates** (not data) are transmitted to the central aggregator.

---

## 2. Aggregation Algorithm Engine

### 2.1 Complete FL Round Pipeline

```mermaid
graph TD
    subgraph "🔄 Federated Learning Round Pipeline"
        direction TB
        
        Start["🚀 <b>Round t Begins</b><br/><i>Server has global model W<sub>t</sub></i>"]
        
        -->|"Step 1: Distribute"| Broadcast["📡 <b>Broadcast Global Weights</b><br/><i>Server sends W<sub>t</sub> to all<br/>selected hospital nodes<br/>via gRPC streaming</i>"]
        
        -->|"Step 2: Local Training"| LocalTraining
        
        subgraph LocalTraining ["🏥 Parallel Local Training (Hospital Nodes)"]
            direction LR
            NodeA["🏥 <b>Hospital A</b><br/><i>E epochs local SGD<br/>n<sub>A</sub> = 5,000 samples<br/>Loss: 0.312</i>"]
            NodeB["🏥 <b>Hospital B</b><br/><i>E epochs local SGD<br/>n<sub>B</sub> = 8,200 samples<br/>Loss: 0.287</i>"]
            NodeC["🏥 <b>Hospital C</b><br/><i>E epochs local SGD<br/>n<sub>C</sub> = 3,100 samples<br/>Loss: 0.341</i>"]
        end

        LocalTraining -->|"Step 3: Privacy Sanitization"| Privacy

        subgraph Privacy ["🔐 Per-Node Privacy Pipeline"]
            direction LR
            Clip["✂️ L2 Clipping<br/><i>||ΔW||₂ ≤ C</i>"]
            Noise["🎲 DP Noise<br/><i>+ N(0, σ²C²I)</i>"]
            Encrypt["🔒 Encrypt<br/><i>HE / SSS</i>"]
            Clip --> Noise --> Encrypt
        end

        Privacy -->|"Step 4: Upload"| Upload["📤 <b>Secure Upload</b><br/><i>Encrypted ΔW sent via<br/>gRPC mTLS stream</i>"]

        Upload -->|"Step 5: Aggregate"| Aggregate

        subgraph Aggregate ["🧮 Central Secure Aggregation"]
            direction TB
            Alg{{"Algorithm<br/>Selection?"}}
            Alg -->|"FedAvg"| FedAvg["<b>FedAvg</b><br/><i>W<sub>t+1</sub> = W<sub>t</sub> + Σ (n<sub>k</sub>/N)·ΔW<sub>k</sub></i>"]
            Alg -->|"FedProx"| FedProx["<b>FedProx</b><br/><i>W<sub>t+1</sub> with proximal<br/>penalty μ/2·||W-W<sub>t</sub>||²</i>"]
        end

        Aggregate -->|"Step 6: Checkpoint"| Save["💾 <b>Save W<sub>t+1</sub></b><br/><i>SHA-256 signed checkpoint<br/>Stored in MinIO/S3<br/>Lineage record logged</i>"]

        Save -->|"Round t+1?"| Start
    end

    style Start fill:#0ea5e9,color:#fff
    style Broadcast fill:#6366f1,color:#fff
    style NodeA fill:#10b981,color:#fff
    style NodeB fill:#10b981,color:#fff
    style NodeC fill:#10b981,color:#fff
    style Clip fill:#f59e0b,color:#fff
    style Noise fill:#ef4444,color:#fff
    style Encrypt fill:#8b5cf6,color:#fff
    style Upload fill:#0ea5e9,color:#fff
    style FedAvg fill:#6366f1,color:#fff
    style FedProx fill:#6366f1,color:#fff
    style Save fill:#10b981,color:#fff
```

### 2.2 Algorithm Comparison Matrix

| Property | **FedAvg** | **FedProx** | **SCAFFOLD** (v1.2) |
|:---|:---:|:---:|:---:|
| **Handles Non-IID Data** | ⚠️ Moderate | ✅ Strong | ✅ Best |
| **Communication Rounds to Converge** | Medium | Medium | Low |
| **Computation Overhead per Node** | Low | Low (+proximal) | Medium (+control variates) |
| **Memory Overhead per Node** | Low | Low | High (stores control variates) |
| **Mathematical Formulation** | $W_{t+1} = \sum \frac{n_k}{N} W_k$ | $+ \frac{\mu}{2}\|\|w - W_t\|\|^2$ | $+ c_k - c$ (variance reduction) |
| **Best Use Case** | IID / mild non-IID data | Non-IID clinical demographics | Extreme non-IID across institutions |

---

## 3. Differential Privacy (DP-SGD) & Budget Accounting

### 3.1 Privacy Guarantee Visualization

```mermaid
graph TD
    subgraph "🔐 (ε, δ)-Differential Privacy Guarantee"
        direction TB
        
        Def["<b>Definition:</b><br/><br/>A mechanism M satisfies (ε, δ)-DP if<br/>for all datasets D, D' differing in<br/>one record, and all outputs S:<br/><br/><b>Pr[M(D) ∈ S] ≤ e<sup>ε</sup> · Pr[M(D') ∈ S] + δ</b><br/><br/><i>Meaning: An adversary observing the<br/>model output cannot determine whether<br/>any specific patient's data was used.</i>"]
        
        Params["<b>MediFL Default Parameters:</b><br/><br/>🔒 ε (epsilon) ≤ 2.0 — privacy budget<br/>🎯 δ (delta) = 10⁻⁵ — failure probability<br/>✂️ C (clip norm) = 1.0 — sensitivity bound<br/>🎲 σ (noise mult) = 1.2 — noise scale<br/><br/><i>Lower ε = stronger privacy<br/>Higher σ = more noise = stronger privacy</i>"]
    end

    style Def fill:#6366f1,color:#fff
    style Params fill:#10b981,color:#fff
```

### 3.2 Privacy vs. Accuracy Trade-off Landscape

```mermaid
quadrantChart
    title DP Privacy Budget vs. Model Accuracy Trade-off
    x-axis Weaker Privacy (High ε) --> Stronger Privacy (Low ε)
    y-axis Lower Accuracy --> Higher Accuracy
    quadrant-1 Ideal Zone (Strong Privacy + High Accuracy)
    quadrant-2 High Accuracy but Weak Privacy
    quadrant-3 Poor on Both
    quadrant-4 Strong Privacy but Low Accuracy
    No DP (ε=∞): [0.05, 0.95]
    ε=4.2 (σ=0.8): [0.3, 0.92]
    ε=1.95 (σ=1.2) TARGET: [0.55, 0.88]
    ε=0.65 (σ=2.5): [0.85, 0.78]
    ε=0.1 (σ=10.0): [0.98, 0.55]
```

### 3.3 Rényi DP Accounting Formula

> [!IMPORTANT]
> MediFL uses **Rényi Differential Privacy** (RDP) for tighter composition bounds compared to basic composition. The RDP accountant tracks privacy loss at multiple orders $\alpha$ and converts to $(\epsilon, \delta)$-DP via optimal order selection.

**Step 1 — Per-round RDP at order $\alpha$:**
$$\epsilon_{RDP}(\alpha) = \frac{\alpha}{2\sigma^2}$$

**Step 2 — Composition over $R$ rounds:**
$$\epsilon_{total}(\alpha) = R \cdot \epsilon_{RDP}(\alpha) = \frac{R \cdot \alpha}{2\sigma^2}$$

**Step 3 — Convert to $(\epsilon, \delta)$-DP:**
$$\epsilon(\delta) = \min_{\alpha > 1} \left\{ \epsilon_{total}(\alpha) + \frac{\ln(1/\delta)}{\alpha - 1} \right\}$$

---

## 4. Supported Medical AI Model Architectures

```mermaid
graph TD
    subgraph "🧠 MediFL Supported Model Architecture Registry"
        direction TB
        
        subgraph Vision ["👁️ Computer Vision Models"]
            V1["📸 <b>DenseNet-121</b><br/><i>Chest X-Ray Classification<br/>7.0M parameters<br/>Input: 224×224 RGB</i>"]
            V2["📸 <b>ResNet-50</b><br/><i>Multi-class Radiology<br/>23.5M parameters<br/>Input: 224×224 RGB</i>"]
            V3["🔬 <b>3D U-Net</b><br/><i>CT/MRI Segmentation<br/>19.0M parameters<br/>Input: 3D NIfTI Volume</i>"]
            V4["🧬 <b>Vision Transformer (ViT)</b><br/><i>Pathology Slide Analysis<br/>86.0M parameters<br/>Input: 224×224 patches</i>"]
        end

        subgraph NLP ["📝 Clinical NLP Models"]
            N1["📄 <b>BioClinical-BERT</b><br/><i>EHR Note Classification<br/>110.0M parameters<br/>Input: Tokenized text</i>"]
            N2["📄 <b>ClinicalLongformer</b><br/><i>Long Clinical Documents<br/>149.0M parameters<br/>Input: 4096 token context</i>"]
        end

        subgraph Tabular ["📊 Tabular & Genomic Models"]
            T1["🧬 <b>Genomic MLP</b><br/><i>Variant Risk Scoring<br/>1.2M parameters<br/>Input: Genotype array</i>"]
            T2["📊 <b>TabNet</b><br/><i>Structured EHR Prediction<br/>2.5M parameters<br/>Input: Tabular features</i>"]
        end
    end

    style Vision fill:#eff6ff,stroke:#3b82f6,stroke-width:2px
    style NLP fill:#fef2f2,stroke:#ef4444,stroke-width:2px
    style Tabular fill:#f0fdf4,stroke:#16a34a,stroke-width:2px
```

---

## 5. Model Lineage & Reproducibility Ledger

### 5.1 Immutable Lineage Record Structure

```mermaid
graph LR
    subgraph "📋 Cryptographic Model Lineage Chain"
        direction LR
        
        R0["🧠 <b>Round 0</b><br/><i>Initial Random Weights<br/>hash: sha256:a3f4...</i>"]
        -->|"FedAvg + DP"| R1["🧠 <b>Round 1</b><br/><i>3 hospitals contributed<br/>hash: sha256:b7e2...</i>"]
        -->|"FedAvg + DP"| R2["🧠 <b>Round 2</b><br/><i>5 hospitals contributed<br/>hash: sha256:c9d1...</i>"]
        -->|"..."| RN["🧠 <b>Round N</b><br/><i>Final Global Model<br/>hash: sha256:f8a3...</i>"]
    end

    style R0 fill:#334155,color:#fff
    style R1 fill:#6366f1,color:#fff
    style R2 fill:#0ea5e9,color:#fff
    style RN fill:#10b981,color:#fff
```

### 5.2 Lineage Record JSON Schema

```json
{
  "schema_version": "1.0",
  "project_id": "medifl-proj-cxr-2026",
  "round_number": 42,
  "timestamp": "2026-08-03T10:15:32.847Z",
  
  "model_lineage": {
    "parent_model_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb924...",
    "current_model_hash": "sha256:9f86d081884c7d659a2feaa0c55ad015...",
    "model_architecture": "ResNet-50",
    "total_parameters": 23508032
  },
  
  "participating_nodes": [
    {
      "node_id": "hospital-alpha",
      "hospital_name": "Alpha Medical Center",
      "sample_count": 1250,
      "local_loss": 0.2841,
      "participation_signature": "0x8f3a2b1c...",
      "certificate_fingerprint": "SHA256:AB:CD:EF:..."
    },
    {
      "node_id": "hospital-beta",
      "hospital_name": "Beta Research Hospital",
      "sample_count": 890,
      "local_loss": 0.3102,
      "participation_signature": "0x3c1b7d9e...",
      "certificate_fingerprint": "SHA256:12:34:56:..."
    }
  ],
  
  "privacy_metrics": {
    "l2_clip_bound": 1.5,
    "noise_multiplier": 1.2,
    "round_epsilon_spent": 0.042,
    "cumulative_epsilon": 0.840,
    "delta": 1e-5,
    "budget_utilization_percent": 42.0
  },
  
  "validation_metrics": {
    "accuracy": 0.942,
    "auc_roc": 0.968,
    "f1_score": 0.938,
    "precision": 0.951,
    "recall": 0.926,
    "confusion_matrix": [[1200, 45], [38, 1150]]
  },
  
  "aggregation_config": {
    "algorithm": "FedAvg",
    "total_nodes_invited": 5,
    "nodes_responded": 4,
    "stragglers_dropped": 1,
    "aggregation_time_seconds": 12.4
  }
}
```

---

<div align="center">

| ← [Phase 7: System Architecture](./07_SYSTEM_ARCHITECTURE.md) | 📄 **Next Document** | [Phase 9: Database Design →](./09_DATABASE_DESIGN.md) |
|:---:|:---:|:---:|

---

*© 2026 MediFL Platform — Confidential & Proprietary*

</div>
