# Snake Game - Multiplayer Application

A full-stack multiplayer Snake game application with authentication, leaderboards, and real-time features.

## Architecture

- **Frontend**: React 19 + Vite + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Containerization**: Docker Compose
- **Orchestration**: Kubernetes (GKE)
- **Infrastructure**: Terraform
- **CI/CD**: GitHub Actions

## System Design

### High-Level Overview

The Snake Game application follows a modern microservices architecture with clear separation between frontend, backend, and data layers. The system is designed for scalability, reliability, and maintainability.

#### Application Layers

1. **Presentation Layer (Frontend)**
   - React-based Single Page Application (SPA)
   - Served via Node.js `serve` in production
   - Communicates with backend via RESTful API
   - Uses relative paths for API calls (routed through Ingress)

2. **Application Layer (Backend)**
   - FastAPI REST API
   - JWT-based authentication
   - Business logic and game state management
   - Stateless design for horizontal scaling

3. **Data Layer**
   - PostgreSQL for production (Cloud SQL)
   - SQLite for local development
   - SQLAlchemy ORM for database abstraction

#### Key Design Principles

- **Stateless Backend**: All state stored in database, enabling horizontal scaling
- **API-First Design**: Clear separation between frontend and backend
- **Containerization**: All services containerized for consistent deployment
- **Infrastructure as Code**: All infrastructure defined in Terraform
- **CI/CD Automation**: Automated testing, building, and deployment
- **Security**: Workload Identity Federation, HTTPS, JWT tokens

### Cloud Resource Architecture

The following diagram illustrates the cloud infrastructure and data flow:

```mermaid
graph TB
    subgraph "External"
        User[👤 Users]
        GitHub[GitHub Actions<br/>CI/CD Pipeline]
    end

    subgraph "Google Cloud Platform"
        subgraph "Networking"
            DNS[Cloud DNS<br/>snake-game.nabuminds-test.app]
            IP[Global Static IP]
            Ingress[GKE Ingress<br/>HTTPS Load Balancer]
            Cert[Managed SSL Certificate]
        end

        subgraph "GKE Cluster (general-cluster)"
            subgraph "Namespace: snake-game"
                subgraph "Frontend"
                    FrontendSvc[Frontend Service<br/>Port 3000]
                    FrontendPod[Frontend Pods<br/>React SPA]
                end

                subgraph "Backend"
                    BackendSvc[Backend Service<br/>Port 8001]
                    BackendPod[Backend Pods<br/>FastAPI]
                end
            end
        end

        subgraph "Storage & Registry"
            ArtifactReg[Artifact Registry<br/>Docker Images]
            CloudSQL[(Cloud SQL<br/>PostgreSQL)]
        end

        subgraph "Infrastructure"
            Terraform[Terraform State<br/>GCS Bucket]
            Secrets[Secret Manager<br/>Credentials]
        end
    end

    User -->|HTTPS| DNS
    DNS --> IP
    IP --> Ingress
    Ingress -->|/api/*| BackendSvc
    Ingress -->|/*| FrontendSvc
    Cert --> Ingress

    FrontendSvc --> FrontendPod
    BackendSvc --> BackendPod
    BackendPod -->|Database Connection| CloudSQL

    GitHub -->|Build & Push| ArtifactReg
    ArtifactReg -->|Pull Images| FrontendPod
    ArtifactReg -->|Pull Images| BackendPod

    GitHub -->|Deploy| Terraform
    Terraform -->|Provision| Ingress
    Terraform -->|Provision| CloudSQL
    Terraform -->|Provision| ArtifactReg

    BackendPod -->|Read Secrets| Secrets
    FrontendPod -->|Read Secrets| Secrets

    style User fill:#e1f5ff
    style GitHub fill:#f0f0f0
    style DNS fill:#fff4e6
    style Ingress fill:#fff4e6
    style FrontendPod fill:#e8f5e9
    style BackendPod fill:#e8f5e9
    style CloudSQL fill:#f3e5f5
    style ArtifactReg fill:#e3f2fd
    style Secrets fill:#ffebee
```

### Component Details

#### Frontend Service
- **Technology**: React 19 + Vite
- **Runtime**: Node.js `serve` (static file server)
- **Port**: 3000
- **Routing**: Client-side routing with SPA support
- **API Communication**: Relative paths (`/api/v1/*`) routed through Ingress

#### Backend Service
- **Technology**: FastAPI (Python)
- **Port**: 8001
- **Authentication**: JWT Bearer tokens
- **Database**: PostgreSQL via Cloud SQL
- **Health Checks**: `/health` endpoint

