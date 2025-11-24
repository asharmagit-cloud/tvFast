# Server Deployment Commands

## Clone Repository on DigitalOcean Server

### Step 1: Clone the Repository

```bash
# Clone the repository (not the pull request URL)
cd /var/www
git clone https://github.com/asharmagit-cloud/tvFast.git
cd tvFast
```

### Step 2: Checkout the Deployment Branch

```bash
# Switch to the deployment branch
git checkout deployment

# Verify you're on the correct branch
git branch
```

### Step 3: Alternative - Clone Specific Branch Directly

If you want to clone only the deployment branch:

```bash
cd /var/www
git clone -b deployment https://github.com/asharmagit-cloud/tvFast.git
cd tvFast
```

## If Repository is Private

If the repository is private, you'll need to authenticate:

### Option 1: Using Personal Access Token

```bash
# Clone with token (replace YOUR_TOKEN with your GitHub token)
git clone https://YOUR_TOKEN@github.com/asharmagit-cloud/tvFast.git
cd tvFast
git checkout deployment
```

### Option 2: Using SSH (Recommended)

1. **Generate SSH key on server:**
   ```bash
   ssh-keygen -t ed25519 -C "manishksharma9801@gmail.com"
   cat ~/.ssh/id_ed25519.pub
   ```

2. **Add SSH key to GitHub:**
   - Go to GitHub → Settings → SSH and GPG keys
   - Add the public key

3. **Clone using SSH:**
   ```bash
   cd /var/www
   git clone git@github.com:asharmagit-cloud/tvFast.git
   cd tvFast
   git checkout deployment
   ```

### Option 3: Configure Git Credentials

```bash
# Set up git config
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"

# Clone repository
git clone https://github.com/asharmagit-cloud/tvFast.git
cd tvFast
git checkout deployment
```

## Complete Deployment Process

```bash
# 1. Navigate to web directory
cd /var/www

# 2. Clone repository
git clone https://github.com/asharmagit-cloud/tvFast.git
cd tvFast

# 3. Checkout deployment branch
git checkout deployment

# 4. Set up environment variables
nano .env
# Add your MongoDB URL, SECRET_KEY, etc.

# 5. Set up frontend environment
cd travhooportal
nano .env.local
# Add NEXT_PUBLIC_API_BASE_URL
cd ..

# 6. Deploy with Docker Compose
docker-compose -f docker-compose.production.yml up -d --build

# 7. Check status
docker-compose -f docker-compose.production.yml ps
docker-compose -f docker-compose.production.yml logs
```

## Update Application Later

```bash
cd /var/www/tvFast
git pull origin deployment
docker-compose -f docker-compose.production.yml up -d --build
```


