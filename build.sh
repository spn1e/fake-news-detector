#!/bin/bash

echo "🚀 Building Fake News Detector for Render..."

# Install Python dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('stopwords')"

# Build React app
cd frontend
npm install
npm run build
cd ..

# Copy React build to static directory
mkdir -p static
cp -r frontend/build/* static/

echo "✅ Build completed successfully!"