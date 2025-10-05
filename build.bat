@echo off
echo 🚀 Building Fake News Detector for Render...

echo 📦 Installing Python dependencies...
pip install -r requirements.txt

echo 📥 Downloading NLTK data...
python -c "import nltk; nltk.download('stopwords')"

echo ⚛️  Building React app...
cd frontend
call npm install
call npm run build
cd ..

echo 📁 Setting up static files...
if exist static rmdir /s /q static
mkdir static

echo 📋 Copying React build files...
xcopy "frontend\build\*" "static\" /E /I /H /Y

echo ✅ Build completed successfully!
pause