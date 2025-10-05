@echo off
echo Fixing Backend Dependencies...
echo.

echo Step 1: Creating virtual environment...
python -m venv venv

echo Step 2: Activating virtual environment...
call venv\Scripts\activate

echo Step 3: Installing requirements...
pip install --upgrade pip
pip install fastapi==0.104.1 uvicorn==0.24.0 joblib==1.3.2 scikit-learn==1.3.0 nltk==3.8.1 numpy==1.24.3 pydantic==2.5.0 python-multipart==0.0.6

echo Step 4: Starting server...
python app.py

pause