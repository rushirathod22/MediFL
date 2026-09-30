# 🧠 MediFL — Step-by-Step Build Guide (Learn by Doing)

> This guide walks you through building the entire MediFL platform from scratch. Each step tells you **what to do**, **why**, and gives you **only the code you need** for that step. Follow in order!

---

## 📋 Overview: What You'll Build

| # | Phase | What You Build |
|---|-------|---------------|
| 1 | **Setup** | Project structure, virtual env, dependencies |
| 2 | **Database** | PostgreSQL schema with SQLAlchemy models |
| 3 | **Backend API** | FastAPI server with REST endpoints |
| 4 | **FL Core** | Federated Averaging (FedAvg) aggregation engine |
| 5 | **Differential Privacy** | DP-SGD noise injection + privacy accounting |
| 6 | **Edge Agent** | Hospital-side training client |
| 7 | **gRPC Communication** | Secure server↔edge communication |
| 8 | **Real-Time Dashboard** | React frontend with live metrics |
| 9 | **Security** | mTLS, JWT auth, audit logging |
| 10 | **Docker & Deployment** | Containerization + Docker Compose |

---

## 🔰 Prerequisites

Before starting, install these on your machine:

| Tool | Version | Why You Need It |
|------|---------|-----------------|
| **Python** | 3.11+ | Backend + AI code |
| **Node.js** | 18+ | Frontend (React) |
| **PostgreSQL** | 15+ | Database |
| **Redis** | 7+ | Caching + Pub/Sub |
| **Docker** | Latest | Containerization |
| **Git** | Latest | Version control |

---

---

# PHASE 1: Project Setup 🏗️

### What you learn: Project structure, virtual environments, dependency management

---

### Step 1.1 — Create the folder structure

Open your terminal in the `medifl` folder and run:

```bash
# Create all the directories
mkdir -p src/server/api
mkdir -p src/server/core
mkdir -p src/server/models
mkdir -p src/server/services
mkdir -p src/server/grpc_service
mkdir -p src/aggregator
mkdir -p src/edge_agent
mkdir -p src/common
mkdir -p frontend
mkdir -p proto
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p docker
mkdir -p config
```

**Your folder tree should look like this:**
```
medifl/
├── src/
│   ├── server/          ← FastAPI backend
│   │   ├── api/         ← REST route handlers
│   │   ├── core/        ← Config, security, DB setup
│   │   ├── models/      ← SQLAlchemy ORM models
│   │   ├── services/    ← Business logic layer
│   │   └── grpc_service/ ← gRPC server
│   ├── aggregator/      ← FedAvg, FedProx engines
│   ├── edge_agent/      ← Hospital-side training code
│   └── common/          ← Shared utilities
├── frontend/            ← React dashboard
├── proto/               ← Protocol Buffers definitions
├── tests/               ← Unit + integration tests
├── docker/              ← Dockerfiles
├── config/              ← YAML config files
├── docs/                ← (already exists)
└── README.md            ← (already exists)
```

> **💡 Why this structure?** Each folder maps to a **microservice** from your HLD doc. Keeping them separate makes testing and deployment easier.

---

### Step 1.2 — Create a Python virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Activate it (Mac/Linux)
# source venv/bin/activate
```

---

### Step 1.3 — Install Python dependencies

Create a file `requirements.txt` in the root folder:

```txt
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.2
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.13.0

# Redis
redis==5.0.1

# AI / ML
torch==2.1.1
opacus==1.4.0

# gRPC
grpcio==1.60.0
grpcio-tools==1.60.0
protobuf==4.25.1

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Utilities
python-dotenv==1.0.0
loguru==0.7.2
httpx==0.25.2
```

Install them:

```bash
pip install -r requirements.txt
```

---

### Step 1.4 — Create the config file

Create `config/settings.yaml`:

```yaml
# MediFL Configuration
app:
  name: "MediFL"
  version: "0.1.0"
  debug: true

database:
  url: "postgresql+asyncpg://medifl:medifl_pass@localhost:5432/medifl_db"
  pool_size: 10

redis:
  url: "redis://localhost:6379/0"

security:
  secret_key: "your-super-secret-key-change-in-production"
  algorithm: "HS256"
  access_token_expire_minutes: 30

federated_learning:
  min_nodes: 2
  max_rounds: 100
  default_strategy: "fedavg"
  dp_enabled: true
  clip_norm: 1.0
  noise_multiplier: 0.1
  target_epsilon: 8.0
  target_delta: 0.00001
