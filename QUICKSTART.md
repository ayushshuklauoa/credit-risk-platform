# CRIP Enterprise Platform - Setup Instructions

## Quick Start

1. **Navigate to project directory:**
```bash
cd credit-risk-platform
```

2. **Create .env file:**
```bash
cp .env.example .env
```

3. **Start all services:**
```bash
docker-compose up -d
```

4. **Verify services are running:**
```bash
# Gateway health
curl http://localhost:8000/health

# View logs
docker-compose logs -f gateway
```

## Service Ports

- **API Gateway**: 8000
- **Auth Service**: 8001
- **Customer Service**: 8002
- **Account Service**: 8003
- **Credit Scoring Service**: 8004
- **Fraud Detection Service**: 8005
- **Document AI Service**: 8006
- **Redis**: 6379
- **PostgreSQL (Auth)**: 5432
- **PostgreSQL (Customer)**: 5433
- **PostgreSQL (Account)**: 5434
- **PostgreSQL (Credit)**: 5435
- **PostgreSQL (Fraud)**: 5436
- **PostgreSQL (Document)**: 5437

## API Documentation

Access Swagger UI at:
- Gateway: http://localhost:8000/docs
- Auth: http://localhost:8001/docs
- Others: http://localhost:800X/docs

## Project Structure

```
credit-risk-platform/
├── gateway/              # API Gateway
├── services/
│   ├── auth-service/
│   ├── customer-service/
│   ├── account-service/
│   ├── credit-scoring-service/
│   ├── fraud-detection-service/
│   └── document-ai-service/
├── shared-lib/          # Shared utilities
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Next Steps

1. Review and test API endpoints
2. Customize .env file for your environment
3. Implement Phase 2: Core Services (databases, business logic)
4. Add async messaging (Kafka/RabbitMQ)
5. Implement notification channels
6. Add observability (OpenTelemetry, Prometheus)
7. Deploy to Kubernetes

## Troubleshooting

**Port already in use:**
- Modify `docker-compose.yml` port mappings
- Kill existing processes: `lsof -i :8000`

**Database connection failed:**
- Wait 30 seconds for databases to start
- Check PostgreSQL logs: `docker-compose logs postgres-auth`

**Service connection refused:**
- Verify Docker network: `docker network ls`
- Check service logs: `docker-compose logs service-name`

## Development Workflow

```bash
# Start services
docker-compose up

# Stop services
docker-compose down

# Rebuild images
docker-compose build

# View specific service logs
docker-compose logs -f auth-service

# Execute command in container
docker-compose exec gateway bash
```

For detailed information, see [README.md](../README.md)
