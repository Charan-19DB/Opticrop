# 🚀 OptiCrop AI – Production Cloud & Local Deployment Guide

This guide covers how to deploy OptiCrop to the cloud or run it locally in a container with persistent SQLite database memory and production WSGI concurrency.

---

## 📋 Table of Contents
1. [Option 1: 1-Click Free Cloud Deployment (Render)](#option-1-render-free-cloud)
2. [Option 2: Railway Deployment](#option-2-railway)
3. [Option 3: Hugging Face Spaces (Free Docker)](#option-3-hugging-face-spaces)
4. [Option 4: Docker & Docker Compose (Local / VPS)](#option-4-docker--docker-compose)
5. [Option 5: Traditional Linux VPS (Ubuntu / Nginx)](#option-5-traditional-vps)

---

## Option 1: Render (Free Cloud)
Render is recommended for hosting OptiCrop for your presentation.

1. Push your repository to **GitHub**:
   ```bash
   git add .
   git commit -m "Deploy OptiCrop v2.0"
   git push origin main
   ```
2. Go to [Render.com](https://render.com) and click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Render automatically detects `render.yaml` or set:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --workers 4 --threads 2 --bind 0.0.0.0:$PORT --timeout 120 app:app`
   - **Health Check Path:** `/health`
5. Click **Create Web Service**. Your public HTTPS URL will be active in ~2 minutes!

---

## Option 2: Railway
1. Go to [Railway.app](https://railway.app).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select your `OptiCrop` repository.
4. Railway automatically detects `railway.json` and spins up the Gunicorn server.
5. In your service settings, generate a domain (e.g. `opticrop.up.railway.app`).

---

## Option 3: Hugging Face Spaces
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces).
2. Click **Create new Space**.
3. Space SDK: Select **Docker** (Blank).
4. Git clone your space repo and push all project files, or link your GitHub repo.
5. Hugging Face will build the provided `Dockerfile` and give you a free, public URL.

---

## Option 4: Docker & Docker Compose (Local or Cloud Server)

### Run with Docker Compose (Recommended)
```bash
# Build and run with SQLite database persistence
docker compose up --build -d

# Check status
docker compose ps

# View live logs
docker compose logs -f

# Access in your browser:
http://localhost:5000
```

### Run with Docker directly:
```bash
# Build Docker image
docker build -t opticrop-ai:latest .

# Run container with mapped port 5000
docker run -d -p 5000:5000 --name opticrop opticrop-ai:latest

# Verify health status
curl http://localhost:5000/health
```

---

## Option 5: Traditional Linux VPS (Ubuntu / Debian)
```bash
# 1. Clone repo and create virtual environment
git clone <your-repo-url>
cd Opticrop-main
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Test running with Gunicorn
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

---

## 🔍 System Verification & Health Check
Verify your deployed instance by accessing the `/health` endpoint:
```bash
curl https://<your-deployed-domain>/health
```
**Expected Response:**
```json
{
  "database": "sqlite_ready",
  "model_loaded": true,
  "service": "OptiCrop Smart Agricultural Optimization Engine",
  "status": "healthy",
  "timestamp": "2026-09-19T18:40:00.000000",
  "total_crops_supported": 22,
  "version": "2.0.0"
}
```
