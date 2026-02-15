from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import json
import os
from pathlib import Path
import tempfile
import shutil

app = FastAPI(
    title="ZeroGuard AI Test",
    description="Test API for file upload",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "ZeroGuard AI Test API is running"}

@app.post("/scan")
async def scan_configuration(
    dockerfile: UploadFile = File(None),
    docker_compose: UploadFile = File(None),
    env_file: UploadFile = File(None),
    mode: str = "devops"
):
    try:
        temp_dir = tempfile.mkdtemp()
        file_contents = {}
        
        # Save uploaded files temporarily
        if dockerfile:
            dockerfile_path = os.path.join(temp_dir, "Dockerfile")
            with open(dockerfile_path, "wb") as f:
                shutil.copyfileobj(dockerfile.file, f)
            file_contents["dockerfile"] = (await dockerfile.read()).decode("utf-8")
        
        if docker_compose:
            compose_path = os.path.join(temp_dir, "docker-compose.yml")
            with open(compose_path, "wb") as f:
                shutil.copyfileobj(docker_compose.file, f)
            file_contents["docker_compose"] = (await docker_compose.read()).decode("utf-8")
        
        if env_file:
            env_path = os.path.join(temp_dir, ".env")
            with open(env_path, "wb") as f:
                shutil.copyfileobj(env_file.file, f)
            file_contents["env_file"] = (await env_file.read()).decode("utf-8")
        
        # Simple test response
        response = {
            "message": "Files uploaded successfully",
            "files": list(file_contents.keys()),
            "mode": mode
        }
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
