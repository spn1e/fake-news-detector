# Multi-stage build for combined frontend + backend

# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --silent || npm install --legacy-peer-deps --silent
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend with static frontend
FROM python:3.11-slim
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('stopwords')"

# Copy backend code
COPY backend/ ./backend/
COPY main.py waitress-serve.py ./

# Copy frontend build from previous stage
COPY --from=frontend-build /app/frontend/build ./static

# Create models directory and copy model files
RUN mkdir -p models
COPY backend/models/*.pkl models/ 2>/dev/null || true
COPY backend/models/*.joblib models/ 2>/dev/null || true

# Expose port (Render will set PORT env variable)
EXPOSE 10000

# Start the application
CMD ["python", "waitress-serve.py"]