```

Create `src/server/core/config.py` to load it:

```python
"""
Application configuration - loads settings from YAML and environment variables.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central config class. Values come from .env or environment variables."""

    # App
    APP_NAME: str = "MediFL"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://medifl:medifl_pass@localhost:5432/medifl_db"
    DB_POOL_SIZE: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Federated Learning
    MIN_NODES: int = 2
    MAX_ROUNDS: int = 100
    DEFAULT_STRATEGY: str = "fedavg"
    DP_ENABLED: bool = True
    CLIP_NORM: float = 1.0
    NOISE_MULTIPLIER: float = 0.1
    TARGET_EPSILON: float = 8.0
    TARGET_DELTA: float = 1e-5

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance - import this everywhere
settings = Settings()
```

Create a `.env` file in the project root:

```env
APP_NAME=MediFL
DEBUG=True
DATABASE_URL=postgresql+asyncpg://medifl:medifl_pass@localhost:5432/medifl_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-super-secret-key-change-in-production
```

> **✅ Checkpoint:** Run `python -c "from src.server.core.config import settings; print(settings.APP_NAME)"` — it should print `MediFL`.

---

---

# PHASE 2: Database Layer 🐘

### What you learn: SQLAlchemy ORM, async database, data modeling

---

### Step 2.1 — Set up PostgreSQL

```bash
# Create the database (run in psql or pgAdmin)
CREATE USER medifl WITH PASSWORD 'medifl_pass';
CREATE DATABASE medifl_db OWNER medifl;
GRANT ALL PRIVILEGES ON DATABASE medifl_db TO medifl;
```

---

### Step 2.2 — Create the database connection

Create `src/server/core/database.py`:

```python
"""
Async database engine and session factory.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.server.core.config import settings


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    echo=settings.DEBUG,  # Logs SQL queries when debug=True
)

# Session factory - creates new DB sessions
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Base class for all ORM models
class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency - yields a DB session per request."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

> **💡 Why async?** Healthcare platforms handle many concurrent requests. Async DB means one request doesn't block another.

---

### Step 2.3 — Create ORM models

These map directly to the tables in your [Database Design doc](file:///c:/CS(AI) Enginering/TY/Indurstry_project/medifl/docs/09_DATABASE_DESIGN.md).

Create `src/server/models/user.py`:

```python
"""
User model - represents platform users (admins, researchers, IT staff).
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.server.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(50), default="researcher"  # admin | researcher | it_admin
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

Create `src/server/models/project.py`:

```python
"""
FL Project model - a training project that hospitals join.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.server.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), default="created"
        # created | recruiting | training | completed | failed
    )
    strategy: Mapped[str] = mapped_column(String(50), default="fedavg")
    total_rounds: Mapped[int] = mapped_column(Integer, default=10)
    current_round: Mapped[int] = mapped_column(Integer, default=0)
    min_nodes: Mapped[int] = mapped_column(Integer, default=2)
    hyperparams: Mapped[dict] = mapped_column(JSONB, default=dict)
    dp_epsilon: Mapped[float] = mapped_column(Float, default=8.0)
    dp_delta: Mapped[float] = mapped_column(Float, default=1e-5)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    rounds = relationship("TrainingRound", back_populates="project")
```

Create `src/server/models/node.py`:

```python
"""
Edge Node model - represents a hospital's training machine.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.server.core.database import Base


class EdgeNode(Base):
    __tablename__ = "edge_nodes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hospital_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default="offline"
        # online | offline | training | error
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True
    )
    hardware_info: Mapped[dict] = mapped_column(JSONB, default=dict)
    last_heartbeat: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
```

Create `src/server/models/training_round.py`:

```python
"""
Training Round model - one round of federated training.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.server.core.database import Base


class TrainingRound(Base):
    __tablename__ = "training_rounds"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default="pending"
        # pending | distributing | training | aggregating | completed | failed
    )
    participating_nodes: Mapped[int] = mapped_column(Integer, default=0)
    global_loss: Mapped[float] = mapped_column(Float, nullable=True)
    global_accuracy: Mapped[float] = mapped_column(Float, nullable=True)
    metrics: Mapped[dict] = mapped_column(JSONB, default=dict)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    project = relationship("Project", back_populates="rounds")
```

Create `src/server/models/__init__.py` to export all models:

```python
"""Export all models so Alembic and other tools can discover them."""
from src.server.models.user import User
from src.server.models.project import Project
from src.server.models.node import EdgeNode
from src.server.models.training_round import TrainingRound

__all__ = ["User", "Project", "EdgeNode", "TrainingRound"]
```

---

### Step 2.4 — Create tables using Alembic migrations

```bash
# Initialize Alembic
cd medifl
alembic init alembic
```

Edit `alembic/env.py` — replace the `target_metadata` line:

```python
# Add these imports at the top
from src.server.core.database import Base
from src.server.models import *  # noqa - imports all models

# Change this line:
target_metadata = Base.metadata
```

Generate and run your first migration:

```bash
alembic revision --autogenerate -m "create initial tables"
alembic upgrade head
```

> **✅ Checkpoint:** Open pgAdmin or run `\dt` in psql — you should see 4 tables: `users`, `projects`, `edge_nodes`, `training_rounds`.

---

---

# PHASE 3: Backend API (FastAPI) ⚙️

### What you learn: REST APIs, request validation, dependency injection

---

### Step 3.1 — Create Pydantic schemas (request/response validation)

Create `src/server/api/schemas.py`:

```python
"""
Pydantic schemas for API request/response validation.
These are NOT database models — they validate what comes IN and goes OUT of the API.
"""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ── User Schemas ──────────────────────────────────
class UserCreate(BaseModel):
    email: str = Field(..., example="dr.smith@hospital.org")
    password: str = Field(..., min_length=8)
    full_name: str
    role: str = "researcher"


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Allows converting SQLAlchemy model → Pydantic


# ── Project Schemas ───────────────────────────────
class ProjectCreate(BaseModel):
    name: str = Field(..., example="Chest X-Ray Pneumonia Detection")
    description: Optional[str] = None
    strategy: str = "fedavg"  # fedavg | fedprox | scaffold
    total_rounds: int = Field(default=10, ge=1, le=1000)
    min_nodes: int = Field(default=2, ge=2)
    hyperparams: dict = Field(default_factory=lambda: {
        "learning_rate": 0.01,
        "batch_size": 32,
        "local_epochs": 5,
    })
    dp_epsilon: float = Field(default=8.0, gt=0)
    dp_delta: float = Field(default=1e-5, gt=0, lt=1)


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    status: str
    strategy: str
    total_rounds: int
    current_round: int
    min_nodes: int
    dp_epsilon: float
    created_at: datetime

    class Config:
        from_attributes = True


# ── Training Round Schemas ────────────────────────
class RoundResponse(BaseModel):
    id: uuid.UUID
    round_number: int
    status: str
    participating_nodes: int
    global_loss: Optional[float]
    global_accuracy: Optional[float]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Auth Schemas ──────────────────────────────────
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: str
    password: str
```

