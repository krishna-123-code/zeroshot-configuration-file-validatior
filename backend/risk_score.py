from typing import Dict, List, Any
import math

class RiskScoringEngine:
    def __init__(self):
        self.severity_weights = {
            "critical": 10,
            "high": 7,
            "medium": 4,
            "low": 1,
            "info": 0.5,
            "error": 6,
            "warning": 3,
            "unknown": 2
        }
        
        self.category_weights = {
            "syntax_errors": 0.2,
            "security_issues": 0.35,
            "logic_conflicts": 0.25,
            "secrets_detected": 0.2
        }
    
    async def calculate_risk_score(
        self, 
        syntax_errors: List[Dict], 
        security_issues: List[Dict], 
        logic_conflicts: List[Dict], 
        secrets_detected: List[Dict]
    ) -> Dict[str, Any]:
        """Calculate overall deployment risk score"""
        
        # Calculate individual risk components
        syntax_risk = self._calculate_syntax_risk(syntax_errors)
        security_risk = self._calculate_security_risk(security_issues)
        logic_risk = self._calculate_logic_risk(logic_conflicts)
        secrets_risk = self._calculate_secrets_risk(secrets_detected)
        
        # Calculate weighted overall score
        overall_score = (
            syntax_risk["score"] * self.category_weights["syntax_errors"] +
            security_risk["score"] * self.category_weights["security_issues"] +
            logic_risk["score"] * self.category_weights["logic_conflicts"] +
            secrets_risk["score"] * self.category_weights["secrets_detected"]
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_score)
        
        # Calculate stability metrics
        stability_metrics = self._calculate_stability_metrics(
            syntax_errors, security_issues, logic_conflicts
        )
        
        return {
            "overall_score": round(overall_score, 1),
            "risk_level": risk_level,
            "breakdown": {
                "syntax_risk": syntax_risk,
                "security_risk": security_risk,
                "logic_risk": logic_risk,
                "secrets_risk": secrets_risk
            },
            "stability_metrics": stability_metrics,
            "issue_counts": {
                "total_syntax_errors": len(syntax_errors),
                "total_security_issues": len(security_issues),
                "total_logic_conflicts": len(logic_conflicts),
                "total_secrets": len(secrets_detected),
                "total_issues": len(syntax_errors) + len(security_issues) + len(logic_conflicts) + len(secrets_detected)
            },
            "recommendations": self._generate_risk_recommendations(
                syntax_risk, security_risk, logic_risk, secrets_risk
            )
        }
    
    def _calculate_syntax_risk(self, syntax_errors: List[Dict]) -> Dict[str, Any]:
        """Calculate syntax-related risk"""
        
        if not syntax_errors:
            return {
                "score": 0,
                "level": "low",
                "factors": [],
                "critical_issues": 0
            }
        
        # Weight issues by severity
        total_weight = 0
        critical_count = 0
        factors = []
        
        for error in syntax_errors:
            severity = error.get("severity", "unknown").lower()
            weight = self.severity_weights.get(severity, self.severity_weights["unknown"])
            total_weight += weight
            
            if severity == "error" or severity == "critical":
                critical_count += 1
            
            factors.append({
                "type": "syntax_error",
                "severity": severity,
                "weight": weight,
                "message": error.get("message", "Unknown syntax error")
            })
        
        # Normalize to 0-100 scale
        # Cap at 20 syntax errors for maximum impact
        normalized_score = min(100, (total_weight / 20) * 100)
        
        return {
            "score": round(normalized_score, 1),
            "level": self._determine_risk_level(normalized_score),
            "factors": factors,
            "critical_issues": critical_count
        }
    
    def _calculate_security_risk(self, security_issues: List[Dict]) -> Dict[str, Any]:
        """Calculate security-related risk"""
        
        if not security_issues:
            return {
                "score": 0,
                "level": "low",
                "factors": [],
                "critical_vulnerabilities": 0
            }
        
        total_weight = 0
        critical_count = 0
        cvss_impact = 0
        factors = []
        
        for issue in security_issues:
            severity = issue.get("severity", "unknown").lower()
            weight = self.severity_weights.get(severity, self.severity_weights["unknown"])
            
            # Extra weight for CVSS scores
            cvss_score = issue.get("cvss_score")
            if cvss_score:
                cvss_impact += cvss_score
                weight += (cvss_score / 10) * 5  # Add up to 5 extra weight for high CVSS
            
            total_weight += weight
            
            if severity == "critical":
                critical_count += 1
            
            factors.append({
                "type": "security_issue",
                "severity": severity,
                "weight": weight,
                "message": issue.get("message", "Unknown security issue"),
                "scanner": issue.get("scanner", "unknown"),
                "cvss_score": cvss_score
            })
        
        # Normalize to 0-100 scale with security emphasis
        # Security issues have higher impact
        normalized_score = min(100, (total_weight / 15) * 100)
        
        return {
            "score": round(normalized_score, 1),
            "level": self._determine_risk_level(normalized_score),
            "factors": factors,
            "critical_vulnerabilities": critical_count,
            "cvss_impact": round(cvss_impact, 1)
        }
    
    def _calculate_logic_risk(self, logic_conflicts: List[Dict]) -> Dict[str, Any]:
        """Calculate logic-related risk"""
        
        if not logic_conflicts:
            return {
                "score": 0,
                "level": "low",
                "factors": [],
                "blocking_issues": 0
            }
        
        total_weight = 0
        blocking_count = 0
        factors = []
        
        for conflict in logic_conflicts:
            severity = conflict.get("severity", "unknown").lower()
            weight = self.severity_weights.get(severity, self.severity_weights["unknown"])
            
            # Extra weight for blocking conflicts
            conflict_type = conflict.get("conflict_type", "")
            if conflict_type in ["port_conflict", "undefined_dependency"]:
                weight += 3
                blocking_count += 1
            
            total_weight += weight
            
            factors.append({
                "type": "logic_conflict",
                "severity": severity,
                "weight": weight,
                "message": conflict.get("message", "Unknown logic conflict"),
                "conflict_type": conflict_type
            })
        
        # Normalize to 0-100 scale
        normalized_score = min(100, (total_weight / 10) * 100)
        
        return {
            "score": round(normalized_score, 1),
            "level": self._determine_risk_level(normalized_score),
            "factors": factors,
            "blocking_issues": blocking_count
        }
    
    def _calculate_secrets_risk(self, secrets_detected: List[Dict]) -> Dict[str, Any]:
        """Calculate secrets-related risk"""
        
        if not secrets_detected:
            return {
                "score": 0,
                "level": "low",
                "factors": [],
                "high_confidence_secrets": 0
            }
        
        total_weight = 0
        high_confidence_count = 0
        ai_confirmed_count = 0
        factors = []
        
        for secret in secrets_detected:
            severity = secret.get("severity", "unknown").lower()
            weight = self.severity_weights.get(severity, self.severity_weights["unknown"])
            
            # Extra weight for AI-confirmed secrets
            if secret.get("ai_confirmed", False):
                weight += 2
                ai_confirmed_count += 1
            
            # Extra weight for high confidence
            confidence = secret.get("confidence", 0)
            if confidence >= 80:
                weight += 1
                high_confidence_count += 1
            
            total_weight += weight
            
            factors.append({
                "type": "secret_detected",
                "severity": severity,
                "weight": weight,
                "message": f"Secret detected: {secret.get('secret_type', 'unknown')}",
                "secret_type": secret.get("secret_type", "unknown"),
                "confidence": confidence,
                "ai_confirmed": secret.get("ai_confirmed", False)
            })
        
        # Normalize to 0-100 scale
        normalized_score = min(100, (total_weight / 12) * 100)
        
        return {
            "score": round(normalized_score, 1),
            "level": self._determine_risk_level(normalized_score),
            "factors": factors,
            "high_confidence_secrets": high_confidence_count,
            "ai_confirmed_secrets": ai_confirmed_count
        }
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level based on score"""
        
        if score >= 80:
            return "Critical"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Low"
        else:
            return "Minimal"
    
    def _calculate_stability_metrics(
        self, 
        syntax_errors: List[Dict], 
        security_issues: List[Dict], 
        logic_conflicts: List[Dict]
    ) -> Dict[str, Any]:
        """Calculate deployment stability metrics"""
        
        # Build stability (syntax + basic logic)
        blocking_issues = sum(1 for issue in logic_conflicts 
                            if issue.get("conflict_type") in ["port_conflict", "undefined_dependency"])
        syntax_errors_count = len(syntax_errors)
        
        build_stability = max(0, 100 - (blocking_issues * 20) - (syntax_errors_count * 5))
        
        # Runtime stability (security + runtime logic)
        critical_security = sum(1 for issue in security_issues 
                               if issue.get("severity") == "critical")
        high_security = sum(1 for issue in security_issues 
                           if issue.get("severity") == "high")
        
        runtime_stability = max(0, 100 - (critical_security * 25) - (high_security * 10))
        
        # Security posture
        total_security = len(security_issues)
        security_posture = max(0, 100 - (critical_security * 30) - (high_security * 15) - (total_security * 2))
        
        # Overall readiness
        overall_readiness = (build_stability + runtime_stability + security_posture) / 3
        
        return {
            "build_stability": round(build_stability, 1),
            "runtime_stability": round(runtime_stability, 1),
            "security_posture": round(security_posture, 1),
            "overall_readiness": round(overall_readiness, 1)
        }
    
    def _generate_risk_recommendations(
        self, 
        syntax_risk: Dict, 
        security_risk: Dict, 
        logic_risk: Dict, 
        secrets_risk: Dict
    ) -> List[str]:
        """Generate risk-based recommendations"""
        
        recommendations = []
        
        # Syntax recommendations
        if syntax_risk["score"] > 40:
            recommendations.append("Fix syntax errors before deployment to prevent build failures")
            if syntax_risk["critical_issues"] > 0:
                recommendations.append("Address critical syntax errors immediately")
        
        # Security recommendations
        if security_risk["score"] > 50:
            recommendations.append("Address security vulnerabilities before production deployment")
            if security_risk["critical_vulnerabilities"] > 0:
                recommendations.append("Critical security vulnerabilities require immediate attention")
        
        # Logic recommendations
        if logic_risk["score"] > 30:
            recommendations.append("Resolve logic conflicts to ensure proper service orchestration")
            if logic_risk["blocking_issues"] > 0:
                recommendations.append("Fix blocking issues that prevent deployment")
        
        # Secrets recommendations
        if secrets_risk["score"] > 60:
            recommendations.append("Remove or secure detected secrets before deployment")
            if secrets_risk["ai_confirmed_secrets"] > 0:
                recommendations.append("AI-confirmed secrets detected - immediate action required")
        
        # Overall recommendations
        if any(risk["score"] > 70 for risk in [syntax_risk, security_risk, logic_risk, secrets_risk]):
            recommendations.append("High-risk configuration detected - consider staging deployment first")
        
        return recommendations
    
    async def calculate_deployment_readiness(
        self, 
        syntax_errors: List[Dict], 
        security_issues: List[Dict], 
        logic_conflicts: List[Dict], 
        secrets_detected: List[Dict]
    ) -> Dict[str, Any]:
        """Calculate detailed deployment readiness metrics"""
        
        risk_score = await self.calculate_risk_score(
            syntax_errors, security_issues, logic_conflicts, secrets_detected
        )
        
        # Calculate deployment readiness score (inverse of risk)
        readiness_score = max(0, 100 - risk_score["overall_score"])
        
        # Determine deployment recommendation
        if readiness_score >= 85:
            deployment_recommendation = "Ready for production"
            deployment_color = "green"
        elif readiness_score >= 70:
            deployment_recommendation = "Ready for staging"
            deployment_color = "yellow"
        elif readiness_score >= 50:
            deployment_recommendation = "Requires fixes before deployment"
            deployment_color = "orange"
        else:
            deployment_recommendation = "Not ready for deployment"
            deployment_color = "red"
        
        # Calculate component readiness
        components = {}
        for component_name, risk_data in risk_score["breakdown"].items():
            component_readiness = max(0, 100 - risk_data["score"])
            components[component_name] = {
                "readiness": round(component_readiness, 1),
                "status": self._determine_risk_level(risk_data["score"]),
                "issues_count": len(risk_data["factors"])
            }
        
        return {
            "overall_readiness": round(readiness_score, 1),
            "deployment_recommendation": deployment_recommendation,
            "deployment_color": deployment_color,
            "components": components,
            "risk_summary": risk_score,
            "estimated_fix_time": self._estimate_fix_time(risk_score),
            "deployment_gates": self._check_deployment_gates(risk_score)
        }
    
    def _estimate_fix_time(self, risk_score: Dict) -> Dict[str, str]:
        """Estimate time to fix issues"""
        
        total_issues = risk_score["issue_counts"]["total_issues"]
        critical_issues = (
            risk_score["breakdown"]["syntax_risk"]["critical_issues"] +
            risk_score["breakdown"]["security_risk"]["critical_vulnerabilities"] +
            risk_score["breakdown"]["logic_risk"]["blocking_issues"]
        )
        
        if total_issues == 0:
            return {"low": "0 minutes", "medium": "0 minutes", "high": "0 minutes"}
        
        # Estimate based on issue count and complexity
        base_time = total_issues * 15  # 15 minutes per issue average
        critical_time = critical_issues * 30  # 30 minutes per critical issue
        
        total_time = base_time + critical_time
        
        return {
            "low": f"{max(5, total_issues * 5)} minutes",
            "medium": f"{max(15, total_issues * 15)} minutes",
            "high": f"{max(30, total_time)} minutes"
        }
    
    def _check_deployment_gates(self, risk_score: Dict) -> Dict[str, bool]:
        """Check if deployment gates pass"""
        
        gates = {
            "no_critical_syntax": risk_score["breakdown"]["syntax_risk"]["critical_issues"] == 0,
            "no_critical_security": risk_score["breakdown"]["security_risk"]["critical_vulnerabilities"] == 0,
            "no_blocking_logic": risk_score["breakdown"]["logic_risk"]["blocking_issues"] == 0,
            "no_high_confidence_secrets": risk_score["breakdown"]["secrets_risk"]["high_confidence_secrets"] == 0,
            "overall_risk_acceptable": risk_score["overall_score"] < 60
        }
        
        gates["all_pass"] = all(gates.values())
        
        return gates
