# Deployment Guide for FastTV Application

This guide covers deploying both the FastAPI backend and Next.js frontend to production.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Variables](#environment-variables)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Database Setup](#database-setup)
6. [Production Configuration](#production-configuration)
7. [Deployment Options](#deployment-options)
8. [Post-Deployment Checklist](#post-deployment-checklist)

## Prerequisites

- Python 3.12+
- Node.js 20+ and npm/pnpm
- MongoDB database (local or cloud)
- Server with Docker (optional but recommended)
- Domain name (optional)

## Environment Variables

### Backend Environment Variables

Create a `.env` file in the root directory:

```env
# MongoDB Configuration
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=travhoo

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production

# CORS (comma-separated list of allowed origins)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Frontend Environment Variables

Create a `.env.local` file in the `travhooportal` directory:

```env
# API Base URL
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com

# Environment
NEXT_PUBLIC_ENVIRONMENT=production
```

## Backend Deployment

### Option 1: Docker Deployment (Recommended)

1. **Build the Docker image:**
   ```bash
   docker build -t fasttv-backend:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name fasttv-backend \
     -p 8000:8000 \
     --env-file .env \
     --restart unless-stopped \
     fasttv-backend:latest
   ```

3. **Using Docker Compose:**
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

### Option 2: Direct Server Deployment

1. **Install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up systemd service** (Linux):
   Create `/etc/systemd/system/fasttv-backend.service`:
   ```ini
   [Unit]
   Description=FastTV Backend API
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/path/to/fastTV
   Environment="PATH=/path/to/fastTV/venv/bin"
   ExecStart=/path/to/fastTV/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Start the service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable fasttv-backend
   sudo systemctl start fasttv-backend
   ```

### Option 3: Cloud Platform Deployment

#### Railway
1. Connect your GitHub repository
2. Set environment variables in Railway dashboard
3. Railway will auto-detect and deploy

#### Render
1. Create a new Web Service
2. Connect your repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

#### Heroku
1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. Deploy:
   ```bash
   heroku create your-app-name
   heroku config:set MONGO_URL=your_mongo_url
   git push heroku main
   ```

## Frontend Deployment

### Option 1: Vercel (Recommended for Next.js)

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Deploy:**
   ```bash
   cd travhooportal
   vercel
   ```

3. **Set environment variables in Vercel dashboard:**
   - `NEXT_PUBLIC_API_BASE_URL`

4. **Or use GitHub integration:**
   - Connect repository to Vercel
   - Set environment variables
   - Auto-deploy on push

### Option 2: Docker Deployment

1. **Build the image:**
   ```bash
   cd travhooportal
   docker build -t fasttv-frontend:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name fasttv-frontend \
     -p 3000:3000 \
     -e NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com \
     --restart unless-stopped \
     fasttv-frontend:latest
   ```

### Option 3: Static Export (Alternative)

1. **Update `next.config.ts`:**
   ```typescript
   const nextConfig: NextConfig = {
     output: 'export',
     trailingSlash: true,
   };
   ```

2. **Build:**
   ```bash
   cd travhooportal
   npm run build
   ```

3. **Deploy the `out` folder to any static hosting:**
   - Netlify
   - AWS S3 + CloudFront
   - GitHub Pages
   - Any web server (nginx, Apache)

### Option 4: Self-Hosted with PM2

1. **Build the application:**
   ```bash
   cd travhooportal
   npm run build
   ```

2. **Install PM2:**
   ```bash
   npm install -g pm2
   ```

3. **Create `ecosystem.config.js`:**
   ```javascript
   module.exports = {
     apps: [{
       name: 'fasttv-frontend',
       script: 'node_modules/next/dist/bin/next',
       args: 'start',
       cwd: '/path/to/travhooportal',
       instances: 2,
       exec_mode: 'cluster',
       env: {
         NODE_ENV: 'production',
         PORT: 3000,
         NEXT_PUBLIC_API_BASE_URL: 'https://api.yourdomain.com'
       }
     }]
   };
   ```

4. **Start with PM2:**
   ```bash
   pm2 start ecosystem.config.js
   pm2 save
   pm2 startup
   ```

## Database Setup

### MongoDB Atlas (Cloud)

1. Create account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a cluster
3. Create database user
4. Whitelist your server IP addresses
5. Get connection string
6. Update `MONGO_URL` in environment variables

### Self-Hosted MongoDB

1. **Install MongoDB:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install mongodb

   # Or use Docker
   docker run -d \
     --name mongodb \
     -p 27017:27017 \
     -v mongodb_data:/data/db \
     mongo:latest
   ```

2. **Connection string:**
   ```
   mongodb://localhost:27017/travhoo
   ```

## Production Configuration

### Backend Production Settings

Update `main.py` for production:

```python
# Update CORS to allow only your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),  # From env
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Use production server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # Adjust based on server
        log_level="info"
    )
```

### Security Checklist

- [ ] Change `SECRET_KEY` to a strong random string
- [ ] Update CORS to only allow your frontend domain
- [ ] Use HTTPS (SSL/TLS certificates)
- [ ] Set up firewall rules
- [ ] Enable MongoDB authentication
- [ ] Use environment variables for all secrets
- [ ] Disable API docs in production (optional):
  ```python
  docs_url=None,
  redoc_url=None,
  ```

### Reverse Proxy (Nginx)

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

Enable SSL with Let's Encrypt:
```bash
sudo certbot --nginx -d api.yourdomain.com
```

## Deployment Options

### Full Stack on Single Server

1. Backend: Port 8000
2. Frontend: Port 3000
3. Nginx reverse proxy for both
4. MongoDB on same server or separate

### Separate Servers

1. Backend server: API only
2. Frontend server: Next.js app
3. Database server: MongoDB (or Atlas)

### Serverless/Cloud

1. Backend: Railway/Render/Heroku
2. Frontend: Vercel/Netlify
3. Database: MongoDB Atlas

## Post-Deployment Checklist

- [ ] Test API endpoints
- [ ] Test frontend pages
- [ ] Verify CORS is working
- [ ] Check database connections
- [ ] Set up monitoring (optional)
- [ ] Set up logging
- [ ] Configure backups
- [ ] Set up SSL certificates
- [ ] Test error handling
- [ ] Verify environment variables
- [ ] Check server resources (CPU, RAM, Disk)
- [ ] Set up automated deployments (CI/CD)

## Monitoring and Logging

### Backend Logging

Add logging configuration in `main.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Health Check Endpoint

Add to `main.py`:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if db.database else "disconnected"
    }
```

## Troubleshooting

### Common Issues

1. **CORS errors:**
   - Check `ALLOWED_ORIGINS` in backend
   - Verify frontend URL matches

2. **Database connection:**
   - Check MongoDB URL
   - Verify network access
   - Check firewall rules

3. **Port conflicts:**
   - Change ports in configuration
   - Check what's using the ports

4. **Environment variables:**
   - Verify `.env` files are loaded
   - Check variable names match

## Support

For issues, check:
- Application logs
- Server logs
- Database logs
- Browser console (frontend)

