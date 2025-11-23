#!/bin/bash

# FastTV Deployment Script
# This script helps deploy the application to a server

set -e

echo "🚀 FastTV Deployment Script"
echo "============================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Please update .env with your production values!${NC}"
    else
        echo -e "${RED}❌ .env.example not found. Please create .env manually.${NC}"
        exit 1
    fi
fi

# Function to deploy backend
deploy_backend() {
    echo -e "\n${GREEN}📦 Deploying Backend...${NC}"
    
    # Check if Docker is available
    if command -v docker &> /dev/null; then
        echo "Building Docker image..."
        docker build -t fasttv-backend:latest .
        
        echo "Stopping existing container..."
        docker stop fasttv-backend 2>/dev/null || true
        docker rm fasttv-backend 2>/dev/null || true
        
        echo "Starting new container..."
        docker run -d \
            --name fasttv-backend \
            -p 8000:8000 \
            --env-file .env \
            --restart unless-stopped \
            fasttv-backend:latest
        
        echo -e "${GREEN}✅ Backend deployed successfully!${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker not found. Deploying directly...${NC}"
        # Direct deployment logic here
    fi
}

# Function to deploy frontend
deploy_frontend() {
    echo -e "\n${GREEN}📦 Deploying Frontend...${NC}"
    
    cd travhooportal
    
    # Check if .env.local exists
    if [ ! -f .env.local ]; then
        echo -e "${YELLOW}⚠️  .env.local not found. Creating from .env.example...${NC}"
        if [ -f .env.example ]; then
            cp .env.example .env.local
            echo -e "${YELLOW}⚠️  Please update .env.local with your production API URL!${NC}"
        fi
    fi
    
    # Check if Docker is available
    if command -v docker &> /dev/null; then
        echo "Building Docker image..."
        docker build -t fasttv-frontend:latest .
        
        echo "Stopping existing container..."
        docker stop fasttv-frontend 2>/dev/null || true
        docker rm fasttv-frontend 2>/dev/null || true
        
        echo "Starting new container..."
        docker run -d \
            --name fasttv-frontend \
            -p 3000:3000 \
            --env-file .env.local \
            --restart unless-stopped \
            fasttv-frontend:latest
        
        echo -e "${GREEN}✅ Frontend deployed successfully!${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker not found. Building and starting with npm...${NC}"
        npm install
        npm run build
        npm start
    fi
    
    cd ..
}

# Function to deploy with Docker Compose
deploy_compose() {
    echo -e "\n${GREEN}📦 Deploying with Docker Compose...${NC}"
    
    if [ -f docker-compose.production.yml ]; then
        docker-compose -f docker-compose.production.yml up -d --build
        echo -e "${GREEN}✅ Deployment complete!${NC}"
    else
        echo -e "${RED}❌ docker-compose.production.yml not found!${NC}"
        exit 1
    fi
}

# Main menu
echo ""
echo "Select deployment option:"
echo "1) Deploy Backend only"
echo "2) Deploy Frontend only"
echo "3) Deploy Both (Docker Compose)"
echo "4) Deploy Both (Separate)"
echo "5) Exit"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        deploy_backend
        ;;
    2)
        deploy_frontend
        ;;
    3)
        deploy_compose
        ;;
    4)
        deploy_backend
        deploy_frontend
        ;;
    5)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}🎉 Deployment complete!${NC}"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"

