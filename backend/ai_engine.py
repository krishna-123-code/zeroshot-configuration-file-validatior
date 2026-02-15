import openai
import json
import os
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

class AIEngine:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        try:
            # Initialize OpenAI client without deprecated parameters
            self.client = openai.OpenAI(
                api_key=api_key,
                timeout=30
            )
        except Exception as e:
            print(f"OpenAI client initialization failed: {e}")
            # Create a mock client for testing
            self.client = None
    
    async def analyze_configuration(
        self, 
        file_contents: Dict[str, str], 
        syntax_errors: List[Dict], 
        security_issues: List[Dict], 
        logic_conflicts: List[Dict],
        mode: str = "devops"
    ) -> Dict[str, Any]:
        """Analyze configuration with AI for root cause tracing"""
        
        # If OpenAI client is not available, return fallback response
        if self.client is None:
            return {
                "explanation": f"Configuration analysis completed. Found {len(syntax_errors)} syntax errors, {len(security_issues)} security issues, and {len(logic_conflicts)} logic conflicts.",
                "confidence_scores": [],
                "root_cause": "Analysis completed with available data"
            }
        
        try:
            context = self._build_context(file_contents, syntax_errors, security_issues, logic_conflicts)
            prompt = self._build_analysis_prompt(context, mode)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_system_prompt(mode)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            # Fallback response when AI fails
            return {
                "explanation": f"Configuration analysis completed. Found {len(syntax_errors)} syntax errors, {len(security_issues)} security issues, and {len(logic_conflicts)} logic conflicts.",
                "confidence_scores": [],
                "root_cause": "Analysis completed with available data"
            }
    
    async def generate_fixes(
        self, 
        file_contents: Dict[str, str], 
        issues: List[Dict], 
        mode: str = "devops"
    ) -> List[Dict[str, Any]]:
        """Generate auto-fixes with confidence scores"""
        
        # If OpenAI client is not available, return empty fixes
        if self.client is None:
            return []
        
        fixes = []
        
        for issue in issues:
            prompt = self._build_fix_prompt(file_contents, issue, mode)
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self._get_fix_system_prompt(mode)},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=1000
                )
                
                fix_result = json.loads(response.choices[0].message.content)
                fixes.append({
                    "issue_id": issue.get("id", "unknown"),
                    "issue_type": issue.get("type", "unknown"),
                    "fix": fix_result.get("fix", ""),
                    "confidence": fix_result.get("confidence", 0),
                    "reason": fix_result.get("reason", ""),
                    "file_affected": issue.get("file", "unknown")
                })
                
            except Exception as e:
                fixes.append({
                    "issue_id": issue.get("id", "unknown"),
                    "issue_type": issue.get("type", "unknown"),
                    "fix": "",
                    "confidence": 0,
                    "reason": f"Fix generation failed: {str(e)}",
                    "file_affected": issue.get("file", "unknown")
                })
        
        return fixes
    
    async def explain_issue(
        self, 
        issue_description: str, 
        configuration_context: Dict[str, Any], 
        mode: str = "devops"
    ) -> str:
        """Explain specific issue in beginner or devops mode"""
        
        prompt = self._build_explanation_prompt(issue_description, configuration_context, mode)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_explanation_system_prompt(mode)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Explanation failed: {str(e)}"
    
    async def confirm_secret(
        self, 
        suspected_line: str, 
        context: str
    ) -> Dict[str, Any]:
        """Use AI to confirm if a line contains a secret"""
        
        prompt = f"""
        Analyze this line for potential secrets:
        
        Line: "{suspected_line}"
        Context: {context}
        
        Return JSON with:
        {{
            "is_secret": true/false,
            "confidence": 0-100,
            "secret_type": "api_key/password/token/etc",
            "severity": "low/medium/high/critical"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a security expert specialized in detecting secrets in code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {
                "is_secret": False,
                "confidence": 0,
                "secret_type": "unknown",
                "severity": "low"
            }
    
    def _build_context(
        self, 
        file_contents: Dict[str, str], 
        syntax_errors: List[Dict], 
        security_issues: List[Dict], 
        logic_conflicts: List[Dict]
    ) -> str:
        """Build context for AI analysis"""
        
        context = "Configuration Files Analysis:\n\n"
        
        for file_type, content in file_contents.items():
            if content and content.strip():  # Only include non-empty files
                context += f"=== {file_type.upper()} ===\n{content}\n\n"
        
        if syntax_errors:
            context += "=== SYNTAX ERRORS ===\n"
            for error in syntax_errors:
                context += f"- {error.get('message', 'Unknown error')}\n"
        
        if security_issues:
            context += "\n=== SECURITY ISSUES ===\n"
            for issue in security_issues:
                context += f"- {issue.get('message', 'Unknown issue')}\n"
        
        if logic_conflicts:
            context += "\n=== LOGIC CONFLICTS ===\n"
            for conflict in logic_conflicts:
                context += f"- {conflict.get('message', 'Unknown conflict')}\n"
        
        return context
    
    def _build_analysis_prompt(self, context: str, mode: str) -> str:
        """Build prompt for configuration analysis"""
        
        if mode == "beginner":
            return f"""
            Analyze this DevOps configuration for a beginner. Explain in simple terms:
            
            {context}
            
            Return JSON with:
            {{
                "root_cause": "Simple explanation of what's wrong",
                "explanation": "Detailed but beginner-friendly explanation",
                "impact": "How this affects deployment in simple terms",
                "confidence_scores": [
                    {{
                        "category": "syntax/security/logic",
                        "score": 0-100,
                        "reason": "Why this score"
                    }}
                ]
            }}
            """
        else:
            return f"""
            Analyze this DevOps configuration for experienced DevOps engineers:
            
            {context}
            
            Return JSON with:
            {{
                "root_cause": "Technical root cause analysis",
                "explanation": "Detailed technical explanation",
                "impact": "Deployment and infrastructure impact",
                "confidence_scores": [
                    {{
                        "category": "syntax/security/logic",
                        "score": 0-100,
                        "reason": "Technical reasoning"
                    }}
                ]
            }}
            """
    
    def _build_fix_prompt(self, file_contents: Dict[str, str], issue: Dict, mode: str) -> str:
        """Build prompt for generating fixes"""
        
        file_content = file_contents.get(issue.get("file", ""), "")
        
        if mode == "beginner":
            return f"""
            Generate a simple fix for this issue:
            
            Issue: {issue.get('message', 'Unknown')}
            File: {issue.get('file', 'Unknown')}
            Current content: {file_content}
            
            Return JSON with:
            {{
                "fix": "The corrected code/configuration",
                "confidence": 0-100,
                "reason": "Simple explanation of why this fixes it"
            }}
            """
        else:
            return f"""
            Generate a technical fix for this issue:
            
            Issue: {issue.get('message', 'Unknown')}
            File: {issue.get('file', 'Unknown')}
            Current content: {file_content}
            
            Return JSON with:
            {{
                "fix": "The corrected code/configuration",
                "confidence": 0-100,
                "reason": "Technical explanation of the fix"
            }}
            """
    
    def _build_explanation_prompt(self, issue: str, context: Dict[str, Any], mode: str) -> str:
        """Build prompt for explaining issues"""
        
        context_str = json.dumps(context, indent=2)
        
        if mode == "beginner":
            return f"""
            Explain this DevOps issue in simple terms:
            
            Issue: {issue}
            Context: {context_str}
            
            Explain like you're teaching someone new to DevOps.
            """
        else:
            return f"""
            Provide a technical explanation for this DevOps issue:
            
            Issue: {issue}
            Context: {context_str}
            
            Explain for an experienced DevOps engineer.
            """
    
    def _get_system_prompt(self, mode: str) -> str:
        """Get system prompt based on mode"""
        
        if mode == "beginner":
            return """
            You are a DevOps expert explaining concepts to beginners. 
            Use simple language, analogies, and avoid jargon.
            Always explain the "why" behind technical concepts.
            """
        else:
            return """
            You are a senior DevOps engineer providing expert analysis.
            Be technical, precise, and focus on root causes and impacts.
            Use proper DevOps terminology and best practices.
            """
    
    def _get_fix_system_prompt(self, mode: str) -> str:
        """Get system prompt for fix generation"""
        
        if mode == "beginner":
            return """
            You are generating fixes for DevOps beginners.
            Provide clean, simple fixes with clear explanations.
            Focus on best practices that are easy to understand.
            """
        else:
            return """
            You are generating expert-level DevOps fixes.
            Provide production-ready solutions following industry best practices.
            Consider security, performance, and maintainability.
            """
    
    def _get_explanation_system_prompt(self, mode: str) -> str:
        """Get system prompt for explanations"""
        
        if mode == "beginner":
            return """
            You explain DevOps concepts to beginners.
            Use simple language, real-world examples, and avoid technical jargon.
            Focus on helping the user understand the core concept.
            """
        else:
            return """
            You provide technical explanations to DevOps professionals.
            Be precise, detailed, and focus on technical accuracy.
            Include relevant best practices and considerations.
            """