---

### Step 3.2 — Create API route handlers

Create `src/server/api/routes_auth.py`:

```python
"""
Authentication endpoints - register + login.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

from src.server.core.database import get_db
from src.server.core.config import settings
from src.server.models.user import User
from src.server.api.schemas import UserCreate, UserResponse, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict) -> str:
    """Create a JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check if email already exists
    existing = await db.execute(select(User).where(User.email == user_data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user with hashed password
    new_user = User(
        email=user_data.email,
        hashed_password=pwd_context.hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
    )
    db.add(new_user)
    await db.flush()   # Gets the auto-generated ID
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login and get a JWT token."""
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token)
```

Create `src/server/api/routes_projects.py`:

```python
"""
Project management endpoints - CRUD for FL training projects.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from src.server.core.database import get_db
from src.server.models.project import Project
from src.server.api.schemas import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new federated learning project."""
    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=uuid.uuid4(),  # TODO: Replace with authenticated user ID
        strategy=project_data.strategy,
        total_rounds=project_data.total_rounds,
        min_nodes=project_data.min_nodes,
        hyperparams=project_data.hyperparams,
        dp_epsilon=project_data.dp_epsilon,
        dp_delta=project_data.dp_delta,
    )
    db.add(new_project)
    await db.flush()
    await db.refresh(new_project)
    return new_project


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    """List all FL projects."""
    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    return result.scalars().all()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific project by ID."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
```

---

### Step 3.3 — Create the main FastAPI app

Create `src/server/main.py`:

```python
"""
MediFL Server — Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.server.core.config import settings
from src.server.core.database import engine, Base
from src.server.api.routes_auth import router as auth_router
from src.server.api.routes_projects import router as projects_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on startup and shutdown."""
    # Startup: create tables (use Alembic in production instead)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started!")
    yield
    # Shutdown
    await engine.dispose()
    print("👋 Server shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Medical Federated Learning Platform",
    lifespan=lifespan,
)

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(auth_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")


@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "HEALTHY",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
```

Run the server:

```bash
uvicorn src.server.main:app --reload --host 0.0.0.0 --port 8000
```

> **✅ Checkpoint:** Open `http://localhost:8000/docs` — you should see the Swagger UI with all your endpoints!

---

---

# PHASE 4: Federated Learning Core 🧠

### What you learn: FedAvg algorithm, model aggregation, OOP design patterns

> **This is the HEART of MediFL** — the aggregation engine that combines model weights from multiple hospitals.

---

### Step 4.1 — Create the base aggregator (Abstract class)

Create `src/aggregator/base.py`:

```python
"""
Base Aggregator — Abstract class that all FL strategies inherit from.
Matches the class hierarchy in LLD doc Section 1.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
from loguru import logger
import hashlib
import json


class ModelUpdate:
    """Represents one hospital's training result for a round."""

    def __init__(self, node_id: str, weights: Dict[str, list], num_samples: int, metrics: dict):
        self.node_id = node_id
        self.weights = weights        # {"layer_name": [weight_values]}
        self.num_samples = num_samples  # How many data samples this node trained on
        self.metrics = metrics          # {"loss": 0.5, "accuracy": 0.85}


class BaseAggregator(ABC):
    """
    Abstract base class for all aggregation strategies.
    
    Why abstract? Because FedAvg, FedProx, SCAFFOLD all aggregate differently,
    but they all need validate + compute_metrics + logging.
    """

    def __init__(self, project_id: str, hyperparams: dict):
        self.project_id = project_id
        self.current_round = 0
        self.hyperparams = hyperparams
        self.logger = logger.bind(project=project_id)

    @abstractmethod
    def aggregate(self, updates: List[ModelUpdate]) -> Dict[str, list]:
        """
        Combine model updates from all hospitals into one global model.
        Each subclass implements this differently.
        """
        pass

    def validate_weights(self, weights: Dict[str, list]) -> bool:
        """Check that weight shapes are consistent."""
        for layer_name, values in weights.items():
            if not isinstance(values, list) or len(values) == 0:
                self.logger.error(f"Invalid weights for layer: {layer_name}")
                return False
        return True

    def _compute_weights_hash(self, weights: Dict[str, list]) -> str:
        """Create a SHA-256 hash of model weights for audit trail."""
        weights_str = json.dumps(weights, sort_keys=True, default=str)
        return hashlib.sha256(weights_str.encode()).hexdigest()
```

> **💡 Key Concept:** `BaseAggregator` uses the **Template Method** pattern — it defines the skeleton (validate, log, hash) and lets subclasses override `aggregate()`.

---

### Step 4.2 — Implement FedAvg (Federated Averaging)

Create `src/aggregator/fedavg.py`:

