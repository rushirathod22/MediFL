<div align="center">

# ⚙️ MediFL — DevOps & CI/CD Guide

### 🏥 GitHub Actions, GitOps (ArgoCD) & Automated Quality Gates

| **Document ID** | `MEDIFL-DEVOPS-014` | **Version** | `v1.0.0` | **Status** | ✅ Approved |
|:---:|:---:|:---:|:---:|:---:|:---:|

---

</div>

## 1. CI/CD Pipeline Architecture

```mermaid
graph TD
    subgraph "🔄 MediFL CI/CD Pipeline"
        direction TB
        
        Trigger["👨‍💻 <b>Developer Push</b><br/><i>PR to main branch</i>"]
        
        subgraph CI ["🔍 Continuous Integration (GitHub Actions)"]
            Lint["📝 <b>Code Quality</b><br/><i>Ruff linting<br/>Mypy type checking<br/>Black formatting</i>"]
            Test["🧪 <b>Automated Testing</b><br/><i>PyTest unit tests<br/>Integration tests<br/>Coverage report</i>"]
            Security["🛡️ <b>Security Scanning</b><br/><i>Trivy CVE scan<br/>Snyk dependency check<br/>SAST analysis</i>"]
            Build["🐳 <b>Docker Build</b><br/><i>Multi-stage build<br/>Image layer caching<br/>Tag with SHA</i>"]
        end

        subgraph CD ["🚀 Continuous Delivery (ArgoCD GitOps)"]
            Push["📦 <b>Push to Registry</b><br/><i>Amazon ECR<br/>Signed image</i>"]
            GitOps["📋 <b>Update K8s Manifests</b><br/><i>GitOps infra repo<br/>Image tag update</i>"]
            Sync["☸️ <b>ArgoCD Sync</b><br/><i>Auto-sync to cluster<br/>Health probe check</i>"]
            Smoke["✅ <b>Smoke Tests</b><br/><i>/healthz endpoint<br/>gRPC connectivity</i>"]
        end

        Trigger --> Lint --> Test
        Lint --> Security
        Test & Security --> Build --> Push --> GitOps --> Sync --> Smoke
    end

    style CI fill:#eff6ff,stroke:#3b82f6,stroke-width:2px
    style CD fill:#f0fdf4,stroke:#16a34a,stroke-width:2px
```

## 2. GitHub Actions Workflow (`ci-cd.yml`)

```yaml
name: MediFL Enterprise CI/CD Pipeline

on:
  push:
    branches: [main, release/*]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    name: 📝 Code Quality & 🧪 Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11', cache: 'pip' }
      - run: pip install ruff mypy pytest pytest-cov
      - run: ruff check ./src
      - run: mypy ./src --strict
      - run: pytest --cov=src --cov-report=xml tests/

  security-scan:
    name: 🛡️ Vulnerability Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@master
        with: { scan-type: 'fs', severity: 'CRITICAL,HIGH' }

  build-and-push:
    name: 🐳 Build & Push
    needs: [lint-and-test, security-scan]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/amazon-ecr-login@v2
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ${{ steps.ecr.outputs.registry }}/medifl-api:${{ github.sha }}
```

## 3. Environment Promotion Strategy

```mermaid
graph LR
    Dev["🟢 <b>Development</b><br/><i>Auto-deploy on PR merge<br/>Feature branch testing</i>"]
    -->|"Auto-sync"| Staging["🟡 <b>Staging</b><br/><i>Integration test suite<br/>Performance benchmarks</i>"]
    -->|"2-person approval"| Prod["🔴 <b>Production</b><br/><i>Blue/Green deployment<br/>Canary rollout</i>"]

    style Dev fill:#10b981,color:#fff
    style Staging fill:#f59e0b,color:#fff
    style Prod fill:#ef4444,color:#fff
```

---

<div align="center">

| ← [Phase 13: Deployment](./13_DEPLOYMENT_ARCHITECTURE.md) | 📄 **Next** | [Phase 15: Test Plan →](./15_TEST_PLAN.md) |
|:---:|:---:|:---:|

*© 2026 MediFL Platform — Confidential & Proprietary*

</div>
