from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from fake_news_detector import FakeNewsDetector

app = FastAPI(
    title="Fake News Detection API",
    description="AI-powered fake news detection system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class PredictionRequest(BaseModel):
    text: str

class BatchPredictionRequest(BaseModel):
    texts: List[str]

# Initialize model
print("Initializing Fake News Detector...")
detector = None

try:
    # Try multiple model paths
    possible_paths = [
        'models/fake_news_model.joblib',
        'backend/models/fake_news_model.joblib',
        'models/fake_news_model.pkl',
        'backend/models/fake_news_model.pkl',
    ]

    model_loaded = False
    for model_path in possible_paths:
        if os.path.exists(model_path):
            print(f"Found model at: {model_path}")
            try:
                detector = FakeNewsDetector(model_path)
                model_loaded = True
                print("Model loaded successfully!")
                break
            except Exception as e:
                print(f"Error loading {model_path}: {e}")
                continue

    if not model_loaded:
        print("WARNING: No model found, creating fallback...")
        # Create detector with non-existent path to trigger fallback
        detector = FakeNewsDetector('fallback')

except Exception as e:
    print(f"Error during initialization: {e}")
    print("WARNING: Creating fallback detector...")
    try:
        detector = FakeNewsDetector('fallback')
    except:
        detector = None

# API Routes
@app.get("/api")
@app.get("/api/")
async def api_root():
    return {
        "message": "Fake News Detection API",
        "version": "1.0.0",
        "status": "running",
        "model_loaded": detector is not None
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": detector is not None,
        "service": "fake-news-detector"
    }

@app.get("/api/model/info")
async def model_info():
    if detector:
        return detector.get_model_info()
    return {
        "model_type": "No Model",
        "version": "1.0.0",
        "status": "Fallback mode",
        "accuracy": 0.0
    }

@app.post("/api/predict")
async def predict(request: PredictionRequest):
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        if detector:
            result = detector.predict(request.text)
        else:
            # Simple fallback
            result = {
                'prediction': 0,
                'confidence': 0.5,
                'class': 'REAL',
                'probabilities': {'real': 0.5, 'fake': 0.5},
                'note': 'No model loaded - using default response'
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/batch-predict")
async def batch_predict(request: BatchPredictionRequest):
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="Text list cannot be empty")

        results = []
        if detector:
            for text in request.texts:
                result = detector.predict(text)
                results.append(result)
        else:
            # Simple fallback for all texts
            for _ in request.texts:
                results.append({
                    'prediction': 0,
                    'confidence': 0.5,
                    'class': 'REAL',
                    'probabilities': {'real': 0.5, 'fake': 0.5}
                })

        return {
            "success": True,
            "results": results
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Serve static files (React build)
static_dir = os.path.join(os.path.dirname(__file__), 'static')
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Don't serve API routes as static files
        if full_path.startswith("api/") or full_path == "health":
            raise HTTPException(status_code=404, detail="Not found")

        # Try to serve the requested file
        file_path = os.path.join(static_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)

        # Otherwise serve index.html for React routing
        index_path = os.path.join(static_dir, 'index.html')
        if os.path.exists(index_path):
            return FileResponse(index_path)

        raise HTTPException(status_code=404, detail="Not found")

else:
    print("WARNING: Static directory not found. Frontend will not be served.")
    print(f"Expected location: {static_dir}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on http://0.0.0.0:{port}")
    print(f"API Docs: http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port)
