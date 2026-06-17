"""Copilot instructions for CRIP Enterprise Platform"""

## Project Overview

CRIP Enterprise Platform is a comprehensive microservices architecture for credit risk assessment and fraud detection.

### Architecture

- **6 Microservices**: Auth, Customer, Account, Credit Scoring, Fraud Detection, Document AI
- **API Gateway**: Central entry point with 13-step request interceptor pipeline
- **Data Layer**: Redis + PostgreSQL
- **Framework**: Python FastAPI

### Key Components

1. **Request Interceptor Pipeline** (gateway/app/interceptors.py)
   - 13-step validation and security pipeline
   - Rate limiting, JWT validation, RBAC enforcement
   - Audit logging

2. **Microservices** (services/*/app/main.py)
   - Each service has own database
   - Health check endpoints
   - Business logic endpoints

3. **Shared Library** (shared-lib/)
   - Token validation, risk profile aggregation
   - Default prediction stubs, exceptions, utilities

### Development Guidelines

1. **Adding an Endpoint**:
   - Define Pydantic schema
   - Add to routes in service or gateway
   - Update middleware if needed

2. **Service Communication**:
   - Gateway proxies requests to services (gateway/app/routes.py)
   - Internal service methods in shared-lib
   - Use httpx for async HTTP calls

3. **Configuration**:
   - Environment variables in .env
   - Settings loaded in app/config.py

### Current Phase

**Phase 1: Foundation & Core Infrastructure**
- ✅ Monorepo structure
- ✅ API Gateway with routing
- ✅ Request Interceptor Pipeline
- ✅ Redis + PostgreSQL setup
- ✅ All 6 services stubbed

### Next Steps

- Phase 2: Implement full business logic
- Phase 3: Add notifications and security hardening
- Phase 4: Production readiness and observability

### Running the Project

```bash
docker-compose up -d
curl http://localhost:8000/health
```

For detailed setup, see QUICKSTART.md