#### Networking
- **Ingress**: GKE Ingress Controller
- **Routing Rules**:
  - `/api/*` → Backend Service
  - `/*` → Frontend Service
- **SSL/TLS**: Google-managed SSL certificates
- **Domain**: `snake-game.nabuminds-test.app`

#### Data Flow

1. **User Request Flow**:
   ```
   User → DNS → Global IP → Ingress → Service → Pod
   ```

2. **API Request Flow**:
   ```
   Frontend → Ingress (/api/*) → Backend Service → Backend Pod → Cloud SQL
   ```

3. **Deployment Flow**:
   ```
   GitHub Actions → Build Images → Push to Artifact Registry → 
   Deploy to GKE → Pull Images → Create Pods
   ```

#### Security

- **Authentication**: Workload Identity Federation (no service account keys)
- **Network**: HTTPS only, internal cluster networking
- **Secrets**: Google Secret Manager for sensitive data
- **Database**: Private IP, no public access
- **Container Images**: Stored in private Artifact Registry

## Quick Start with Docker

The easiest way to run the entire application:

```bash
# 1. Copy environment file (required - no defaults)
cp .env.example .env

# 2. Edit .env file with your values (especially SECRET_KEY and POSTGRES_PASSWORD)

# 3. Start all services
docker-compose up --build

# 4. Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

**Important:** The `.env` file is required. All environment variables must be set as there are no default values in `docker-compose.yml`.

See [DOCKER.md](./DOCKER.md) for detailed Docker documentation.

## Local Development

### Prerequisites

- Python 3.9+
- Node.js 20+
- PostgreSQL (optional, SQLite used by default)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run server
python run.py
# Or: uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Backend will be available at http://localhost:8001

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at http://localhost:5173

### Environment Variables

#### Backend
Create a `.env` file in the `backend` directory:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/snake_game
# Or for SQLite (default):
# DATABASE_URL=sqlite:///./snake_game.db
SECRET_KEY=your-secret-key
```

#### Frontend
Create a `.env` file in the `frontend` directory:
```env
VITE_API_BASE_URL=http://localhost:8001/api/v1
```

## Testing

### Backend Tests

```bash
cd backend

# Unit tests
pytest tests/ -v

# Integration tests
pytest tests_integration/ -v

# All tests
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run tests with UI
npm run test:ui
```

## Project Structure

```
Module_2_End_to_End_Application/
├── backend/                    # FastAPI backend
│   ├── app/                    # Application code
│   │   ├── routers/           # API routes
│   │   ├── models.py          # Pydantic models
│   │   ├── db_models.py       # SQLAlchemy models
│   │   ├── database.py        # Database operations
│   │   └── db_config.py       # Database configuration
│   ├── tests/                 # Unit tests
│   ├── tests_integration/     # Integration tests
│   └── Dockerfile             # Backend Docker image
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/         # API service
│   │   └── utils/            # Utilities
│   └── Dockerfile            # Frontend Docker image (uses Node.js serve)
├── infrastructure/             # Infrastructure as Code
│   ├── terraform/            # Terraform configurations
│   └── manifest/            # Kubernetes manifests
│       ├── network/         # Ingress and certificates
│       ├── secrets/         # Kubernetes secrets
│       └── workloads/       # Deployments and services
├── .github/
│   ├── workflows/           # GitHub Actions workflows
│   │   ├── merge.yml       # Deployment workflow (main branch)
│   │   └── pull-request.yml # CI workflow (PRs)
│   └── actions/            # Custom GitHub Actions
│       └── gke-auth/       # GKE authentication action
├── api/                      # OpenAPI specifications
├── policy/                   # OPA/Conftest policies
├── docker-compose.yml        # Docker Compose configuration
├── deploy.sh                 # Manual deployment script
└── DOCKER.md                 # Docker documentation
```

## Features

### Application Features
- ✅ User authentication (signup, login, logout)
- ✅ JWT token-based authentication
- ✅ Game modes (wall, pass-through)
- ✅ Score submission and leaderboard
- ✅ Real-time top 5 leaderboard on landing page
- ✅ Full leaderboard page
- ✅ Game pause/resume functionality

### Infrastructure & DevOps
- ✅ PostgreSQL (production) and SQLite (development) support
- ✅ Docker Compose setup for local development
- ✅ Kubernetes deployment to GKE
- ✅ Infrastructure as Code with Terraform
- ✅ CI/CD with GitHub Actions
- ✅ Automated testing (unit, integration)
- ✅ Policy enforcement with Conftest/OPA
- ✅ Commit SHA-based image tagging
- ✅ Workload Identity Federation for secure authentication
- ✅ Comprehensive test coverage

