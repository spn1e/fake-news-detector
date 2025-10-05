import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Fake News Detector on port {port}...")
    print(f"Server will be available at http://0.0.0.0:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")