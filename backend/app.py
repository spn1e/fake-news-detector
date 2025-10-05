from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import joblib
import os
import uvicorn
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
print("🚀 Initializing Fake News Detector...")
try:
    model_path = os.path.join(os.path.dirname(__file__), 'models/fake_news_model.joblib')
    detector = FakeNewsDetector(model_path)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("⚠️  Using fallback mode")
    detector = None

@app.get("/")
async def root():
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

@app.get("/model/info")
async def model_info():
    if detector:
        return detector.get_model_info()
    return {
        "model_type": "Fallback Mode",
        "version": "1.0.0",
        "status": "No model loaded - using fallback",
        "accuracy": 0.75
    }

@app.post("/predict")
async def predict(request: PredictionRequest):
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if detector:
            result = detector.predict(request.text)
        else:
            # Fallback prediction
            result = {
                'prediction': 0,
                'confidence': 0.7,
                'class': 'REAL',
                'probabilities': {'real': 0.7, 'fake': 0.3},
                'note': 'Using fallback mode - train model in Colab'
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

if __name__ == "__main__":
    print("📍 Starting server on http://0.0.0.0:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)