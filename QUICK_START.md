# Quick Start Deployment Guide

This is a simplified guide for quickly deploying your FastTV application.

## Prerequisites

- Docker and Docker Compose installed
- MongoDB connection string
- Domain name (optional)

## Step 1: Set Up Environment Variables

### Backend (.env in root directory)
```bash
MONGO_URL=your_mongodb_connection_string
DB_NAME=travhoo
SECRET_KEY=generate-a-random-32-character-string
ALLOWED_ORIGINS=https://yourdomain.com
ENVIRONMENT=production
```

### Frontend (.env.local in travhooportal directory)
```bash
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com
```

## Step 2: Deploy with Docker Compose

```bash
# Make deploy script executable (Linux/Mac)
chmod +x deploy.sh

# Run deployment
./deploy.sh
# Or directly:
docker-compose -f docker-compose.production.yml up -d --build
```

## Step 3: Verify Deployment

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000
```

## Step 4: Set Up Reverse Proxy (Nginx)

### Install Nginx
```bash
sudo apt-get update
sudo apt-get install nginx
```

### Backend Configuration
Create `/etc/nginx/sites-available/fasttv-api`:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Frontend Configuration
Create `/etc/nginx/sites-available/fasttv-web`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Enable Sites
```bash
sudo ln -s /etc/nginx/sites-available/fasttv-api /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/fasttv-web /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Set Up SSL with Let's Encrypt
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
```

## Alternative: Deploy to Cloud Platforms

### Backend → Railway/Render
1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

### Frontend → Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `cd travhooportal && vercel`
3. Set `NEXT_PUBLIC_API_BASE_URL` in Vercel dashboard

## Troubleshooting

### Check Logs
```bash
# Backend logs
docker logs fasttv-backend

# Frontend logs
docker logs fasttv-frontend

# All services
docker-compose -f docker-compose.production.yml logs
```

### Restart Services
```bash
docker-compose -f docker-compose.production.yml restart
```

### Check Health
```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000
```

## Next Steps

1. Set up monitoring (optional)
2. Configure backups
3. Set up CI/CD pipeline
4. Review security settings
5. Test all endpoints

For detailed information, see [DEPLOYMENT.md](./DEPLOYMENT.md)