## CI/CD

This project uses GitHub Actions for continuous integration and deployment to Google Kubernetes Engine (GKE).

### Workflows

#### Pull Request Workflow (`.github/workflows/pull-request.yml`)

Runs on pull requests to `main` branch:

1. **Backend Tests** - Runs unit tests for the backend
2. **Frontend Tests** - Runs unit tests for the frontend
3. **Integration Tests** - Runs integration tests
4. **Terraform Validate** - Validates Terraform configuration
5. **Terraform Plan** - Creates Terraform plan and runs Conftest policy checks

#### Merge Workflow (`.github/workflows/merge.yml`)

Runs on pushes to `main` branch:

1. **Terraform Apply** - Applies infrastructure changes
   - Generates image tag from commit SHA (first 7 characters)
   - Deploys infrastructure using Terraform
   - Outputs image tag for use in deployment jobs

2. **Deploy Secrets** - Deploys Kubernetes secrets

3. **Deploy Backend** - Deploys backend application
   - Uses image tag from Terraform job output
   - Deploys backend service and deployment
   - Waits for rollout completion

4. **Deploy Frontend** - Deploys frontend application
   - Uses image tag from Terraform job output
   - Deploys frontend service and deployment
   - Waits for rollout completion

5. **Deploy Network Resources** - Deploys ingress and certificates
   - Runs after both frontend and backend are deployed

6. **Verify Deployments** - Verifies all deployments are healthy

### Image Tagging

Docker images are tagged using the commit SHA (first 7 characters) instead of timestamps. This provides:
- **Traceability**: Direct link between code commit and deployed image
- **Reproducibility**: Same commit always produces the same tag
- **Uniqueness**: Each commit gets a unique identifier

Example: Commit `a1b2c3d4e5f6...` produces image tag `a1b2c3d`

### Custom Actions

- **GKE Auth Action** (`.github/actions/gke-auth/action.yml`)
  - Reusable action for authenticating to Google Cloud and GKE
  - Configures kubectl and creates namespace if needed

### Setup

The workflows use **Workload Identity Federation** for authentication:

1. Service Account: `terraform-test-deployment@nabuminds-test.iam.gserviceaccount.com`
2. Workload Identity Provider: Configured for GitHub Actions
3. No secrets required - authentication is handled via Workload Identity

See [.github/workflows/README.md](.github/workflows/README.md) for detailed setup instructions.

### Manual Deployment

You can also deploy manually using the provided script:

```bash
./deploy.sh
```

This script:
- Deploys infrastructure with Terraform
- Generates timestamp-based image tags
- Builds and pushes Docker images
- Deploys to Kubernetes

### Deployment Architecture

The deployment process follows this order:

1. **Infrastructure** → Terraform applies infrastructure changes
2. **Secrets** → Kubernetes secrets are deployed
3. **Backend & Frontend** → Applications are deployed in parallel
4. **Network** → Ingress and certificates are configured
5. **Verification** → All deployments are verified

This ensures proper dependency ordering and allows for parallel deployment of frontend and backend services.

## Kubernetes Deployment

The application is deployed to Google Kubernetes Engine (GKE) with the following configuration:

### Cluster Information
- **Project**: `nabuminds-test`
- **Cluster**: `general-cluster`
- **Region**: `europe-west3`
- **Namespace**: `snake-game`

### Services
- **Backend**: FastAPI service on port 8001
- **Frontend**: React application served via Node.js `serve` on port 3000
- **Database**: PostgreSQL (Cloud SQL)

### Networking
- **Ingress**: HTTPS with managed certificates
- **Domain**: `snake-game.nabuminds-test.app`
- **API Routing**: `/api/*` routes to backend, `/*` routes to frontend

### Image Registry
- **Registry**: `europe-west3-docker.pkg.dev/nabuminds-test/snake-game/`
- **Backend Image**: `backend-image:<commit-sha>`
- **Frontend Image**: `frontend-image:<commit-sha>`

### Deployment Process
1. Infrastructure is provisioned via Terraform
2. Docker images are built and pushed to Artifact Registry
3. Kubernetes manifests are applied in the correct order
4. Health checks ensure successful deployment

## API Documentation

When the backend is running, visit:
- **Local**: http://localhost:8001/docs
- **Production**: https://snake-game.nabuminds-test.app/api/v1/docs (if deployed)

OpenAPI specification: [api/openapi.yaml](./api/openapi.yaml)

## License

MIT
