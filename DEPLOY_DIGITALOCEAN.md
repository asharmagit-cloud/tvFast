# DigitalOcean Deployment Guide

Complete guide for deploying FastTV application to DigitalOcean.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Option 1: DigitalOcean Droplet (VPS)](#option-1-digitalocean-droplet-vps)
3. [Option 2: DigitalOcean App Platform](#option-2-digitalocean-app-platform)
4. [Database Setup](#database-setup)
5. [Domain Configuration](#domain-configuration)
6. [SSL/HTTPS Setup](#sslhttps-setup)
7. [Monitoring & Maintenance](#monitoring--maintenance)

## Prerequisites

- DigitalOcean account
- Domain name (optional but recommended)
- SSH key pair
- MongoDB database (DigitalOcean Managed Database or external)

## Option 1: DigitalOcean Droplet (VPS)

This option gives you full control and is cost-effective for production.

### Step 1: Create a Droplet

1. **Go to DigitalOcean Dashboard** → Create → Droplets
2. **Choose configuration:**
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: 
     - Minimum: 2GB RAM / 1 vCPU ($12/month) - for testing
     - Recommended: 4GB RAM / 2 vCPU ($24/month) - for production
   - **Datacenter**: Choose closest to your users
   - **Authentication**: SSH keys (recommended) or password
   - **Hostname**: `fasttv-server` (or your preference)
3. **Click "Create Droplet"**

### Step 2: Initial Server Setup

1. **Connect to your Droplet:**
   ```bash
   ssh root@your_droplet_ip
   ```

2. **Update system:**
   ```bash
   apt update && apt upgrade -y
   ```

3. **Install Docker and Docker Compose:**
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Install Docker Compose
   apt install docker-compose -y
   
   # Add your user to docker group (if not using root)
   usermod -aG docker $USER
   
   # Verify installation
   docker --version
   docker-compose --version
   ```

4. **Install Nginx (for reverse proxy):**
   ```bash
   apt install nginx -y
   systemctl enable nginx
   systemctl start nginx
   ```

5. **Install Git:**
   ```bash
   apt install git -y
   ```

### Step 3: Deploy Application

1. **Clone your repository:**
   ```bash
   cd /opt
   git clone https://github.com/yourusername/fastTV.git
   cd fastTV
   ```

   Or upload files via SCP:
   ```bash
   # From your local machine
   scp -r . root@your_droplet_ip:/opt/fastTV
   ```

2. **Set up environment variables:**
   ```bash
   cd /opt/fastTV
   nano .env
   ```
   
   Add your production values:
   ```env
   MONGO_URL=your_mongodb_connection_string
   DB_NAME=travhoo
   SECRET_KEY=your-super-secret-key-min-32-chars
   ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ENVIRONMENT=production
   ```

3. **Set up frontend environment:**
   ```bash
   cd /opt/fastTV/travhooportal
   nano .env.local
   ```
   
   Add:
   ```env
   NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com
   NEXT_PUBLIC_ENVIRONMENT=production
   ```

4. **Deploy with Docker Compose:**
   ```bash
   cd /opt/fastTV
   docker-compose -f docker-compose.production.yml up -d --build
   ```

5. **Verify services are running:**
   ```bash
   docker ps
   docker-compose -f docker-compose.production.yml logs
   ```

### Step 4: Configure Nginx Reverse Proxy

1. **Create backend configuration:**
   ```bash
   nano /etc/nginx/sites-available/fasttv-api
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name api.yourdomain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

2. **Create frontend configuration:**
   ```bash
   nano /etc/nginx/sites-available/fasttv-web
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;

       location / {
           proxy_pass http://localhost:3000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

3. **Enable sites:**
   ```bash
   ln -s /etc/nginx/sites-available/fasttv-api /etc/nginx/sites-enabled/
   ln -s /etc/nginx/sites-available/fasttv-web /etc/nginx/sites-enabled/
   
   # Test configuration
   nginx -t
   
   # Reload Nginx
   systemctl reload nginx
   ```

### Step 5: Set Up SSL with Let's Encrypt

1. **Install Certbot:**
   ```bash
   apt install certbot python3-certbot-nginx -y
   ```

2. **Get SSL certificates:**
   ```bash
   certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
   ```

3. **Auto-renewal is set up automatically. Test it:**
   ```bash
   certbot renew --dry-run
   ```

### Step 6: Set Up Firewall

```bash
# Install UFW
apt install ufw -y

# Allow SSH
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

### Step 7: Set Up Auto-restart on Reboot

Create a systemd service for Docker Compose:

```bash
nano /etc/systemd/system/fasttv.service
```

Add:
```ini
[Unit]
Description=FastTV Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/fastTV
ExecStart=/usr/bin/docker-compose -f docker-compose.production.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.production.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl daemon-reload
systemctl enable fasttv
systemctl start fasttv
```

## Option 2: DigitalOcean App Platform

Easier deployment with automatic scaling and SSL.

### Step 1: Prepare Your Repository

1. **Ensure your code is on GitHub/GitLab/Bitbucket**
2. **Create `app.yaml` in root directory:**

```yaml
name: fasttv
services:
  - name: backend
    source_dir: /
    github:
      repo: yourusername/fastTV
      branch: main
    run_command: uvicorn main:app --host 0.0.0.0 --port $PORT
    environment_slug: python
    instance_count: 1
    instance_size_slug: basic-xxs
    http_port: 8000
    routes:
      - path: /
    envs:
      - key: MONGO_URL
        scope: RUN_TIME
        value: ${MONGO_URL}
      - key: DB_NAME
        scope: RUN_TIME
        value: travhoo
      - key: SECRET_KEY
        scope: RUN_TIME
        value: ${SECRET_KEY}
      - key: ALLOWED_ORIGINS
        scope: RUN_TIME
        value: ${ALLOWED_ORIGINS}
    health_check:
      http_path: /health
      initial_delay_seconds: 10
      period_seconds: 10
      timeout_seconds: 5
      success_threshold: 1
      failure_threshold: 3

  - name: frontend
    source_dir: /travhooportal
    github:
      repo: yourusername/fastTV
      branch: main
    build_command: npm install && npm run build
    run_command: npm start
    environment_slug: node-js
    instance_count: 1
    instance_size_slug: basic-xxs
    http_port: 3000
    routes:
      - path: /
    envs:
      - key: NEXT_PUBLIC_API_BASE_URL
        scope: RUN_AND_BUILD_TIME
        value: ${NEXT_PUBLIC_API_BASE_URL}
```

### Step 2: Deploy to App Platform

1. **Go to DigitalOcean Dashboard** → Apps → Create App
2. **Connect your repository**
3. **DigitalOcean will detect `app.yaml`** or configure manually:
   - **Backend Service:**
     - Source: Your repository root
     - Build Command: `pip install -r requirements.txt`
     - Run Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - Environment: Python
   - **Frontend Service:**
     - Source: `travhooportal` directory
     - Build Command: `npm install && npm run build`
     - Run Command: `npm start`
     - Environment: Node.js
4. **Set environment variables** in App Platform dashboard
5. **Click "Create Resources"**

### Step 3: Configure Custom Domain

1. **In App Platform dashboard** → Settings → Domains
2. **Add your domain**
3. **Update DNS records** as instructed
4. **SSL is automatically configured**

## Database Setup

### Option A: DigitalOcean Managed MongoDB

1. **Create Database:**
   - Go to Databases → Create Database
   - Choose MongoDB
   - Select region (same as your Droplet/App)
   - Choose plan (minimum $15/month)
   - Create database

2. **Get Connection String:**
   - Go to database dashboard
   - Click "Connection Details"
   - Copy connection string
   - Update `MONGO_URL` in your `.env`

3. **Configure Trusted Sources:**
   - Add your Droplet IP or App Platform component

### Option B: MongoDB Atlas (External)

1. **Create cluster on MongoDB Atlas**
2. **Get connection string**
3. **Whitelist DigitalOcean IPs:**
   - Add your Droplet IP
   - Or use `0.0.0.0/0` for App Platform (less secure)

## Domain Configuration

### Step 1: Point Domain to DigitalOcean

1. **In DigitalOcean Dashboard** → Networking → Domains
2. **Add your domain**
3. **Add DNS records:**
   - **A Record**: `@` → Your Droplet IP
   - **A Record**: `api` → Your Droplet IP
   - **CNAME**: `www` → `@`

### Step 2: Update Environment Variables

Update `ALLOWED_ORIGINS` and `NEXT_PUBLIC_API_BASE_URL` with your domain.

## Monitoring & Maintenance

### Set Up Monitoring

1. **DigitalOcean Monitoring:**
   - Enable in Droplet settings
   - Set up alerts for CPU, RAM, Disk

2. **Application Monitoring:**
   ```bash
   # View logs
   docker-compose -f docker-compose.production.yml logs -f
   
   # View specific service logs
   docker logs fasttv-backend -f
   docker logs fasttv-frontend -f
   ```

### Backup Strategy

1. **Database Backups:**
   - DigitalOcean Managed DB: Automatic daily backups
   - MongoDB Atlas: Automatic backups
   - Manual: Use `mongodump`

2. **Application Backups:**
   ```bash
   # Backup environment files
   tar -czf backup-$(date +%Y%m%d).tar.gz .env travhooportal/.env.local
   ```

### Update Application

```bash
# SSH into server
ssh root@your_droplet_ip

# Navigate to app directory
cd /opt/fastTV

# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.production.yml up -d --build

# Check status
docker-compose -f docker-compose.production.yml ps
```

### Useful Commands

```bash
# View running containers
docker ps

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Restart services
docker-compose -f docker-compose.production.yml restart

# Stop services
docker-compose -f docker-compose.production.yml down

# Check disk space
df -h

# Check memory usage
free -h

# Check system resources
htop
```

## Troubleshooting

### Services Not Starting

```bash
# Check logs
docker-compose -f docker-compose.production.yml logs

# Check container status
docker ps -a

# Restart services
docker-compose -f docker-compose.production.yml restart
```

### Database Connection Issues

1. **Check MongoDB connection string**
2. **Verify firewall rules**
3. **Check network connectivity:**
   ```bash
   # Test MongoDB connection
   docker exec -it fasttv-backend python -c "from database import connect_to_mongo; import asyncio; asyncio.run(connect_to_mongo())"
   ```

### Nginx Issues

```bash
# Test configuration
nginx -t

# Check error logs
tail -f /var/log/nginx/error.log

# Reload Nginx
systemctl reload nginx
```

### SSL Certificate Issues

```bash
# Check certificate status
certbot certificates

# Renew manually
certbot renew

# Check renewal logs
tail -f /var/log/letsencrypt/letsencrypt.log
```

## Cost Estimation

### Droplet Option:
- **Droplet**: $12-24/month (depending on size)
- **Managed MongoDB**: $15/month (optional)
- **Domain**: ~$12/year
- **Total**: ~$27-39/month

### App Platform Option:
- **Backend**: $5-12/month
- **Frontend**: $5-12/month
- **Managed MongoDB**: $15/month (optional)
- **Domain**: ~$12/year
- **Total**: ~$25-39/month

## Security Checklist

- [ ] Change default SSH port (optional)
- [ ] Set up SSH keys (disable password auth)
- [ ] Configure firewall (UFW)
- [ ] Use strong SECRET_KEY
- [ ] Enable SSL/HTTPS
- [ ] Restrict CORS to your domain
- [ ] Set up MongoDB authentication
- [ ] Regular security updates
- [ ] Enable DigitalOcean monitoring
- [ ] Set up automated backups

## Next Steps

1. Deploy following one of the options above
2. Test all endpoints
3. Set up monitoring alerts
4. Configure automated backups
5. Set up CI/CD pipeline (optional)
6. Review and optimize performance

For issues, check:
- Application logs
- Nginx logs
- DigitalOcean monitoring
- Database connection status

