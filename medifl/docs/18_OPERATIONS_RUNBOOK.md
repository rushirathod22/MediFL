<div align="center">

# 🔧 MediFL — Operations Runbook

### 🏥 Monitoring, Alerting & Incident Response Procedures

| **Document ID** | `MEDIFL-OPS-018` | **Version** | `v1.0.0` | **Status** | ✅ Approved |
|:---:|:---:|:---:|:---:|:---:|:---:|

---

</div>

## 1. Monitoring Stack Architecture

```mermaid
graph LR
    subgraph "📊 MediFL Observability Stack"
        Pods["🐳 MediFL Pods<br/>& Edge Nodes"]
        -->|"/metrics"| Prom["📊 <b>Prometheus</b><br/><i>Metric scraping<br/>15s intervals</i>"]
        -->|"PromQL"| Graf["📈 <b>Grafana</b><br/><i>Dashboards<br/>SLA tracking</i>"]
        
        Prom -->|"Alert Rules"| Alert["🚨 <b>Alertmanager</b><br/><i>PagerDuty<br/>Slack #medifl-ops</i>"]
        
        Pods -->|"Structured Logs"| Loki["📝 <b>Loki</b><br/><i>Log aggregation<br/>LogQL search</i>"]
        --> Graf
    end

    style Prom fill:#e6522c,color:#fff
    style Graf fill:#f46800,color:#fff
    style Alert fill:#ef4444,color:#fff
    style Loki fill:#f46800,color:#fff
```

## 2. Critical Alert Rules

| Alert Name | Condition | Severity | Response SLA |
|:---|:---|:---:|:---:|
| 🔴 `AggregatorOOM` | Container memory > 90% | Critical | ⏱️ 5 min |
| 🔴 `PostgreSQLDown` | DB connection failures > 10/min | Critical | ⏱️ 5 min |
| 🟠 `PrivacyBudgetHigh` | $\epsilon / \epsilon_{max} \ge 85\%$ | High | ⏱️ 15 min |
| 🟠 `HighNodeDropout` | Dropout rate > 30% over 5 min | High | ⏱️ 15 min |
| 🟡 `RoundStalled` | Round in COLLECTING > 10 min | Warning | ⏱️ 30 min |
| 🟡 `CertExpiryWarning` | Node cert expires in < 7 days | Warning | ⏱️ 24 hours |

## 3. Incident Response SOPs

### SOP-101: Straggler Node Recovery

```mermaid
graph TD
    Detect["🚨 Alert: Round Stalled<br/><i>3 nodes not responding</i>"]
    --> Check["🔍 Check node heartbeats<br/><code>kubectl logs medifl-aggregator</code>"]
    --> Decision{{"Node recoverable?"}}
    Decision -->|"Yes"| Retry["🔄 Wait for timeout T_max<br/><i>Node excluded automatically</i>"]
    Decision -->|"No"| Skip["⏭️ Force-skip node<br/><code>medifl-admin rounds skip-node</code>"]
    Retry & Skip --> Continue["✅ Round proceeds<br/><i>Aggregate with available updates</i>"]

    style Detect fill:#ef4444,color:#fff
    style Continue fill:#10b981,color:#fff
```

### SOP-102: Privacy Budget Exhaustion

> [!CAUTION]
> This is a **critical compliance event**. Follow these steps immediately:

1. **Pause** the FL campaign: `POST /api/v1/projects/{id}/pause`
2. **Notify** Lead AI Scientist and CISO within 15 minutes
3. **Review** RDP budget logs in database
4. **Decision**: Extend budget (CISO approval required) or terminate experiment

---

<div align="center">

| ← [Phase 17: Installation](./17_INSTALLATION_GUIDE.md) | 📄 **Next** | [Phase 19: Developer Guide →](./19_DEVELOPER_GUIDE.md) |
|:---:|:---:|:---:|

*© 2026 MediFL Platform — Confidential & Proprietary*

</div>
