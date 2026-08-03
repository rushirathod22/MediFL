<div align="center">

# 🛡️ MediFL — Security Architecture Document

### 🏥 Zero Trust Model, mTLS, Differential Privacy & STRIDE Threat Analysis

| **Document ID** | **Classification** | **Version** | **Status** |
|:---:|:---:|:---:|:---:|
| `MEDIFL-SEC-011` | 🔴 Highly Confidential | `v1.0.0` | ✅ Approved |

---

</div>

## 📑 Table of Contents

- [1. Zero Trust Security Architecture](#1-zero-trust-security-architecture)
- [2. Authentication & Identity Architecture](#2-authentication--identity-architecture)
- [3. Cryptographic Key Management](#3-cryptographic-key-management)
- [4. STRIDE Threat Analysis & Defense Matrix](#4-stride-threat-analysis--defense-matrix)
- [5. Data Protection & Privacy Boundaries](#5-data-protection--privacy-boundaries)

---

## 1. Zero Trust Security Architecture

> [!CAUTION]
> MediFL processes privacy-sensitive medical AI model updates derived from Protected Health Information (PHI). **Every component operates under Zero Trust** — no implicit trust based on network location, and every request is authenticated, authorized, and encrypted.

```mermaid
graph TD
    subgraph "🏥 Hospital Intranet (PHI Zone)"
        PACS["💾 Hospital PACS<br/><i>DICOM Patient Imaging</i>"]
        EHR["📋 Hospital EHR<br/><i>Clinical Records</i>"]
        Agent["🐳 <b>MediFL Edge Agent</b><br/><i>Isolated Docker container<br/>Read-only data access<br/>No persistent storage<br/>GPU-accelerated training</i>"]
        
        PACS -->|"🔒 Read-Only<br/>RAM Only"| Agent
        EHR -->|"🔒 Read-Only<br/>RAM Only"| Agent
    end

    subgraph "🌐 Network Security Perimeter"
        FW["🧱 <b>Hospital Firewall</b><br/><i>Outbound-only rules<br/>No inbound ports opened</i>"]
        WAF["🛡️ <b>AWS WAF</b><br/><i>DDoS protection<br/>IP allowlisting<br/>Request inspection</i>"]
    end

    subgraph "☁️ MediFL Zero Trust Cloud"
        GW["🚪 <b>Envoy mTLS Gateway</b><br/><i>X.509 client cert validation<br/>JWT token verification<br/>Certificate pinning<br/>Rate limiting</i>"]
        PKI["🔐 <b>Vault PKI CA</b><br/><i>Certificate issuance<br/>CRL management<br/>Auto-rotation (30-day)</i>"]
        Secrets["🔑 <b>HashiCorp Vault</b><br/><i>Dynamic secrets<br/>DB credential rotation<br/>Encryption-as-a-Service</i>"]
        Core["⚙️ <b>Core Services</b><br/><i>Namespace isolation<br/>Read-only filesystem<br/>Dropped Linux capabilities<br/>Non-root containers</i>"]
        HSM["🔐 <b>Cloud HSM</b><br/><i>FIPS 140-2 Level 3<br/>Aggregation encryption keys<br/>Never extracted</i>"]
    end

    Agent -->|"1️⃣ Outbound mTLS<br/>(Client Cert + Server Cert)"| FW
    FW -->|"2️⃣ Encrypted TLS 1.3<br/>(AES-256-GCM)"| WAF
    WAF -->|"3️⃣ Validated Request"| GW
    GW <-->|"4️⃣ Verify Cert Chain"| PKI
    GW -->|"5️⃣ Authenticated"| Core
    Core <--> Secrets
    Core <--> HSM

    style Agent fill:#10b981,color:#fff
    style GW fill:#ef4444,color:#fff
    style PKI fill:#6366f1,color:#fff
    style Secrets fill:#f59e0b,color:#fff
    style HSM fill:#8b5cf6,color:#fff
```

---

## 2. Authentication & Identity Architecture

### 2.1 Dual Authentication Model

```mermaid
graph LR
    subgraph "🔐 MediFL Dual Authentication"
        direction TB
        
        subgraph Human ["👤 Human User Authentication"]
            Login["👤 User Login<br/><i>Email + Password</i>"]
            -->MFA["🔑 Multi-Factor Auth<br/><i>TOTP / WebAuthn</i>"]
            -->OIDC["🎫 OIDC Token Exchange<br/><i>Keycloak issues JWT</i>"]
            -->JWT["📋 JWT Access Token<br/><i>60-min expiry<br/>Contains: user_id, role,<br/>permissions, iss, exp</i>"]
        end

        subgraph Machine ["🤖 Machine (Edge Node) Authentication"]
            Cert["📜 X.509 Client Certificate<br/><i>Issued by MediFL Vault CA<br/>30-day validity</i>"]
            -->TLS["🤝 mTLS Handshake<br/><i>Mutual certificate exchange<br/>TLS 1.3 negotiation</i>"]
            -->Verify["✅ Certificate Validation<br/><i>Chain verification<br/>CRL check<br/>Fingerprint DB lookup</i>"]
            -->Session["🔗 Authenticated gRPC Session<br/><i>Persistent bidirectional<br/>stream established</i>"]
        end
    end

    style Human fill:#eff6ff,stroke:#3b82f6,stroke-width:2px
    style Machine fill:#f0fdf4,stroke:#16a34a,stroke-width:2px
```

### 2.2 RBAC Permission Matrix

| Permission | 🔴 ADMIN | 🟡 RESEARCHER | 🔵 COMPLIANCE_OFFICER |
|:---|:---:|:---:|:---:|
| Create / Delete Users | ✅ | ❌ | ❌ |
| Create / Configure FL Projects | ✅ | ✅ | ❌ |
| Start / Pause Training Rounds | ✅ | ✅ | ❌ |
| Register Hospital Nodes | ✅ | ❌ | ❌ |
| Revoke Node Certificates | ✅ | ❌ | ❌ |
| View Training Metrics & Dashboard | ✅ | ✅ | ✅ |
| View Audit Logs & Privacy Reports | ✅ | ✅ | ✅ |
| Export Compliance Audit PDF | ✅ | ❌ | ✅ |
| Modify Privacy Budget Limits | ✅ | ❌ | ❌ |

---

## 3. Cryptographic Key Management

```mermaid
graph TD
    subgraph "🔐 Cryptographic Key Hierarchy"
        direction TB
        
        Root["🔑 <b>Root CA Key</b><br/><i>Stored in CloudHSM<br/>FIPS 140-2 Level 3<br/>Never exported<br/>4096-bit RSA</i>"]
        
        Root --> IntCA["🔑 <b>Intermediate CA Key</b><br/><i>Vault PKI mount<br/>2048-bit RSA<br/>2-year validity</i>"]
        
        IntCA --> ServerCert["📜 <b>Server TLS Certificate</b><br/><i>*.medifl.health<br/>90-day auto-renewal<br/>Let's Encrypt / Vault</i>"]
        
        IntCA --> ClientCert["📜 <b>Client Certificates</b><br/><i>Per hospital node<br/>30-day validity<br/>Auto-rotated by agent</i>"]
        
        Root --> JWTKey["🔑 <b>JWT Signing Key</b><br/><i>RS256 (RSA 2048-bit)<br/>Vault transit engine<br/>Rotated monthly</i>"]
        
        Root --> DBKey["🔑 <b>Database Encryption Key</b><br/><i>AES-256 TDE<br/>Vault transit engine<br/>Rotated quarterly</i>"]
    end

    style Root fill:#7f1d1d,color:#fff
    style IntCA fill:#ef4444,color:#fff
    style ServerCert fill:#0ea5e9,color:#fff
    style ClientCert fill:#10b981,color:#fff
    style JWTKey fill:#6366f1,color:#fff
    style DBKey fill:#f59e0b,color:#fff
```

---

## 4. STRIDE Threat Analysis & Defense Matrix

```mermaid
graph TD
    subgraph "🛡️ STRIDE Threat Model — MediFL"
        direction TB
        
        S["<b>S</b>poofing<br/><i>Rogue node pretends<br/>to be a hospital</i>"]
        T["<b>T</b>ampering<br/><i>MITM alters gradient<br/>tensors in transit</i>"]
        R["<b>R</b>epudiation<br/><i>Hospital denies<br/>round participation</i>"]
        I["<b>I</b>nformation Disclosure<br/><i>Gradient inversion<br/>reconstructs images</i>"]
        D["<b>D</b>enial of Service<br/><i>Malicious oversized<br/>tensor payload</i>"]
        E["<b>E</b>levation of Privilege<br/><i>Web user accesses<br/>admin DB credentials</i>"]
    end

    style S fill:#ef4444,color:#fff
    style T fill:#f59e0b,color:#fff
    style R fill:#eab308,color:#fff
    style I fill:#6366f1,color:#fff
    style D fill:#0ea5e9,color:#fff
    style E fill:#8b5cf6,color:#fff
```

| STRIDE Category | Threat | Severity | Defense Control |
|:---|:---|:---:|:---|
| **🔴 Spoofing** | Rogue node masquerades as hospital participant | Critical | ✅ mTLS X.509 client cert binding + API key HMAC |
| **🟠 Tampering** | Man-in-the-middle alters tensor in transit | Critical | ✅ TLS 1.3 AES-256-GCM + SHA-256 per-chunk hash verification |
| **🟡 Repudiation** | Hospital denies participation in FL round | High | ✅ Immutable audit log with cryptographic node signature |
| **🔵 Info Disclosure** | Gradient Inversion Attack (DLG/iDLG) | Critical | ✅ DP-SGD noise ($\epsilon \le 2.0$) + Homomorphic Encryption |
| **⚪ DoS** | Oversized corrupt tensor exhausts server memory | High | ✅ gRPC max payload 500 MB + rate limiting + node timeout |
| **🟣 Privilege Escalation** | Compromised user accesses admin secrets | High | ✅ RBAC enforcement + Vault dynamic secrets + least privilege |

---

## 5. Data Protection & Privacy Boundaries

```mermaid
graph TB
    subgraph "🔒 MediFL Data Classification & Protection Boundaries"
        direction TB
        
        subgraph RED ["🔴 RESTRICTED — Never Leaves Hospital"]
            D1["Raw DICOM Images"]
            D2["Patient EHR Records"]
            D3["Personal Identifiers (PHI)"]
        end

        subgraph AMBER ["🟠 CONFIDENTIAL — Encrypted in Transit"]
            D4["DP-Noised Gradient Updates"]
            D5["Local Training Metrics"]
            D6["Node Hardware Specs"]
        end

        subgraph GREEN ["🟢 INTERNAL — Stored in Central DB"]
            D7["Aggregated Global Model Weights"]
            D8["Round Metrics & Audit Logs"]
            D9["User Accounts & Project Config"]
        end
    end

    RED -.->|"❌ NEVER<br/>TRANSMITTED"| AMBER
    AMBER -->|"🔒 mTLS + DP<br/>Encrypted"| GREEN

    style RED fill:#7f1d1d,color:#fff,stroke:#ef4444,stroke-width:3px
    style AMBER fill:#78350f,color:#fff,stroke:#f59e0b,stroke-width:3px
    style GREEN fill:#14532d,color:#fff,stroke:#10b981,stroke-width:3px
```

---

<div align="center">

| ← [Phase 10: API Specification](./10_API_SPECIFICATION.md) | 📄 **Next Document** | [Phase 12: UI/UX Design Guide →](./12_UI_UX_DESIGN_GUIDE.md) |
|:---:|:---:|:---:|

---

*© 2026 MediFL Platform — Confidential & Proprietary*

</div>