```python
"""
Federated Averaging (FedAvg) — McMahan et al., 2017
https://arxiv.org/abs/1602.05629

The idea: average model weights from all hospitals, weighted by their dataset size.
A hospital with 50K samples gets more influence than one with 5K samples.
"""
from typing import List, Dict
from src.aggregator.base import BaseAggregator, ModelUpdate


class FedAvgAggregator(BaseAggregator):
    """
    Federated Averaging aggregation strategy.
    
    Algorithm:
    1. Receive model weights from N hospitals
    2. Calculate each hospital's weight = (its_samples / total_samples)
    3. For each layer: new_weight = sum(hospital_weight_i * hospital_layer_i)
    """

    def aggregate(self, updates: List[ModelUpdate]) -> Dict[str, list]:
        """
        Perform weighted average of all model updates.

        Args:
            updates: List of ModelUpdate objects from each hospital

        Returns:
            Aggregated global model weights
        """
        if not updates:
            raise ValueError("No updates to aggregate!")

        self.logger.info(
            f"FedAvg aggregating {len(updates)} updates for round {self.current_round}"
        )

        # Step 1: Calculate total samples across all hospitals
        total_samples = sum(u.num_samples for u in updates)

        # Step 2: Calculate the weight (importance) of each hospital
        weights = [u.num_samples / total_samples for u in updates]
        self.logger.info(f"Node weights: {dict(zip([u.node_id for u in updates], weights))}")

        # Step 3: Weighted average of all model parameters
        aggregated = self._weighted_average(updates, weights)

        # Step 4: Validate and log
        if self.validate_weights(aggregated):
            weight_hash = self._compute_weights_hash(aggregated)
            self.logger.info(f"✅ Round {self.current_round} aggregated. Hash: {weight_hash[:16]}...")
        
        self.current_round += 1
        return aggregated

    def _weighted_average(
        self, updates: List[ModelUpdate], weights: List[float]
    ) -> Dict[str, list]:
        """
        Compute weighted average across all layers.

        Math: global_layer = Σ (w_i * local_layer_i)
        where w_i = n_i / Σn_j (proportion of data at node i)
        """
        # Get layer names from first update
        layer_names = updates[0].weights.keys()
        result = {}

        for layer in layer_names:
            # For each layer, compute weighted sum
            layer_values = []
            for i, update in enumerate(updates):
                node_layer = update.weights[layer]
                # Multiply each value by this node's weight
                weighted = [v * weights[i] for v in node_layer]
                layer_values.append(weighted)

            # Sum across all nodes
            aggregated_layer = [
                sum(values) for values in zip(*layer_values)
            ]
            result[layer] = aggregated_layer

        return result
```

> **✅ Test it manually:**
> ```python
> from src.aggregator.fedavg import FedAvgAggregator, ModelUpdate
> 
> agg = FedAvgAggregator("test-project", {})
> 
> # Simulate 2 hospitals sending their trained weights
> update1 = ModelUpdate("hospital-a", {"layer1": [1.0, 2.0, 3.0]}, num_samples=100, metrics={"loss": 0.5})
> update2 = ModelUpdate("hospital-b", {"layer1": [3.0, 4.0, 5.0]}, num_samples=300, metrics={"loss": 0.3})
> 
> result = agg.aggregate([update1, update2])
> print(result)
> # layer1: [2.5, 3.5, 4.5]  ← Hospital B has 3x weight because 300 vs 100 samples
> ```

---

### Step 4.3 — Implement FedProx (optional, but good for learning)

Create `src/aggregator/fedprox.py`:

```python
"""
FedProx — Li et al., 2020
https://arxiv.org/abs/1812.06127

Like FedAvg but adds a "proximal term" that penalizes local models
from drifting too far from the global model. Useful when hospitals
have very different data distributions (non-IID data).
"""
from typing import List, Dict
from src.aggregator.base import BaseAggregator, ModelUpdate


class FedProxAggregator(BaseAggregator):

    def __init__(self, project_id: str, hyperparams: dict, mu: float = 0.01):
        super().__init__(project_id, hyperparams)
        self.mu = mu  # Proximal term strength (higher = more regularization)
        self.global_reference_weights = None

    def aggregate(self, updates: List[ModelUpdate]) -> Dict[str, list]:
        """FedProx aggregation with proximal regularization."""
        if not updates:
            raise ValueError("No updates to aggregate!")

        self.logger.info(f"FedProx (μ={self.mu}) aggregating {len(updates)} updates")

        # Apply proximal penalty to each update before averaging
        if self.global_reference_weights is not None:
            updates = [
                ModelUpdate(
                    node_id=u.node_id,
                    weights=self._apply_proximal_penalty(u.weights, self.global_reference_weights),
                    num_samples=u.num_samples,
                    metrics=u.metrics,
                )
                for u in updates
            ]

        # Then do standard weighted average (same as FedAvg)
        total_samples = sum(u.num_samples for u in updates)
        weights = [u.num_samples / total_samples for u in updates]

        layer_names = updates[0].weights.keys()
        aggregated = {}
        for layer in layer_names:
            layer_values = []
            for i, update in enumerate(updates):
                weighted = [v * weights[i] for v in update.weights[layer]]
                layer_values.append(weighted)
            aggregated[layer] = [sum(vals) for vals in zip(*layer_values)]

        # Save as reference for next round
        self.global_reference_weights = aggregated
        self.current_round += 1
        return aggregated

    def _apply_proximal_penalty(
        self, local_weights: Dict, global_weights: Dict
    ) -> Dict[str, list]:
        """
        Penalize local weights that deviate from global model.
        Formula: w_new = w_local - μ * (w_local - w_global)
        """
        penalized = {}
        for layer in local_weights:
            penalized[layer] = [
                local_val - self.mu * (local_val - global_val)
                for local_val, global_val in zip(
                    local_weights[layer], global_weights[layer]
                )
            ]
        return penalized
```

