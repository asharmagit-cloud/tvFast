# Docker Setup Guide

This guide explains how to containerize and run the FastAPI backend and Next.js frontend using Docker.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

## Quick Start

### Development Environment

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Update `.env` with your MongoDB connection string and other settings**

3. **Start all services:**
   ```bash
   docker-compose up --build
   ```

4. **Access the applications:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Test API Page: http://localhost:3000/test-api

### Staging Environment

1. **Create `.env.staging` file with staging configuration**

2. **Start staging services:**
   ```bash
   docker-compose -f docker-compose.staging.yml --env-file .env.staging up --build
   ```

   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8001

### Production Environment

1. **Create `.env.production` file with production configuration**

2. **Start production services:**
   ```bash
   docker-compose -f docker-compose.production.yml --env-file .env.production up --build -d
   ```

## Building Individual Images

### Backend (FastAPI)

```bash
docker build -t fasttv-api:latest .
```

Run the container:
```bash
docker run -p 8000:8000 \
  -e MONGO_URL=your_mongodb_url \
  -e DB_NAME=travhoo \
  fasttv-api:latest
```

### Frontend (Next.js)

```bash
cd travhooportal
docker build -t fasttv-web:latest \
  --build-arg NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 .
```

Run the container:
```bash
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 \
  fasttv-web:latest
```

## Docker Compose Commands

### Start services
```bash
docker-compose up
```

### Start in background (detached)
```bash
docker-compose up -d
```

### Rebuild and start
```bash
docker-compose up --build
```

### Stop services
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

### View logs for specific service
```bash
docker-compose logs -f api
docker-compose logs -f web
```

### Execute commands in container
```bash
docker-compose exec api python -m pip list
docker-compose exec web pnpm --version
```

## Environment Variables

### Backend (FastAPI)
- `MONGO_URL`: MongoDB connection string
- `DB_NAME`: Database name (default: `travhoo`)
- `SECRET_KEY`: Secret key for cryptographic operations
- `ALGORITHM`: JWT algorithm (default: `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

### Frontend (Next.js)
- `NEXT_PUBLIC_API_BASE_URL`: Backend API base URL
- `NODE_ENV`: Environment (`development`, `production`)

## Health Checks

Both containers include health checks:
- **Backend**: `GET /health` endpoint
- **Frontend**: HTTP check on port 3000

Check health status:
```bash
docker-compose ps
```

## Troubleshooting

### Port already in use
If ports 3000 or 8000 are already in use, modify the port mappings in `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Change host port
```

### MongoDB connection issues
1. Verify MongoDB URL in `.env` file
2. Check network connectivity from container:
   ```bash
   docker-compose exec api ping your-mongodb-host
   ```

### Frontend can't reach backend
1. Ensure `NEXT_PUBLIC_API_BASE_URL` is set correctly
2. For local development, use `http://localhost:8000`
3. For Docker, use service name: `http://api:8000` (internal) or `http://localhost:8000` (external)

### Rebuild after code changes
```bash
docker-compose up --build --force-recreate
```

## Production Deployment

For production:
1. Use `.env.production` with secure values
2. Never commit `.env` files to version control
3. Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)
4. Enable HTTPS with reverse proxy (nginx, Traefik)
5. Set up monitoring and logging
6. Configure resource limits (already included in `docker-compose.production.yml`)

## Next Steps

- Set up CI/CD pipeline to build and push images
- Configure reverse proxy (nginx) for HTTPS
- Set up container orchestration (Kubernetes, Docker Swarm)
- Implement monitoring and logging solutions

