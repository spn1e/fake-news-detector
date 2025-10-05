import pickle
import joblib
import os

def convert_to_pickle():
    """Convert joblib model to pickle format"""
    try:
        print("Attempting to convert model to pickle format...")
        
        # Try to load with joblib first
        artifacts = joblib.load('backend/models/fake_news_model.joblib')
        
        # Save with pickle
        with open('models/fake_news_model.pkl', 'wb') as f:
            pickle.dump(artifacts, f)
        
        print("✅ Model converted to pickle format!")
        return True
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        return False

if __name__ == "__main__":
    convert_to_pickle()