---

---

# PHASE 5: Differential Privacy 🔒

### What you learn: DP-SGD, gradient clipping, noise injection, privacy accounting

> **This is what makes MediFL HIPAA-compliant** — even the gradients can't leak patient info.

---

### Step 5.1 — Create the DP decorator

Create `src/aggregator/dp.py`:

```python
"""
Differential Privacy Decorator — wraps any aggregator with DP guarantees.

Uses the Decorator Pattern: wraps FedAvg/FedProx without changing their code.
Based on Abadi et al., "Deep Learning with Differential Privacy" (2016).
"""
import math
import random
from typing import List, Dict, Tuple
from loguru import logger

from src.aggregator.base import BaseAggregator, ModelUpdate


class DPAggregatorDecorator(BaseAggregator):
    """
    Adds Differential Privacy to any aggregation strategy.
    
    Two key operations:
    1. CLIP: Limit how much any single hospital can influence the result
    2. NOISE: Add calibrated Gaussian noise to the aggregated weights
    """

    def __init__(
        self,
        wrapped_aggregator: BaseAggregator,
        clip_norm: float = 1.0,
        noise_multiplier: float = 0.1,
        target_delta: float = 1e-5,
    ):
        super().__init__(
            wrapped_aggregator.project_id,
            wrapped_aggregator.hyperparams,
        )
        self.wrapped = wrapped_aggregator
        self.clip_norm = clip_norm
        self.noise_multiplier = noise_multiplier
        self.target_delta = target_delta

        # Privacy accounting (tracks total privacy budget spent)
        self.epsilon_spent = 0.0
        self.rounds_completed = 0

    def aggregate(self, updates: List[ModelUpdate]) -> Dict[str, list]:
        """
        DP-enhanced aggregation:
        1. Clip each hospital's update
        2. Aggregate using the wrapped strategy (e.g., FedAvg)
        3. Add calibrated noise to the result
        """
        self.logger.info(f"🔒 DP aggregation with clip={self.clip_norm}, noise={self.noise_multiplier}")

        # Step 1: Clip each hospital's gradients
        clipped_updates = []
        for update in updates:
            clipped_weights = self.clip_gradients(update.weights)
            clipped_updates.append(
                ModelUpdate(update.node_id, clipped_weights, update.num_samples, update.metrics)
            )

        # Step 2: Aggregate using wrapped strategy (FedAvg, FedProx, etc.)
        aggregated = self.wrapped.aggregate(clipped_updates)

        # Step 3: Add Gaussian noise
        noised = self.add_dp_noise(aggregated, len(updates))

        # Step 4: Update privacy accounting
        self._update_privacy_budget(len(updates))

        eps, delta = self.get_privacy_spent()
        self.logger.info(f"🔒 Privacy budget: ε={eps:.4f}, δ={delta}")

        return noised

    def clip_gradients(self, weights: Dict[str, list]) -> Dict[str, list]:
        """
        Clip gradients so no single hospital has outsized influence.
        
        How: If the L2 norm of the weights exceeds clip_norm, scale them down.
        This is like saying "no hospital can change the model by more than X amount."
        """
        # Calculate L2 norm across all layers
        total_norm = 0.0
        for layer_values in weights.values():
            total_norm += sum(v ** 2 for v in layer_values)
        total_norm = math.sqrt(total_norm)

        # If norm exceeds clip threshold, scale down
        if total_norm > self.clip_norm:
            scale = self.clip_norm / total_norm
            clipped = {}
            for layer, values in weights.items():
                clipped[layer] = [v * scale for v in values]
            self.logger.debug(f"Clipped: norm {total_norm:.4f} → {self.clip_norm}")
            return clipped

        return weights  # No clipping needed

    def add_dp_noise(self, weights: Dict[str, list], num_nodes: int) -> Dict[str, list]:
        """
        Add calibrated Gaussian noise to aggregated weights.
        
        Noise scale = (clip_norm * noise_multiplier) / num_nodes
        More nodes → less noise per parameter (privacy amplification).
        """
        noise_scale = (self.clip_norm * self.noise_multiplier) / num_nodes
        noised = {}

        for layer, values in weights.items():
            noised[layer] = [
                v + random.gauss(0, noise_scale)
                for v in values
            ]

        return noised

    def _update_privacy_budget(self, num_nodes: int):
        """Simple privacy accounting using basic composition theorem."""
        # Per-round epsilon (simplified — use RDP accountant for production)
        round_epsilon = self.noise_multiplier * math.sqrt(2 * math.log(1.25 / self.target_delta))
        self.epsilon_spent += round_epsilon
        self.rounds_completed += 1

    def get_privacy_spent(self) -> Tuple[float, float]:
        """Return total (epsilon, delta) spent so far."""
        return (self.epsilon_spent, self.target_delta)
```

