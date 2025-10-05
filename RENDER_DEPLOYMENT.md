# Render Deployment Guide

## Files Fixed for Render Deployment

### 1. ✅ `main.py` - Main Application Entry Point
- Created complete FastAPI application
- Serves both API endpoints (`/api/*`) and static frontend files
- Handles multiple model paths (fallback support)
- Auto-detects PORT from environment
- Serves React app for all non-API routes

### 2. ✅ `render.yaml` - Render Configuration
- Updated Python version to 3.11
- Improved build command with better logging
- Uses `npm ci --only=production` for faster, reliable builds
- Proper static file setup

### 3. ✅ `.renderignore` - Exclude Unnecessary Files
- Excludes large directories (venv, node_modules)
- Excludes Docker files (not needed on Render)

### 4. ✅ `waitress-serve.py` - Production Server
- Already configured correctly
- Uses Waitress WSGI server (production-ready)
- Reads PORT from environment

## Key Differences Between Docker and Render

| Aspect | Docker Setup | Render Setup |
|--------|--------------|--------------|
| **Architecture** | Multi-container (backend + frontend + nginx) | Single service (monolithic) |
| **Static Files** | Served by Nginx | Served by FastAPI |
| **API Endpoints** | `http://backend:8000/...` | `/api/...` |
| **Environment** | Isolated containers | Single Python environment |
| **Build Process** | Multiple Dockerfiles | Single buildCommand |

## Deployment Steps

### Option 1: Blueprint (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push
   ```

2. **Create New Web Service on Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Connect your repository
   - Render will auto-detect `render.yaml`

### Option 2: Manual Setup

1. **Create Web Service**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your repository

2. **Configure Settings**
   - **Name**: `fake-news-detector`
   - **Environment**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python -c "import nltk; nltk.download('stopwords')" && mkdir -p models && cp backend/models/fake_news_model.joblib models/ || true && cd frontend && npm ci --only=production && npm run build && cd .. && mkdir -p static && cp -r frontend/build/* static/
     ```
   - **Start Command**: `python waitress-serve.py`
   - **Plan**: Free

3. **Environment Variables**
   - `PYTHON_VERSION`: `3.11`

4. **Advanced Settings**
   - **Health Check Path**: `/health`

## Expected Build Process

```
1. Installing Python dependencies... (~2 min)
2. Downloading NLTK data... (~30 sec)
3. Setting up models directory...
4. Building React frontend... (~3-5 min)
5. Copying static files...
6. Starting server...
```

**Total build time**: ~5-8 minutes on first deploy

## Endpoints After Deployment

- **Frontend**: `https://your-app.onrender.com/`
- **Health Check**: `https://your-app.onrender.com/health`
- **API Docs**: `https://your-app.onrender.com/docs`
- **API Root**: `https://your-app.onrender.com/api`
- **Predict**: `https://your-app.onrender.com/api/predict` (POST)

## Troubleshooting

### Build Fails

**Check Python Version**
```bash
python --version
```
Should be 3.11.x

**Check Node Version**
```bash
node --version
```
Should be 18.x or higher

### Model Not Loading

The app has fallback mode if model files aren't found. Check logs:
```
⚠️  No model found, creating fallback...
```

This is OK for testing. The app will still work with reduced accuracy.

### Static Files Not Serving

Check build logs for:
```
📂 Copying static files...
```

Verify `static/` directory exists with `index.html`

### Health Check Failing

The app should respond to `/health` within 30 seconds of starting.
Check logs for:
```
🚀 Starting Fake News Detector on port 10000...
```

## Performance Tips

1. **Free Tier Limitations**
   - Service spins down after 15 minutes of inactivity
   - First request after spin-down takes ~1 minute
   - Use a cron job or UptimeRobot for keep-alive pings

2. **Optimize Build Time**
   - Frontend `node_modules` are cached between deploys
   - Python packages are cached
   - Model files persist after first build

3. **Memory Usage**
   - Free tier: 512 MB RAM
   - scikit-learn model: ~50-100 MB
   - Should fit comfortably

## Testing Locally Before Deploy

```bash
# Build frontend
cd frontend
npm install
npm run build
cd ..

# Copy to static
mkdir -p static
cp -r frontend/build/* static/

# Run server
python waitress-serve.py
```

Visit http://localhost:10000

## Production Checklist

- [x] `main.py` created with FastAPI app + static serving
- [x] `render.yaml` configured correctly
- [x] `.renderignore` excludes unnecessary files
- [x] `requirements.txt` has all dependencies
- [x] `waitress-serve.py` uses PORT environment variable
- [x] Model files exist in `backend/models/`
- [x] Frontend uses `/api` prefix for production
- [ ] Test local build process
- [ ] Push to GitHub
- [ ] Deploy on Render
- [ ] Test health endpoint
- [ ] Test frontend UI
- [ ] Test prediction functionality

## Common Issues Fixed

### ✅ Issue 1: `waitress-serve.py` imports non-existent app
**Before**: `from main import app` (main.py had no app)
**After**: Proper FastAPI app in main.py

### ✅ Issue 2: Separate backend/frontend architecture
**Before**: Docker multi-container setup
**After**: Monolithic app serving both API and static files

### ✅ Issue 3: Model path resolution
**Before**: Hardcoded path
**After**: Tries multiple paths with fallback

### ✅ Issue 4: Static file serving
**Before**: Nginx
**After**: FastAPI StaticFiles + FileResponse

## Support

If deployment fails, check Render logs:
- Dashboard → Your Service → Logs
- Look for errors in red
- Common issues: dependency conflicts, build timeouts, out of memory

Good luck with your deployment! 🚀
