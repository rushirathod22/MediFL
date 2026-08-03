<div align="center">

# 📡 MediFL — API Specification Document

### 🏥 REST (OpenAPI 3.0), gRPC (Protocol Buffers) & WebSocket Events

| **Document ID** | **Classification** | **Version** | **Status** |
|:---:|:---:|:---:|:---:|
| `MEDIFL-API-010` | 🔒 Confidential | `v1.0.0` | ✅ Approved |

---

</div>

## 📑 Table of Contents

- [1. API Architecture Overview](#1-api-architecture-overview)
- [2. REST API Endpoints (OpenAPI 3.0)](#2-rest-api-endpoints-openapi-30)
- [3. gRPC Service Definition (Protocol Buffers)](#3-grpc-service-definition-protocol-buffers)
- [4. WebSocket Real-Time Telemetry](#4-websocket-real-time-telemetry)

---

## 1. API Architecture Overview

```mermaid
graph TB
    subgraph "🌐 MediFL API Gateway Architecture"
        direction TB
        
        subgraph Clients ["📱 API Consumers"]
            Web["🖥️ Web Dashboard<br/><i>React SPA</i>"]
            CLI["⌨️ Admin CLI<br/><i>Python CLI Tool</i>"]
            Edge["🏥 Edge Agents<br/><i>Hospital Nodes</i>"]
        end

        subgraph Gateway ["🚪 Envoy API Gateway (Port 443)"]
            Auth["🔐 JWT / mTLS<br/>Validation"]
            Rate["⚡ Rate Limiter<br/><i>100 req/s per IP</i>"]
            Route["🔀 Request Router"]
        end

        subgraph APIs ["📡 API Services"]
            REST["🔗 <b>REST API</b><br/><i>FastAPI (Port 8000)<br/>JSON over HTTPS<br/>OpenAPI 3.0 spec</i>"]
            GRPC["📡 <b>gRPC Service</b><br/><i>Aggregator (Port 50051)<br/>Protobuf over HTTP/2<br/>Bidirectional streaming</i>"]
            WSS["📊 <b>WebSocket</b><br/><i>Telemetry (Port 8001)<br/>JSON events over WSS<br/>Real-time broadcasting</i>"]
        end

        Web -->|"HTTPS"| Gateway
        CLI -->|"HTTPS"| Gateway
        Edge -->|"gRPC/mTLS"| Gateway
        
        Gateway --> REST
        Gateway --> GRPC
        Gateway --> WSS
    end

    style REST fill:#0ea5e9,color:#fff
    style GRPC fill:#6366f1,color:#fff
    style WSS fill:#10b981,color:#fff
```

---

## 2. REST API Endpoints (OpenAPI 3.0)

**Base URL:** `https://api.medifl.health/api/v1`

### 2.1 Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|:---:|:---|:---|:---:|
| `POST` | `/auth/login` | Authenticate user, return JWT access + refresh tokens | ❌ Public |
| `POST` | `/auth/refresh` | Refresh expired JWT access token | 🔑 Refresh Token |
| `POST` | `/auth/logout` | Invalidate current session tokens | 🔑 JWT |

### 2.2 Project Management Endpoints

| Method | Endpoint | Description | Auth Required |
|:---:|:---|:---|:---:|
| `POST` | `/projects` | Create new FL campaign project | 🔑 RESEARCHER+ |
| `GET` | `/projects` | List all projects (paginated) | 🔑 Any Role |
| `GET` | `/projects/{id}` | Get project details with latest round metrics | 🔑 Any Role |
| `PATCH` | `/projects/{id}` | Update project settings (hyperparams, DP config) | 🔑 RESEARCHER+ |
| `POST` | `/projects/{id}/model` | Upload model architecture file (.py / .onnx) | 🔑 RESEARCHER+ |
| `POST` | `/projects/{id}/start-round` | Trigger the next training round | 🔑 RESEARCHER+ |
| `POST` | `/projects/{id}/pause` | Pause active training | 🔑 ADMIN |

#### 📋 Create Project — Request/Response Example

```http
POST /api/v1/projects HTTP/1.1
Host: api.medifl.health
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
Content-Type: application/json

{
  "title": "Multi-Center Chest X-Ray Pneumonia Model",
  "description": "Federated ResNet-50 training across 10 hospital centers for pneumonia detection.",
  "target_domain": "CHEST_RADIOLOGY",
  "model_architecture": "ResNet50",
  "hyperparameters": {
    "total_rounds": 50,
    "local_epochs": 3,
    "batch_size": 32,
    "learning_rate": 0.001,
    "optimizer": "AdamW",
    "aggregation_algorithm": "FedAvg",
    "min_nodes_per_round": 5,
    "straggler_timeout_seconds": 600
  },
  "dp_config": {
    "enabled": true,
    "l2_clip_norm": 1.5,
    "noise_multiplier": 1.2,
    "max_epsilon": 2.0,
    "delta": 1e-5
  }
}
```

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "project_id": "a8c909e4-3b1a-4d76-8f3a-129482701b2a",
  "status": "CREATED",
  "model_architecture": "ResNet50",
  "dp_enabled": true,
  "max_epsilon": 2.0,
  "created_at": "2026-08-03T10:00:00Z",
  "links": {
    "self": "/api/v1/projects/a8c909e4-3b1a-4d76-8f3a-129482701b2a",
    "start_round": "/api/v1/projects/a8c909e4-3b1a-4d76-8f3a-129482701b2a/start-round",
    "nodes": "/api/v1/projects/a8c909e4-3b1a-4d76-8f3a-129482701b2a/nodes"
  }
}
```

### 2.3 Error Response Format

> [!NOTE]
> All API errors follow [RFC 7807 Problem Details](https://tools.ietf.org/html/rfc7807) standard format.

```json
{
  "type": "https://api.medifl.health/errors/privacy-budget-exhausted",
  "title": "Privacy Budget Exhausted",
  "status": 409,
  "detail": "Cumulative epsilon (2.04) exceeds maximum allowed budget (2.0). Experiment auto-terminated.",
  "instance": "/api/v1/projects/a8c909e4/start-round",
  "extensions": {
    "current_epsilon": 2.04,
    "max_epsilon": 2.0,
    "last_round_completed": 42
  }
}
```

---

## 3. gRPC Service Definition (Protocol Buffers)

### 3.1 Service Architecture

```mermaid
graph LR
    subgraph "📡 gRPC Edge Node Service (Port 50051)"
        direction TB
        
        KA["💓 <b>KeepAlive</b><br/><i>Bidirectional Stream<br/>Edge ↔ Server<br/>Heartbeat + Commands</i>"]
        
        DW["📥 <b>DownloadWeights</b><br/><i>Server Streaming<br/>Server → Edge<br/>Chunked W_t download</i>"]
        
        UU["📤 <b>UploadUpdate</b><br/><i>Client Streaming<br/>Edge → Server<br/>Chunked ΔW upload</i>"]
    end

    style KA fill:#10b981,color:#fff
    style DW fill:#0ea5e9,color:#fff
    style UU fill:#6366f1,color:#fff
```

### 3.2 Protocol Buffer Definition (`medifl_service.proto`)

```protobuf
syntax = "proto3";
package medifl.v1;

option go_package = "github.com/medifl/proto/v1;mediflv1";

// ============================================================
// MediFL Edge Node Communication Service
// ============================================================

service EdgeNodeService {
  // Bidirectional heartbeat stream for keepalive & server commands
  rpc KeepAlive(stream HeartbeatRequest) returns (stream HeartbeatResponse);
  
  // Server-streaming: Download global model weights for round t
  rpc DownloadWeights(WeightDownloadRequest) returns (stream WeightChunk);
  
  // Client-streaming: Upload encrypted gradient updates for round t  
  rpc UploadUpdate(stream UpdateChunk) returns (UploadResponse);
}

// ============================================================
// Message Definitions
// ============================================================

message HeartbeatRequest {
  string node_id = 1;
  string status = 2;          // READY, TRAINING, ERROR
  float gpu_utilization = 3;   // 0.0 - 100.0%
  int64 ram_free_bytes = 4;
  string cuda_version = 5;
  int32 gpu_count = 6;
}

message HeartbeatResponse {
  string command = 1;          // WAIT, START_TRAINING, STOP, REBOOT
  string active_round_id = 2;
  bytes hyperparameters_json = 3;
}

message WeightDownloadRequest {
  string round_id = 1;
  string node_id = 2;
  string requested_format = 3; // pytorch, safetensors
}

message WeightChunk {
  int32 chunk_index = 1;
  int32 total_chunks = 2;
  bytes data_buffer = 3;       // Raw binary tensor data
  string sha256_checksum = 4;  // Per-chunk integrity hash
}

message UpdateChunk {
  string round_id = 1;
  string node_id = 2;
  int32 sample_count = 3;
  float local_loss = 4;
  float local_accuracy = 5;
  int32 chunk_index = 6;
  int32 total_chunks = 7;
  bytes encrypted_tensor_payload = 8;
  string sha256_checksum = 9;
}

message UploadResponse {
  bool success = 1;
  string message = 2;
  int64 bytes_received = 3;
  string server_computed_hash = 4;
}
```

---

## 4. WebSocket Real-Time Telemetry

**URL:** `wss://api.medifl.health/ws/telemetry/{project_id}?token=<JWT>`

### 4.1 Event Types & Payloads

| Event Type | Direction | Description |
|:---|:---:|:---|
| `ROUND_STARTED` | Server → Client | New round initiated, broadcasting weights |
| `NODE_STATUS_UPDATE` | Server → Client | Hospital node changed status (READY, TRAINING, STRAGGLER) |
| `ROUND_PROGRESS` | Server → Client | Aggregation metrics update (loss, accuracy, ε) |
| `ROUND_COMPLETED` | Server → Client | Round finished, checkpoint saved |
| `PRIVACY_ALERT` | Server → Client | Privacy budget threshold exceeded |

### 4.2 Sample Event Payload

```json
{
  "event": "ROUND_PROGRESS",
  "timestamp": "2026-08-03T10:15:32.847Z",
  "payload": {
    "project_id": "a8c909e4-3b1a-4d76-8f3a-129482701b2a",
    "round_number": 14,
    "total_rounds": 50,
    "status": "AGGREGATING",
    "nodes": {
      "invited": 10,
      "submitted": 8,
      "stragglers": 1,
      "rejected": 1
    },
    "metrics": {
      "training_loss": 0.2415,
      "validation_accuracy": 0.9340,
      "validation_auc_roc": 0.9612,
      "validation_f1_score": 0.9280
    },
    "privacy": {
      "round_epsilon_spent": 0.042,
      "cumulative_epsilon": 0.584,
      "max_epsilon": 2.0,
      "budget_utilization_percent": 29.2,
      "delta": 1e-5
    }
  }
}
```

---

<div align="center">

| ← [Phase 9: Database Design](./09_DATABASE_DESIGN.md) | 📄 **Next Document** | [Phase 11: Security Architecture →](./11_SECURITY_ARCHITECTURE.md) |
|:---:|:---:|:---:|

---

*© 2026 MediFL Platform — Confidential & Proprietary*

</div>
