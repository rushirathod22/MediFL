<div align="center">

# 🎨 MediFL — UI/UX Design Guide

### 🏥 Design System, Component Library & Dashboard Wireframes

| **Document ID** | **Classification** | **Version** | **Status** |
|:---:|:---:|:---:|:---:|
| `MEDIFL-UX-012` | 🔒 Confidential | `v1.0.0` | ✅ Approved |

---

</div>

## 📑 Table of Contents

- [1. Design Principles](#1-design-principles)
- [2. Design Token System](#2-design-token-system)
- [3. Screen Layout Architecture](#3-screen-layout-architecture)
- [4. Key UI Components](#4-key-ui-components)

---

## 1. Design Principles

```mermaid
graph LR
    subgraph "🎨 MediFL Design Philosophy"
        P1["👁️ <b>Clinical Precision</b><br/><i>High-contrast data display<br/>Clear typographic hierarchy<br/>No visual noise</i>"]
        P2["⚡ <b>Real-Time Alive</b><br/><i>Live animated charts<br/>Pulsing node statuses<br/>Dynamic progress gauges</i>"]
        P3["🌙 <b>Dark Mode Default</b><br/><i>Reduces eye fatigue during<br/>prolonged monitoring sessions</i>"]
        P4["🔒 <b>Trust Signals</b><br/><i>Privacy budget always visible<br/>Audit trail accessible<br/>Compliance badges</i>"]
    end

    style P1 fill:#6366f1,color:#fff
    style P2 fill:#0ea5e9,color:#fff
    style P3 fill:#334155,color:#fff
    style P4 fill:#10b981,color:#fff
```

---

## 2. Design Token System

### 2.1 Color Palette

```mermaid
graph TD
    subgraph "🎨 MediFL Color System"
        direction LR
        
        subgraph Surfaces ["Surface Colors"]
            C1["<b>--bg-primary</b><br/>#0F172A<br/>██████<br/><i>Main background</i>"]
            C2["<b>--bg-surface</b><br/>#1E293B<br/>██████<br/><i>Card backgrounds</i>"]
            C3["<b>--bg-elevated</b><br/>#334155<br/>██████<br/><i>Modals, dropdowns</i>"]
        end
        
        subgraph Brand ["Brand Colors"]
            C4["<b>--brand-primary</b><br/>#0EA5E9<br/>██████<br/><i>Primary CTA, links</i>"]
            C5["<b>--brand-accent</b><br/>#6366F1<br/>██████<br/><i>Charts, progress bars</i>"]
            C6["<b>--brand-glow</b><br/>#8B5CF6<br/>██████<br/><i>Active highlights</i>"]
        end
        
        subgraph Status ["Status Colors"]
            C7["<b>--status-success</b><br/>#10B981<br/>██████<br/><i>Ready, completed</i>"]
            C8["<b>--status-warning</b><br/>#F59E0B<br/>██████<br/><i>Stragglers, ε ≥ 80%</i>"]
            C9["<b>--status-danger</b><br/>#EF4444<br/>██████<br/><i>Errors, budget exceeded</i>"]
        end
    end
```

### 2.2 Typography Scale

| Token | Size | Weight | Font Family | Usage |
|:---|:---:|:---:|:---|:---|
| `--text-display` | 2.5rem (40px) | Bold 700 | JetBrains Mono | Metric values, hero numbers |
| `--text-h1` | 2.25rem (36px) | Bold 700 | Inter | Page titles |
| `--text-h2` | 1.5rem (24px) | SemiBold 600 | Inter | Section headings |
| `--text-h3` | 1.125rem (18px) | Medium 500 | Inter | Card titles |
| `--text-body` | 0.875rem (14px) | Regular 400 | Inter | Body text, descriptions |
| `--text-caption` | 0.75rem (12px) | Regular 400 | Inter | Labels, timestamps |
| `--text-code` | 0.8125rem (13px) | Regular 400 | JetBrains Mono | Hashes, IDs, code |

---

## 3. Screen Layout Architecture

### 3.1 Main Dashboard Layout

```
╔══════════════════════════════════════════════════════════════════════════╗
║  🧠 MediFL  │  Dashboard  │  Projects  │  Nodes  │  Audit  │ 👤 Profile ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  📋 PROJECT: Multi-Center Chest X-Ray Campaign v1                      ║
║  Status: 🟢 ACTIVE (Round 14 / 50)   │   🔒 Privacy: ε = 0.584 / 2.0 ║
║                                                                        ║
╠═══════════════════════════════╦════════════════════════════════════════╣
║  📈 LIVE TRAINING TELEMETRY   ║  🏥 HOSPITAL NODE STATUS              ║
║                               ║                                        ║
║  ╭───────────────────────╮    ║  ┌──────────────────────────────────┐  ║
║  │ Loss   ╲              │    ║  │ ✅ Hospital Alpha   GPU: 87% ██▓ │  ║
║  │ 0.40    ╲             │    ║  │ ✅ Hospital Beta    GPU: 94% ███ │  ║
║  │ 0.20     ╲___         │    ║  │ ⚠️ Hospital Gamma  [STRAGGLER]  │  ║
║  │ 0.00         ╲___     │    ║  │ ✅ Hospital Delta   GPU: 72% ██▒ │  ║
║  │                   Acc  │    ║  │ ✅ Hospital Epsilon GPU: 88% ██▓ │  ║
║  │        Round 1 ... 14  │    ║  │ ❌ Hospital Zeta   [OFFLINE]    │  ║
║  ╰───────────────────────╯    ║  └──────────────────────────────────┘  ║
║                               ║                                        ║
╠═══════════════════════════════╩════════════════════════════════════════╣
║  🔒 PRIVACY BUDGET GAUGE              📊 ROUND METRICS SUMMARY       ║
║                                                                        ║
║  ╭──────────╮   ε Used: 29.2%         Accuracy:  93.4%  ↑ +0.3%      ║
║  │  ╱    ╲  │   ε Remaining: 70.8%    AUC-ROC:   96.1%  ↑ +0.1%      ║
║  │ │  29% │ │   Budget Status: 🟢     F1-Score:  92.8%  ↑ +0.4%      ║
║  │  ╲    ╱  │   Rounds Remaining: ~36  Loss:     0.241  ↓ -0.012     ║
║  ╰──────────╯                                                          ║
║                                                                        ║
╠════════════════════════════════════════════════════════════════════════╣
║  📋 AUDIT LOG & CHECKPOINT HISTORY                                     ║
║                                                                        ║
║  ▸ 10:15:32  Round 14 Aggregation Complete  │ Hash: sha256:9f86d0...  ║
║  ▸ 10:14:28  Hospital Gamma marked STRAGGLER │ Timeout: 600s           ║
║  ▸ 10:12:05  Round 14 Started               │ 6 nodes selected        ║
║  ▸ 10:11:30  Round 13 Checkpoint Saved      │ Val Acc: 93.1%          ║
╚════════════════════════════════════════════════════════════════════════╝
```

---

## 4. Key UI Components

### 4.1 Privacy Budget Gauge Component

```mermaid
graph TD
    subgraph "🔒 PrivacyBudgetGauge Component"
        direction TB
        
        Spec["<b>Component:</b> PrivacyBudgetGauge.tsx<br/><br/><b>Props:</b><br/>currentEpsilon: number<br/>maxEpsilon: number<br/>delta: number<br/><br/><b>Visual Behavior:</b><br/>• Circular arc rendering<br/>• Animated fill on update<br/>• Color transitions:<br/>  🟢 0-60%: Green (#10B981)<br/>  🟡 60-85%: Amber (#F59E0B) + pulse<br/>  🔴 85-100%: Red (#EF4444) + glow"]
    end

    style Spec fill:#1e293b,color:#e2e8f0
```

### 4.2 Node Health Card Component

```mermaid
graph LR
    subgraph "🏥 NodeHealthCard Component"
        Card["<b>Component:</b> NodeHealthCard.tsx<br/><br/><b>Displays:</b><br/>🏥 Hospital Name & Region<br/>📡 Connection Status (colored dot)<br/>🖥️ GPU Utilization (progress bar)<br/>💾 RAM Usage (progress bar)<br/>📊 Local Sample Count<br/>📜 Certificate Expiry Countdown<br/>⏱️ Last Heartbeat (relative time)<br/><br/><b>States:</b><br/>✅ READY — Green border<br/>🔄 TRAINING — Blue pulsing border<br/>⚠️ STRAGGLER — Amber flashing<br/>❌ OFFLINE — Red dimmed"]
    end

    style Card fill:#1e293b,color:#e2e8f0
```

---

<div align="center">

| ← [Phase 11: Security](./11_SECURITY_ARCHITECTURE.md) | 📄 **Next Document** | [Phase 13: Deployment →](./13_DEPLOYMENT_ARCHITECTURE.md) |
|:---:|:---:|:---:|

---

*© 2026 MediFL Platform — Confidential & Proprietary*

</div>
