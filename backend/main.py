from fastapi import FastAPI, File, UploadFile, HTTPException, Form
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
        
        # Real analysis based on file contents
        syntax_errors = []
        security_issues = []
        logic_conflicts = []
        secrets_detected = []
        best_practice_suggestions = []
        
        # Analyze Dockerfile if present
        if file_contents.get("dockerfile") and file_contents["dockerfile"].strip():
            dockerfile_content = file_contents["dockerfile"]
            
            # Check for common Dockerfile issues
            if "FROM" not in dockerfile_content:
                syntax_errors.append({
                    "type": "syntax_error",
                    "file": "dockerfile",
                    "message": "Dockerfile missing FROM instruction",
                    "severity": "high",
                    "line": 1
                })
            
            if "latest" in dockerfile_content:
                security_issues.append({
                    "type": "security_issue",
                    "file": "dockerfile",
                    "message": "Using 'latest' tag is not recommended for production",
                    "severity": "medium",
                    "recommendation": "Use specific version tags"
                })
            
            if "root" in dockerfile_content.lower() and "USER" not in dockerfile_content:
                security_issues.append({
                    "type": "security_issue",
                    "file": "dockerfile",
                    "message": "Container runs as root user",
                    "severity": "high",
                    "recommendation": "Add USER instruction to run as non-root"
                })
            
            # Best practices
            if dockerfile_content.count("RUN") > 5:
                best_practice_suggestions.append({
                    "type": "best_practice",
                    "file": "dockerfile",
                    "message": "Consider combining RUN instructions to reduce layers",
                    "severity": "low",
                    "recommendation": "Use && to combine RUN commands"
                })
        
        # Analyze docker-compose if present
        if file_contents.get("docker_compose") and file_contents["docker_compose"].strip():
            compose_content = file_contents["docker_compose"]
            
            # Check for common compose issues
            if "version:" not in compose_content:
                syntax_errors.append({
                    "type": "syntax_error",
                    "file": "docker_compose",
                    "message": "docker-compose.yml missing version",
                    "severity": "medium",
                    "line": 1
                })
            
            if "restart:" not in compose_content:
                security_issues.append({
                    "type": "security_issue",
                    "file": "docker_compose",
                    "message": "Services don't have restart policies",
                    "severity": "medium",
                    "recommendation": "Add restart: always or restart: unless-stopped"
                })
            
            # Check for exposed ports
            if "ports:" in compose_content and "80:" in compose_content:
                best_practice_suggestions.append({
                    "type": "best_practice",
                    "file": "docker_compose",
                    "message": "Port 80 is exposed - consider using non-standard ports in production",
                    "severity": "low",
                    "recommendation": "Use ports like 8080:80 instead of 80:80"
                })
        
        # Analyze .env file if present
        if file_contents.get("env_file") and file_contents["env_file"].strip():
            env_content = file_contents["env_file"]
            
            # Check for secrets in .env
            secret_patterns = ["password", "secret", "key", "token", "api_key"]
            for line in env_content.split('\n'):
                line = line.strip()
                if line and '=' in line:
                    key, value = line.split('=', 1)
                    for pattern in secret_patterns:
                        if pattern.lower() in key.lower() and value and value != '':
                            secrets_detected.append({
                                "type": "secret",
                                "file": "env_file",
                                "message": f"Potential secret found: {key}",
                                "severity": "high",
                                "line": env_content.split('\n').index(line) + 1,
                                "recommendation": "Use environment variables or secret management"
                            })
                            break
            
            # Check for production settings
            if "NODE_ENV=production" in env_content:
                best_practice_suggestions.append({
                    "type": "best_practice",
                    "file": "env_file",
                    "message": "NODE_ENV set to production - good practice!",
                    "severity": "info",
                    "recommendation": "Ensure production environment is properly configured"
                })
        
        # Cross-file analysis
        if (file_contents.get("dockerfile") and file_contents.get("docker_compose") and 
            file_contents["dockerfile"].strip() and file_contents["docker_compose"].strip()):
            
            # Check for port conflicts
            dockerfile_content = file_contents["dockerfile"]
            compose_content = file_contents["docker_compose"]
            
            exposed_ports = []
            for line in dockerfile_content.split('\n'):
                if line.strip().startswith('EXPOSE'):
                    parts = line.split()
                    if len(parts) > 1:
                        exposed_ports.extend(parts[1:])
            
            for port in exposed_ports:
                if f"{port}:" in compose_content:
                    logic_conflicts.append({
                        "type": "logic_conflict",
                        "file": "docker_compose",
                        "message": f"Port {port} exposed in Dockerfile and mapped in docker-compose",
                        "severity": "low",
                        "recommendation": "This is normal, but ensure port mapping is correct"
                    })
        
        # Generate suggested fixes based on actual issues
        suggested_fixes = []
        for issue in syntax_errors + security_issues:
            suggested_fixes.append({
                "issue_id": f"fix_{len(suggested_fixes)}",
                "issue_type": issue.get("type", "unknown"),
                "fix": f"Fix: {issue.get('recommendation', 'Review the issue')}",
                "confidence": 85,
                "reason": f"Based on detected {issue.get('type', 'issue')}: {issue.get('message', '')}",
                "file_affected": issue.get("file", "unknown")
            })
        
        # Dynamic confidence scores based on analysis results
        confidence_scores = [
            {
                "category": "syntax",
                "score": max(0, 100 - len(syntax_errors) * 20),
                "reason": f"Found {len(syntax_errors)} syntax issues"
            },
            {
                "category": "security",
                "score": max(0, 100 - len(security_issues) * 15),
                "reason": f"Found {len(security_issues)} security issues"
            },
            {
                "category": "best_practices",
                "score": max(0, 100 - len(best_practice_suggestions) * 10),
                "reason": f"Found {len(best_practice_suggestions)} best practice suggestions"
            }
        ]
        
        # Dynamic AI explanation based on actual analysis
        total_issues = len(syntax_errors) + len(security_issues) + len(logic_conflicts) + len(secrets_detected)
        ai_explanation = f"Configuration analysis completed. Processed {len([k for k, v in file_contents.items() if v.strip()])} files. Found {total_issues} total issues: {len(syntax_errors)} syntax, {len(security_issues)} security, {len(logic_conflicts)} logic conflicts, and {len(secrets_detected)} potential secrets."
        
        # Dynamic simulation scores based on analysis
        base_score = 85
        if syntax_errors:
            base_score -= len(syntax_errors) * 10
        if security_issues:
            base_score -= len(security_issues) * 5
        if secrets_detected:
            base_score -= len(secrets_detected) * 15
        
        simulation_scores = {
            "overall_readiness": max(0, base_score),
            "build_stability": max(0, base_score - 5 if syntax_errors else base_score),
            "runtime_stability": max(0, base_score - 10 if security_issues else base_score),
            "security_posture": max(0, base_score - 15 if (security_issues or secrets_detected) else base_score)
        }
        
        # Dynamic dependency graph based on actual services
        nodes = []
        edges = []
        
        if file_contents.get("docker_compose") and file_contents["docker_compose"].strip():
            compose_content = file_contents["docker_compose"]
            # Simple parsing for services
            lines = compose_content.split('\n')
            current_service = None
            
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith(' ') and not stripped.startswith('\t') and ':' in stripped:
                    if 'services:' in stripped:
                        continue
                    current_service = stripped.replace(':', '').strip()
                    nodes.append({
                        "id": current_service,
                        "label": current_service,
                        "type": "service"
                    })
            
            # Add file nodes
            for file_type, content in file_contents.items():
                if content.strip():
                    nodes.append({
                        "id": file_type,
                        "label": file_type.replace('_', '.').upper(),
                        "type": "file"
                    })
        
        dependency_graph = {
            "nodes": nodes,
            "edges": edges
        }
        
        # Dynamic risk score based on actual issues
        risk_total = 0
        if syntax_errors:
            risk_total += len(syntax_errors) * 10
        if security_issues:
            risk_total += len(security_issues) * 15
        if secrets_detected:
            risk_total += len(secrets_detected) * 20
        if logic_conflicts:
            risk_total += len(logic_conflicts) * 5
        
        risk_level = "Low" if risk_total < 30 else "Medium" if risk_total < 60 else "High"
        
        risk_score = {
            "overall": risk_total,
            "risk_level": risk_level,
            "breakdown": {
                "syntax_issues": len(syntax_errors),
                "security_issues": len(security_issues),
                "secrets": len(secrets_detected),
                "logic_conflicts": len(logic_conflicts)
            }
        }
        
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
    issue_description: str = Form(...),
    configuration_context: str = Form(...),
    mode: str = Form("devops")
):
    try:
        # Parse the configuration context from JSON string
        import json
        context = json.loads(configuration_context)
        
        # Generate context-aware explanation based on the actual question and context
        explanation = ""
        
        # Analyze the question to provide relevant response
        question_lower = issue_description.lower()
        
        # Check for different types of questions
        if "security" in question_lower or "vulnerability" in question_lower:
            if context.get("security_issues"):
                security_count = len(context["security_issues"])
                explanation = f"I found {security_count} security issue(s) in your configuration. "
                if security_count > 0:
                    top_issue = context["security_issues"][0]
                    explanation += f"The most critical issue is: {top_issue.get('message', 'Unknown security issue')}. "
                    explanation += f"This affects the {top_issue.get('file', 'unknown')} file. "
                    explanation += f"Recommendation: {top_issue.get('recommendation', 'Review security best practices')}."
                else:
                    explanation += "No security issues were detected in your configuration."
            else:
                explanation = "I don't see any security analysis results in the provided context. Please run a scan first to analyze your configuration for security issues."
        
        elif "dockerfile" in question_lower or "docker" in question_lower:
            if context.get("syntax_errors"):
                dockerfile_errors = [e for e in context["syntax_errors"] if e.get("file") == "dockerfile"]
                if dockerfile_errors:
                    explanation = f"Your Dockerfile has {len(dockerfile_errors)} issue(s). "
                    explanation += f"Main issue: {dockerfile_errors[0].get('message', 'Unknown Dockerfile issue')}. "
                    explanation += f"This is a {dockerfile_errors[0].get('severity', 'unknown')} severity issue. "
                    explanation += f"Fix: {dockerfile_errors[0].get('recommendation', 'Review Dockerfile syntax')}."
                else:
                    explanation = "No Dockerfile syntax errors were found."
            else:
                explanation = "No Dockerfile analysis available in the context. Please upload a Dockerfile and run a scan."
        
        elif "port" in question_lower or "expose" in question_lower:
            if context.get("best_practices"):
                port_issues = [bp for bp in context["best_practices"] if "port" in bp.get("message", "").lower()]
                if port_issues:
                    explanation = f"Found {len(port_issues)} port-related issue(s): {port_issues[0].get('message', 'Port configuration issue')}. "
                    explanation += f"Recommendation: {port_issues[0].get('recommendation', 'Review port configuration')}."
                else:
                    explanation = "No port-related issues were detected in your configuration."
            else:
                explanation = "No port analysis available. Please ensure your configuration includes port mappings and run a scan."
        
        elif "secret" in question_lower or "password" in question_lower or "key" in question_lower:
            if context.get("secrets_detected"):
                secrets_count = len(context["secrets_detected"])
                explanation = f"⚠️ Found {secrets_count} potential secret(s) in your configuration! "
                if secrets_count > 0:
                    secret = context["secrets_detected"][0]
                    explanation += f"Secret detected: {secret.get('message', 'Potential secret found')}. "
                    explanation += f"Location: {secret.get('file', 'unknown')} file at line {secret.get('line', 'unknown')}. "
                    explanation += f"⚠️ SECURITY RISK: {secret.get('recommendation', 'Remove secrets from configuration files')}."
                else:
                    explanation += "No secrets were detected, which is good for security!"
            else:
                explanation = "No secrets analysis available. Please upload .env files and run a scan to check for exposed secrets."
        
        elif "risk" in question_lower or "score" in question_lower:
            if context.get("risk_score"):
                risk = context["risk_score"]
                explanation = f"Your configuration has a {risk.get('risk_level', 'Unknown')} risk level with a score of {risk.get('overall', 0)}. "
                breakdown = risk.get('breakdown', {})
                if breakdown:
                    explanation += f"Breakdown: {breakdown.get('syntax_issues', 0)} syntax issues, "
                    explanation += f"{breakdown.get('security_issues', 0)} security issues, "
                    explanation += f"{breakdown.get('secrets', 0)} secrets, "
                    explanation += f"{breakdown.get('logic_conflicts', 0)} logic conflicts. "
                
                if risk.get('risk_level') == 'High':
                    explanation += "🚨 High risk detected! Address critical issues before deployment."
                elif risk.get('risk_level') == 'Medium':
                    explanation += "⚠️ Medium risk. Review and fix issues for better security."
                else:
                    explanation += "✅ Low risk configuration. Good job following best practices!"
            else:
                explanation = "No risk analysis available. Please run a scan first to calculate risk scores."
        
        elif "fix" in question_lower or "how" in question_lower or "solve" in question_lower:
            if context.get("suggested_fixes"):
                fixes = context["suggested_fixes"]
                if fixes:
                    explanation = f"I have {len(fixes)} suggested fix(es) for your issues. "
                    top_fix = fixes[0]
                    explanation += f"Top priority fix: {top_fix.get('fix', 'Review configuration')}. "
                    explanation += f"Confidence: {top_fix.get('confidence', 0)}%. "
                    explanation += f"Reason: {top_fix.get('reason', 'Configuration improvement')}. "
                    explanation += f"File affected: {top_fix.get('file_affected', 'unknown')}."
                else:
                    explanation = "No specific fixes needed. Your configuration looks good!"
            else:
                explanation = "No fixes available. Please run a scan first to generate suggested fixes."
        
        elif "best practice" in question_lower or "improve" in question_lower:
            if context.get("best_practices"):
                practices = context["best_practices"]
                if practices:
                    explanation = f"Found {len(practices)} best practice suggestion(s). "
                    practice = practices[0]
                    explanation += f"Suggestion: {practice.get('message', 'Best practice advice')}. "
                    explanation += f"This is a {practice.get('severity', 'info')} level suggestion. "
                    explanation += f"Recommendation: {practice.get('recommendation', 'Follow best practices')}."
                else:
                    explanation = "Great! No best practice violations detected."
            else:
                explanation = "No best practices analysis available. Please run a scan first."
        
        elif "deploy" in question_lower or "production" in question_lower:
            if context.get("simulation_scores"):
                scores = context["simulation_scores"]
                explanation = f"Deployment readiness analysis: "
                explanation += f"Overall readiness: {scores.get('overall_readiness', 0)}%, "
                explanation += f"Build stability: {scores.get('build_stability', 0)}%, "
                explanation += f"Runtime stability: {scores.get('runtime_stability', 0)}%, "
                explanation += f"Security posture: {scores.get('security_posture', 0)}%. "
                
                if scores.get('overall_readiness', 0) > 80:
                    explanation += " ✅ Your configuration appears ready for production deployment."
                elif scores.get('overall_readiness', 0) > 60:
                    explanation += " ⚠️ Some improvements needed before production deployment."
                else:
                    explanation += " 🚨 Significant issues found. Not recommended for production deployment."
            else:
                explanation = "No deployment simulation available. Please run a scan first to analyze deployment readiness."
        
        else:
            # Generic response for other questions
            total_issues = 0
            if context.get("syntax_errors"):
                total_issues += len(context["syntax_errors"])
            if context.get("security_issues"):
                total_issues += len(context["security_issues"])
            if context.get("secrets_detected"):
                total_issues += len(context["secrets_detected"])
            
            explanation = f"Based on your question about '{issue_description}', I analyzed your configuration and found {total_issues} total issues. "
            
            if total_issues == 0:
                explanation += "Your configuration looks good with no major issues detected!"
            else:
                explanation += "I recommend reviewing the detailed scan results for specific issues and fixes. "
                explanation += "You can ask me about specific topics like security, Dockerfile issues, secrets, or deployment readiness for more detailed help."
        
        return {"explanation": explanation}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
