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
    title="ZeroGuard AI",
    description="AI-powered DevOps Configuration Intelligence Platform",
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
    return {"message": "ZeroGuard AI API is running"}

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
        
        # Mock analysis results
        syntax_errors = []
        security_issues = []
        logic_conflicts = []
        secrets_detected = []
        best_practice_suggestions = []
        suggested_fixes = []
        confidence_scores = []
        ai_explanation = "Configuration analysis completed successfully"
        simulation_scores = {"overall_readiness": 85, "build_stability": 90, "runtime_stability": 80, "security_posture": 85}
        dependency_graph = {"nodes": [], "edges": []}
        risk_score = {"overall": 25, "risk_level": "Low", "breakdown": {}}
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        return {
            "syntax_errors": syntax_errors,
            "security_issues": security_issues,
            "logic_conflicts": logic_conflicts,
            "secrets_detected": secrets_detected,
            "best_practices": best_practice_suggestions,
            "suggested_fixes": suggested_fixes,
            "confidence_scores": confidence_scores,
            "ai_explanation": ai_explanation,
            "simulation_scores": simulation_scores,
            "dependency_graph": dependency_graph,
            "risk_score": risk_score
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

@app.post("/explain")
async def explain_issue(
    issue_description: str,
    configuration_context: Dict[str, Any],
    mode: str = "devops"
):
    try:
        explanation = f"This is a mock explanation for: {issue_description}"
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