> **✅ Test it:**
> ```python
> from src.aggregator.fedavg import FedAvgAggregator, ModelUpdate
> from src.aggregator.dp import DPAggregatorDecorator
> 
> # Create FedAvg, then wrap it with DP
> base = FedAvgAggregator("test", {})
> dp_agg = DPAggregatorDecorator(base, clip_norm=1.0, noise_multiplier=0.5)
> 
> u1 = ModelUpdate("hosp-a", {"layer1": [1.0, 2.0]}, 100, {"loss": 0.5})
> u2 = ModelUpdate("hosp-b", {"layer1": [3.0, 4.0]}, 200, {"loss": 0.3})
> 
> result = dp_agg.aggregate([u1, u2])
> print(result)  # Values will be slightly different each time (noise!)
> print(dp_agg.get_privacy_spent())  # (epsilon, delta)
> ```

---

---

# PHASE 6: Edge Agent (Hospital Side) 🏥

### What you learn: PyTorch training loops, model serialization, client-server patterns

---

### Step 6.1 — Create the edge agent trainer

Create `src/edge_agent/trainer.py`:

```python
"""
Edge Agent Trainer — runs on each hospital's machine.
Trains a local model on private patient data, then sends only the weights (not data) to the server.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, Tuple
from loguru import logger


class LocalTrainer:
    """
    Handles local model training at a hospital edge node.
    
    Workflow each round:
    1. Receive global model weights from server
    2. Load them into local model
    3. Train on local patient data for N epochs
    4. Extract weight updates (difference)
    5. Send updates back to server
    """

    def __init__(
        self,
        model: nn.Module,
        node_id: str,
        learning_rate: float = 0.01,
        local_epochs: int = 5,
        device: str = "cpu",
    ):
        self.model = model.to(device)
        self.node_id = node_id
        self.learning_rate = learning_rate
        self.local_epochs = local_epochs
        self.device = device
        self.logger = logger.bind(node=node_id)

    def load_global_weights(self, global_weights: Dict[str, list]):
        """Load the global model weights received from the server."""
        state_dict = {}
        for name, values in global_weights.items():
            state_dict[name] = torch.tensor(values)
        self.model.load_state_dict(state_dict)
        self.logger.info("📥 Loaded global model weights")

    def train(self, dataloader: DataLoader) -> Tuple[Dict[str, list], int, dict]:
        """
        Train the model on local data.

        Returns:
            Tuple of (updated_weights, num_samples, metrics)
        """
        self.model.train()
        optimizer = optim.SGD(self.model.parameters(), lr=self.learning_rate)
        criterion = nn.CrossEntropyLoss()

        total_loss = 0.0
        total_correct = 0
        total_samples = 0

        for epoch in range(self.local_epochs):
            epoch_loss = 0.0
            for batch_data, batch_labels in dataloader:
                batch_data = batch_data.to(self.device)
                batch_labels = batch_labels.to(self.device)

                # Forward pass
                outputs = self.model(batch_data)
                loss = criterion(outputs, batch_labels)

                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                # Track metrics
                epoch_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                total_correct += (predicted == batch_labels).sum().item()
                total_samples += batch_labels.size(0)

            avg_loss = epoch_loss / len(dataloader)
            self.logger.info(f"  Epoch {epoch+1}/{self.local_epochs} — Loss: {avg_loss:.4f}")
            total_loss += avg_loss

        # Extract trained weights
        updated_weights = {}
        for name, param in self.model.named_parameters():
            updated_weights[name] = param.detach().cpu().tolist()

        metrics = {
            "loss": total_loss / self.local_epochs,
            "accuracy": total_correct / total_samples if total_samples > 0 else 0,
        }

        self.logger.info(
            f"✅ Training complete. Loss: {metrics['loss']:.4f}, "
            f"Accuracy: {metrics['accuracy']:.4f}, Samples: {total_samples}"
        )

        return updated_weights, total_samples, metrics

    def get_weights(self) -> Dict[str, list]:
        """Get current model weights as plain Python lists."""
        weights = {}
        for name, param in self.model.named_parameters():
            weights[name] = param.detach().cpu().tolist()
        return weights
```

---

### Step 6.2 — Create a simple medical image model

Create `src/edge_agent/model.py`:

```python
"""
Simple CNN for medical image classification.
In production, you'd use ResNet, DenseNet, or Vision Transformers.
This is a learning-friendly starting point.
"""
import torch.nn as nn


class SimpleMedicalCNN(nn.Module):
    """
    A basic CNN for classifying medical images (e.g., chest X-rays).
    Input: 1-channel grayscale image (224x224)
    Output: num_classes predictions
    """

    def __init__(self, num_classes: int = 2):
        super().__init__()

        # Feature extraction layers
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),             # 224 → 112

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),             # 112 → 56

            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((7, 7)),   # Any size → 7x7
        )

        # Classification head
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 7 * 7, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x
```

---

---

# PHASE 7: gRPC Communication 📡

### What you learn: Protocol Buffers, gRPC services, server↔client architecture

---

### Step 7.1 — Define the Protocol Buffer schema

Create `proto/medifl.proto`:

