import os
import shutil

def copy_model():
    print("📁 Setting up model files...")
    
    # Source and destination paths
    source = "backend/models/fake_news_model.joblib"
    destination = "models/fake_news_model.joblib"
    
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    # Copy model file
    if os.path.exists(source):
        shutil.copy2(source, destination)
        print(f"✅ Model copied from {source} to {destination}")
    else:
        print(f"❌ Source model not found at: {source}")
        print("Available files in backend/models/:")
        if os.path.exists("backend/models"):
            for file in os.listdir("backend/models"):
                print(f"  - {file}")
    
    # Also check if we have any model files
    print("Current model files:")
    if os.path.exists("models"):
        for file in os.listdir("models"):
            print(f"  - models/{file}")

if __name__ == "__main__":
    copy_model()