#!/bin/bash

# DigitalOcean Deployment Script for FastTV
# Run this script on your DigitalOcean Droplet

set -e

echo "🚀 FastTV DigitalOcean Deployment"
echo "=================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root or with sudo${NC}"
    exit 1
fi

# Update system
echo -e "\n${GREEN}📦 Updating system...${NC}"
apt update && apt upgrade -y

# Install Docker
if ! command -v docker &> /dev/null; then
    echo -e "\n${GREEN}🐳 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "\n${GREEN}📦 Installing Docker Compose...${NC}"
    apt install docker-compose -y
else
    echo -e "${GREEN}✅ Docker Compose already installed${NC}"
fi

# Install Nginx
if ! command -v nginx &> /dev/null; then
    echo -e "\n${GREEN}🌐 Installing Nginx...${NC}"
    apt install nginx -y
    systemctl enable nginx
    systemctl start nginx
else
    echo -e "${GREEN}✅ Nginx already installed${NC}"
fi

# Install Certbot
if ! command -v certbot &> /dev/null; then
    echo -e "\n${GREEN}🔒 Installing Certbot...${NC}"
    apt install certbot python3-certbot-nginx -y
else
    echo -e "${GREEN}✅ Certbot already installed${NC}"
fi

# Install UFW
if ! command -v ufw &> /dev/null; then
    echo -e "\n${GREEN}🔥 Installing UFW firewall...${NC}"
    apt install ufw -y
else
    echo -e "${GREEN}✅ UFW already installed${NC}"
fi

# Configure firewall
echo -e "\n${GREEN}🔥 Configuring firewall...${NC}"
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo -e "${GREEN}✅ Firewall configured${NC}"

# Check if app directory exists
APP_DIR="/opt/fastTV"
if [ ! -d "$APP_DIR" ]; then
    echo -e "\n${YELLOW}⚠️  App directory not found at $APP_DIR${NC}"
    echo "Please either:"
    echo "1. Clone your repository: git clone https://github.com/yourusername/fastTV.git $APP_DIR"
    echo "2. Or upload files to $APP_DIR"
    read -p "Press Enter after you've set up the app directory..."
fi

# Check for .env file
if [ ! -f "$APP_DIR/.env" ]; then
    echo -e "\n${YELLOW}⚠️  .env file not found${NC}"
    echo "Creating .env file. Please edit it with your values:"
    cat > "$APP_DIR/.env" << EOF
MONGO_URL=your_mongodb_connection_string
DB_NAME=travhoo
SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ENVIRONMENT=production
EOF
    nano "$APP_DIR/.env"
fi

# Check for frontend .env.local
if [ ! -f "$APP_DIR/travhooportal/.env.local" ]; then
    echo -e "\n${YELLOW}⚠️  Frontend .env.local not found${NC}"
    echo "Creating .env.local file. Please edit it with your API URL:"
    cat > "$APP_DIR/travhooportal/.env.local" << EOF
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com
NEXT_PUBLIC_ENVIRONMENT=production
EOF
    nano "$APP_DIR/travhooportal/.env.local"
fi

# Deploy application
echo -e "\n${GREEN}🚀 Deploying application...${NC}"
cd "$APP_DIR"

# Stop existing containers
docker-compose -f docker-compose.production.yml down 2>/dev/null || true

# Build and start
docker-compose -f docker-compose.production.yml up -d --build

# Wait for services to start
echo -e "\n${GREEN}⏳ Waiting for services to start...${NC}"
sleep 10

# Check health
echo -e "\n${GREEN}🏥 Checking service health...${NC}"
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is healthy${NC}"
else
    echo -e "${RED}❌ Frontend health check failed${NC}"
fi

# Set up systemd service for auto-start
echo -e "\n${GREEN}⚙️  Setting up auto-start service...${NC}"
cat > /etc/systemd/system/fasttv.service << EOF
[Unit]
Description=FastTV Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/docker-compose -f docker-compose.production.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.production.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable fasttv

echo -e "\n${GREEN}✅ Auto-start service configured${NC}"

# Nginx configuration prompt
echo -e "\n${YELLOW}📝 Nginx Configuration${NC}"
read -p "Do you want to set up Nginx reverse proxy? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your domain name (e.g., yourdomain.com): " DOMAIN
    read -p "Enter API subdomain (e.g., api): " API_SUBDOMAIN
    
    # Backend Nginx config
    cat > /etc/nginx/sites-available/fasttv-api << EOF
server {
    listen 80;
    server_name ${API_SUBDOMAIN}.${DOMAIN};

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

    # Frontend Nginx config
    cat > /etc/nginx/sites-available/fasttv-web << EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

    # Enable sites
    ln -sf /etc/nginx/sites-available/fasttv-api /etc/nginx/sites-enabled/
    ln -sf /etc/nginx/sites-available/fasttv-web /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload
    nginx -t && systemctl reload nginx
    
    echo -e "\n${GREEN}✅ Nginx configured${NC}"
    echo -e "${YELLOW}⚠️  Don't forget to:${NC}"
    echo "1. Point your DNS to this server's IP"
    echo "2. Run: certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} -d ${API_SUBDOMAIN}.${DOMAIN}"
fi

# Summary
echo -e "\n${GREEN}🎉 Deployment Complete!${NC}"
echo ""
echo "Services:"
echo "  Backend: http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "  Health: http://localhost:8000/health"
echo ""
echo "Useful commands:"
echo "  View logs: docker-compose -f docker-compose.production.yml logs -f"
echo "  Restart: docker-compose -f docker-compose.production.yml restart"
echo "  Stop: docker-compose -f docker-compose.production.yml down"
echo "  Status: docker-compose -f docker-compose.production.yml ps"