```protobuf
// MediFL gRPC Service Definition
// This defines the "contract" between the server and hospital edge agents.

syntax = "proto3";
package medifl;

// ── Service Definition ───────────────────────────
service FederatedService {
    // Hospital registers itself with the server
    rpc RegisterNode (NodeRegistration) returns (NodeRegistrationResponse);

    // Hospital sends a heartbeat to prove it's alive
    rpc Heartbeat (HeartbeatRequest) returns (HeartbeatResponse);

    // Server sends global model → Hospital
    rpc GetGlobalModel (ModelRequest) returns (GlobalModel);

    // Hospital sends trained weights → Server
    rpc SubmitUpdate (ModelUpdate) returns (SubmitResponse);
}

// ── Messages ─────────────────────────────────────
message NodeRegistration {
    string node_id = 1;
    string hospital_name = 2;
    string hardware_info = 3;   // JSON string
}

message NodeRegistrationResponse {
    bool success = 1;
    string message = 2;
    string assigned_project_id = 3;
}

message HeartbeatRequest {
    string node_id = 1;
    string status = 2;          // "idle" | "training" | "error"
    float gpu_utilization = 3;
    float memory_usage = 4;
}

message HeartbeatResponse {
    bool acknowledged = 1;
    string command = 2;         // "wait" | "start_training" | "stop"
}

message ModelRequest {
    string node_id = 1;
    string project_id = 2;
    int32 round_number = 3;
}

message GlobalModel {
    string project_id = 1;
    int32 round_number = 2;
    bytes model_weights = 3;    // Serialized model weights
    string hyperparams = 4;     // JSON string
}

message ModelUpdate {
    string node_id = 1;
    string project_id = 2;
    int32 round_number = 3;
    bytes model_weights = 4;    // Serialized trained weights
    int32 num_samples = 5;
    string metrics = 6;         // JSON string {"loss": 0.5, "accuracy": 0.85}
}

message SubmitResponse {
    bool accepted = 1;
    string message = 2;
}
```

Generate Python code from proto:

```bash
python -m grpc_tools.protoc \
    -I proto/ \
    --python_out=src/server/grpc_service/ \
    --grpc_python_out=src/server/grpc_service/ \
    proto/medifl.proto
```

This generates `medifl_pb2.py` and `medifl_pb2_grpc.py` automatically.

---

### Step 7.2 — Create the gRPC server

Create `src/server/grpc_service/server.py`:

```python
"""
gRPC Server — handles communication with hospital edge agents.
"""
import grpc
from concurrent import futures
import json
import pickle
from loguru import logger

# These are auto-generated from the .proto file
from src.server.grpc_service import medifl_pb2, medifl_pb2_grpc


class FederatedServicer(medifl_pb2_grpc.FederatedServiceServicer):
    """Implements the gRPC service methods."""

    def __init__(self):
        self.registered_nodes = {}
        self.pending_updates = {}
        self.global_model_weights = None
        self.current_round = 0

    def RegisterNode(self, request, context):
        """Handle hospital node registration."""
        logger.info(f"🏥 Node registering: {request.hospital_name} ({request.node_id})")
        self.registered_nodes[request.node_id] = {
            "hospital_name": request.hospital_name,
            "status": "online",
            "hardware": json.loads(request.hardware_info) if request.hardware_info else {},
        }
        return medifl_pb2.NodeRegistrationResponse(
            success=True,
            message=f"Welcome {request.hospital_name}!",
            assigned_project_id="default-project",
        )

    def Heartbeat(self, request, context):
        """Handle heartbeat from edge nodes."""
        if request.node_id in self.registered_nodes:
            self.registered_nodes[request.node_id]["status"] = request.status
        
        # Decide what to tell the node
        command = "wait"
        if self.current_round > 0:
            command = "start_training"

        return medifl_pb2.HeartbeatResponse(acknowledged=True, command=command)

    def GetGlobalModel(self, request, context):
        """Send global model weights to a requesting node."""
        logger.info(f"📤 Sending global model to {request.node_id}")
        
        model_bytes = pickle.dumps(self.global_model_weights) if self.global_model_weights else b""
        
        return medifl_pb2.GlobalModel(
            project_id=request.project_id,
            round_number=self.current_round,
            model_weights=model_bytes,
            hyperparams=json.dumps({"learning_rate": 0.01, "local_epochs": 5}),
        )

    def SubmitUpdate(self, request, context):
        """Receive trained model weights from a hospital."""
        logger.info(
            f"📥 Received update from {request.node_id} "
            f"(round {request.round_number}, {request.num_samples} samples)"
        )
        
        weights = pickle.loads(request.model_weights)
        metrics = json.loads(request.metrics)
        
        # Store the update
        if request.round_number not in self.pending_updates:
            self.pending_updates[request.round_number] = []
        
        self.pending_updates[request.round_number].append({
            "node_id": request.node_id,
            "weights": weights,
            "num_samples": request.num_samples,
            "metrics": metrics,
        })
        
        return medifl_pb2.SubmitResponse(
            accepted=True,
            message=f"Update accepted for round {request.round_number}",
        )


def serve(port: int = 50051):
    """Start the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    medifl_pb2_grpc.add_FederatedServiceServicer_to_server(
        FederatedServicer(), server
    )
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info(f"🚀 gRPC server running on port {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
```

---

---

# PHASE 8: React Dashboard 🖥️

### What you learn: React, REST API calls, real-time WebSocket updates

---

### Step 8.1 — Create the React app

```bash
cd frontend
npx -y create-react-app@latest . --template typescript
npm install axios recharts react-router-dom
```

---

### Step 8.2 — Create the Dashboard page

Replace `frontend/src/App.tsx`:

```tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://localhost:8000/api/v1';

interface Project {
  id: string;
  name: string;
  status: string;
  strategy: string;
  current_round: number;
  total_rounds: number;
}

function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [health, setHealth] = useState<string>('checking...');

  useEffect(() => {
    // Check server health
    axios.get('http://localhost:8000/healthz')
      .then(res => setHealth(res.data.status))
      .catch(() => setHealth('OFFLINE'));

    // Fetch projects
    axios.get(`${API_BASE}/projects/`)
      .then(res => setProjects(res.data))
      .catch(err => console.error('Failed to fetch projects:', err));
  }, []);

  return (
    <div className="app">
      <header className="header">
        <h1>🧠 MediFL Dashboard</h1>
        <span className={`status ${health === 'HEALTHY' ? 'online' : 'offline'}`}>
          Server: {health}
        </span>
      </header>

      <main className="main">
        <section className="projects">
          <h2>FL Training Projects</h2>
          {projects.length === 0 ? (
            <p>No projects yet. Create one via the API!</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Strategy</th>
                  <th>Status</th>
                  <th>Progress</th>
                </tr>
              </thead>
              <tbody>
                {projects.map(p => (
                  <tr key={p.id}>
                    <td>{p.name}</td>
                    <td>{p.strategy.toUpperCase()}</td>
                    <td><span className={`badge ${p.status}`}>{p.status}</span></td>
                    <td>{p.current_round} / {p.total_rounds} rounds</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
```

---

---

# PHASE 9: Security 🔐

### What you learn: JWT auth middleware, mTLS certificates, audit logging

---

### Step 9.1 — Create JWT auth middleware

Create `src/server/core/security.py`:

```python
"""
Security utilities — JWT validation, role-based access control.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from src.server.core.config import settings

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    """
    FastAPI dependency — extracts and validates JWT from Authorization header.
    Use it like: @router.get("/protected", dependencies=[Depends(get_current_user)])
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")


def require_role(allowed_roles: list):
    """
    Role-based access decorator.
    Usage: @router.get("/admin-only", dependencies=[Depends(require_role(["admin"]))])
    """
    async def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker
```

---

### Step 9.2 — Generate mTLS certificates (for gRPC)

```bash
# Create a certificates directory
mkdir -p certs

# Generate CA (Certificate Authority) key and cert
openssl req -x509 -newkey rsa:4096 -keyout certs/ca.key -out certs/ca.crt \
    -days 365 -nodes -subj "/CN=MediFL-CA"

# Generate server key and CSR
openssl req -newkey rsa:4096 -keyout certs/server.key -out certs/server.csr \
    -nodes -subj "/CN=medifl-server"

# Sign server cert with CA
openssl x509 -req -in certs/server.csr -CA certs/ca.crt -CAkey certs/ca.key \
    -CAcreateserial -out certs/server.crt -days 365

# Generate client (edge node) key and cert
openssl req -newkey rsa:4096 -keyout certs/client.key -out certs/client.csr \
    -nodes -subj "/CN=hospital-edge-node"

openssl x509 -req -in certs/client.csr -CA certs/ca.crt -CAkey certs/ca.key \
    -CAcreateserial -out certs/client.crt -days 365
```

> **💡 Why mTLS?** Regular TLS only verifies the server. mTLS (mutual TLS) verifies **both** sides — so the server proves it's MediFL, and the hospital proves it's authorized.

---

---

# PHASE 10: Docker & Deployment 🐳

### What you learn: Dockerfiles, Docker Compose, multi-service orchestration

---

### Step 10.1 — Create the backend Dockerfile

Create `docker/Dockerfile.server`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY config/ config/
COPY .env .env

# Expose ports (REST + gRPC)
EXPOSE 8000 50051

# Run the FastAPI server
CMD ["uvicorn", "src.server.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### Step 10.2 — Create Docker Compose

Create `docker-compose.yml` in the project root:

```yaml
version: "3.9"

services:
  # ── PostgreSQL Database ──────────────────────
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: medifl
      POSTGRES_PASSWORD: medifl_pass
      POSTGRES_DB: medifl_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U medifl"]
      interval: 5s
      timeout: 5s
      retries: 5

  # ── Redis Cache ──────────────────────────────
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s

  # ── MediFL API Server ────────────────────────
  server:
    build:
      context: .
      dockerfile: docker/Dockerfile.server
    ports:
      - "8000:8000"
      - "50051:50051"
    environment:
      DATABASE_URL: postgresql+asyncpg://medifl:medifl_pass@postgres:5432/medifl_db
      REDIS_URL: redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

volumes:
  pgdata:
```

Run everything:

```bash
docker compose up -d --build
```

> **✅ Final Checkpoint:** Open `http://localhost:8000/healthz` — should return `{"status": "HEALTHY"}`

---

---

# 🎯 Summary: What You Learned

| Phase | Concepts |
|-------|----------|
| 1. Setup | Project structure, virtual envs, configs |
| 2. Database | SQLAlchemy ORM, async PostgreSQL, migrations |
| 3. API | FastAPI REST, Pydantic validation, dependency injection |
| 4. FL Core | FedAvg algorithm, weighted averaging, OOP design |
| 5. DP | Gradient clipping, noise injection, privacy accounting |
| 6. Edge Agent | PyTorch training loop, model serialization |
| 7. gRPC | Protocol Buffers, RPC services, server-client comms |
| 8. Frontend | React, Axios API calls, dashboard UI |
| 9. Security | JWT auth, mTLS, role-based access control |
| 10. Docker | Containerization, Docker Compose, multi-service orchestration |

---

## 🚀 What's Next?

After finishing these 10 phases, you can enhance with:
- **WebSocket** real-time training progress
- **Prometheus + Grafana** monitoring
- **Kubernetes** deployment
- **Opacus** library for production-grade DP-SGD
- **Flower** framework for production FL
