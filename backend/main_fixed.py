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
        
        # Save uploaded files temporarily, set empty string if not provided
        try:
            if dockerfile:
                dockerfile_path = os.path.join(temp_dir, "Dockerfile")
                dockerfile_content = await dockerfile.read()
                with open(dockerfile_path, "wb") as f:
                    f.write(dockerfile_content)
                try:
                    file_contents["dockerfile"] = dockerfile_content.decode("utf-8")
                except (UnicodeDecodeError, Exception):
                    file_contents["dockerfile"] = dockerfile_content.decode("utf-8", errors="ignore")
            else:
                file_contents["dockerfile"] = ""
            
            if docker_compose:
                compose_path = os.path.join(temp_dir, "docker-compose.yml")
                docker_compose_content = await docker_compose.read()
                with open(compose_path, "wb") as f:
                    f.write(docker_compose_content)
                try:
                    file_contents["docker_compose"] = docker_compose_content.decode("utf-8")
                except (UnicodeDecodeError, Exception):
                    file_contents["docker_compose"] = docker_compose_content.decode("utf-8", errors="ignore")
            else:
                file_contents["docker_compose"] = ""
            
            if env_file:
                env_path = os.path.join(temp_dir, ".env")
                env_file_content = await env_file.read()
                with open(env_path, "wb") as f:
                    f.write(env_file_content)
                try:
                    file_contents["env_file"] = env_file_content.decode("utf-8")
                except (UnicodeDecodeError, Exception):
                    file_contents["env_file"] = env_file_content.decode("utf-8", errors="ignore")
            else:
                file_contents["env_file"] = ""
        except Exception as e:
            # If any file reading fails, set all to empty strings
            file_contents = {
                "dockerfile": "",
                "docker_compose": "",
                "env_file": ""
            }
            print(f"File reading error: {e}")
        
        # Mock analysis results (without OpenAI)
        syntax_errors = []
        security_issues = []
        logic_conflicts = []
        secrets_detected = []
        best_practice_suggestions = []
        suggested_fixes = []
        confidence_scores = []
        ai_explanation = f"Configuration analysis completed. Files processed: {list(file_contents.keys())}"
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
    uvicorn.run(app, host="0.0.0.0", port=8003)
