import os
import subprocess
import shutil
import sys

def run_command(command, shell=False, cwd=None):
    """Run a command and handle errors"""
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=True, cwd=cwd)
        else:
            result = subprocess.run(command, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print(f"Error: {e}")
        return False

def main():
    print("🚀 Building Fake News Detector for Render...")
    
    # Install Python dependencies
    print("📦 Installing Python dependencies...")
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]):
        return False
    
    # Download NLTK data
    print("📥 Downloading NLTK data...")
    if not run_command([sys.executable, "-c", "import nltk; nltk.download('stopwords')"]):
        return False
    
    # Copy model files
    print("🤖 Copying model files...")
    os.makedirs("models", exist_ok=True)
    
    # Copy from backend/models to models/
    if os.path.exists("backend/models/fake_news_model.joblib"):
        shutil.copy2("backend/models/fake_news_model.joblib", "models/")
        print("✅ Model copied to models/ directory")
    else:
        print("⚠️ Model file not found in backend/models/")
        print("Available files:")
        for root, dirs, files in os.walk("."):
            for file in files:
                if "model" in file.lower() or "joblib" in file or "pkl" in file:
                    print(f"  - {os.path.join(root, file)}")
    
    # Build React app
    print("⚛️  Building React app...")
    
    # Install npm dependencies
    print("Installing npm dependencies...")
    if not run_command("npm install", shell=True, cwd="frontend"):
        return False
    
    # Build React app
    print("Building React app...")
    if not run_command("npm run build", shell=True, cwd="frontend"):
        return False
    
    # Create static directory
    print("📁 Setting up static files...")
    if os.path.exists("static"):
        shutil.rmtree("static")
    os.makedirs("static", exist_ok=True)
    
    # Copy React build
    print("📋 Copying React build files...")
    build_dir = "frontend/build"
    if os.path.exists(build_dir):
        for item in os.listdir(build_dir):
            src = os.path.join(build_dir, item)
            dst = os.path.join("static", item)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        print(f"✅ Copied {len(os.listdir(build_dir))} items to static/")
    else:
        print("❌ React build directory not found!")
        return False
    
    print("✅ Build completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)