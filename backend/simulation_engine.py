import yaml
import re
from typing import Dict, List, Any

class DeploymentSimulationEngine:
    def __init__(self):
        self.build_factors = {
            "dockerfile_syntax": 0.3,
            "dockerfile_best_practices": 0.2,
            "image_size": 0.15,
            "layer_optimization": 0.15,
            "dependencies": 0.2
        }
        
        self.runtime_factors = {
            "port_conflicts": 0.25,
            "service_dependencies": 0.2,
            "resource_limits": 0.15,
            "health_checks": 0.2,
            "restart_policies": 0.1,
            "environment_config": 0.1
        }
        
        self.security_factors = {
            "vulnerabilities": 0.4,
            "secrets_exposure": 0.3,
            "privileged_containers": 0.15,
            "network_exposure": 0.15
        }
    
    async def simulate_deployment(self, file_contents: Dict[str, str]) -> Dict[str, Any]:
        """Run comprehensive deployment simulation"""
        
        # Simulate different aspects of deployment
        build_stability = await self._simulate_build_stability(file_contents)
        runtime_stability = await self._simulate_runtime_stability(file_contents)
        security_posture = await self._simulate_security_posture(file_contents)
        
        # Calculate overall readiness
        overall_readiness = (
            build_stability * 0.3 +
            runtime_stability * 0.4 +
            security_posture * 0.3
        )
        
        # Generate deployment predictions
        deployment_predictions = await self._predict_deployment_outcomes(
            build_stability, runtime_stability, security_posture
        )
        
        # Calculate resource requirements
        resource_estimates = await self._estimate_resource_requirements(file_contents)
        
        # Generate deployment timeline
        timeline = await self._estimate_deployment_timeline(file_contents)
        
        return {
            "build_stability": round(build_stability, 1),
            "runtime_stability": round(runtime_stability, 1),
            "security_posture": round(security_posture, 1),
            "overall_readiness": round(overall_readiness, 1),
            "deployment_predictions": deployment_predictions,
            "resource_estimates": resource_estimates,
            "deployment_timeline": timeline,
            "risk_factors": await self._identify_risk_factors(file_contents),
            "optimization_suggestions": await self._generate_optimization_suggestions(file_contents)
        }
    
    async def _simulate_build_stability(self, file_contents: Dict[str, str]) -> float:
        """Simulate build process stability"""
        
        score = 100.0
        
        if file_contents.get("dockerfile") and file_contents["dockerfile"].strip():
            dockerfile_content = file_contents["dockerfile"]
            
            # Check Dockerfile syntax
            syntax_issues = self._check_dockerfile_syntax(dockerfile_content)
            score -= syntax_issues * 10
            
            # Check for best practices violations
            best_practice_issues = self._check_dockerfile_best_practices(dockerfile_content)
            score -= best_practice_issues * 5
            
            # Estimate image size impact
            size_impact = self._estimate_image_size_impact(dockerfile_content)
            score -= size_impact
            
            # Check layer optimization
            layer_issues = self._check_layer_optimization(dockerfile_content)
            score -= layer_issues * 3
            
            # Check dependency management
            dependency_issues = self._check_dependency_management(dockerfile_content)
            score -= dependency_issues * 7
        
        if "docker_compose" in file_contents:
            compose_content = file_contents["docker_compose"]
            
            # Check build configurations
            build_issues = self._check_compose_build_configs(compose_content)
            score -= build_issues * 8
        
        return max(0, score)
    
    async def _simulate_runtime_stability(self, file_contents: Dict[str, str]) -> float:
        """Simulate runtime stability"""
        
        score = 100.0
        
        if "docker_compose" in file_contents:
            compose_content = file_contents["docker_compose"]
            
            try:
                compose_data = yaml.safe_load(compose_content)
                
                if "services" in compose_data:
                    # Check port conflicts
                    port_conflicts = self._check_port_conflicts(compose_data["services"])
                    score -= port_conflicts * 15
                    
                    # Check service dependencies
                    dependency_issues = self._check_service_dependencies(compose_data["services"])
                    score -= dependency_issues * 10
                    
                    # Check resource limits
                    resource_issues = self._check_resource_limits(compose_data["services"])
                    score -= resource_issues * 8
                    
                    # Check health checks
                    health_check_issues = self._check_health_checks(compose_data["services"])
                    score -= health_check_issues * 12
                    
                    # Check restart policies
                    restart_policy_issues = self._check_restart_policies(compose_data["services"])
                    score -= restart_policy_issues * 5
                    
                    # Check environment configuration
                    env_issues = self._check_environment_config(compose_data["services"])
                    score -= env_issues * 6
            
            except yaml.YAMLError:
                score -= 50  # Major penalty for invalid YAML
        
        return max(0, score)
    
    async def _simulate_security_posture(self, file_contents: Dict[str, str]) -> float:
        """Simulate security posture"""
        
        score = 100.0
        
        if "dockerfile" in file_contents:
            dockerfile_content = file_contents["dockerfile"]
            
            # Check for security best practices
            security_issues = self._check_dockerfile_security(dockerfile_content)
            score -= security_issues * 8
        
        if "docker_compose" in file_contents:
            compose_content = file_contents["docker_compose"]
            
            try:
                compose_data = yaml.safe_load(compose_content)
                
                if "services" in compose_data:
                    # Check privileged containers
                    privileged_issues = self._check_privileged_containers(compose_data["services"])
                    score -= privileged_issues * 20
                    
                    # Check network exposure
                    network_issues = self._check_network_exposure(compose_data["services"])
                    score -= network_issues * 10
            
            except yaml.YAMLError:
                score -= 30
        
        if "env_file" in file_contents:
            env_content = file_contents["env_file"]
            
            # Check for secrets in environment
            secrets_issues = self._check_env_secrets(env_content)
            score -= secrets_issues * 15
        
        return max(0, score)
    
    async def _predict_deployment_outcomes(
        self, 
        build_stability: float, 
        runtime_stability: float, 
        security_posture: float
    ) -> Dict[str, Any]:
        """Predict likely deployment outcomes"""
        
        outcomes = {
            "build_success_probability": min(100, build_stability),
            "deployment_success_probability": min(100, (build_stability + runtime_stability) / 2),
            "security_incident_probability": max(0, 100 - security_posture),
            "performance_issues_probability": max(0, 100 - runtime_stability),
            "rollback_probability": max(0, (100 - build_stability + 100 - runtime_stability) / 2)
        }
        
        # Determine overall deployment confidence
        avg_score = (build_stability + runtime_stability + security_posture) / 3
        
        if avg_score >= 85:
            confidence_level = "Very High"
            recommendation = "Deploy with confidence"
        elif avg_score >= 70:
            confidence_level = "High"
            recommendation = "Deploy with monitoring"
        elif avg_score >= 50:
            confidence_level = "Medium"
            recommendation = "Test in staging first"
        else:
            confidence_level = "Low"
            recommendation = "Fix issues before deployment"
        
        outcomes["confidence_level"] = confidence_level
        outcomes["recommendation"] = recommendation
        
        return outcomes
    
    async def _estimate_resource_requirements(self, file_contents: Dict[str, str]) -> Dict[str, Any]:
        """Estimate resource requirements"""
        
        estimates = {
            "cpu_cores": "Unknown",
            "memory_gb": "Unknown",
            "storage_gb": "Unknown",
            "network_bandwidth": "Unknown"
        }
        
        if "docker_compose" in file_contents:
            compose_content = file_contents["docker_compose"]
            
            try:
                compose_data = yaml.safe_load(compose_content)
                
                if compose_data and "services" in compose_data:
                    total_cpu = 0
                    total_memory = 0
                    service_count = len(compose_data["services"])
                    
                    for service_name, service_config in compose_data["services"].items():
                        # Check for explicit resource limits
                        if "deploy" in service_config and "resources" in service_config["deploy"]:
                            resources = service_config["deploy"]["resources"]
                            
                            if "limits" in resources:
                                if "cpus" in resources["limits"]:
                                    total_cpu += float(resources["limits"]["cpus"])
                                if "memory" in resources["limits"]:
                                    memory_str = resources["limits"]["memory"]
                                    total_memory += self._parse_memory_string(memory_str)
                        
                        # Estimate based on service type
                        estimated_cpu, estimated_memory = self._estimate_service_resources(
                            service_name, service_config
                        )
                        total_cpu += estimated_cpu
                        total_memory += estimated_memory
                    
                    estimates["cpu_cores"] = f"{total_cpu:.1f}"
                    estimates["memory_gb"] = f"{total_memory:.1f}"
                    
                    # Estimate storage (base + per service)
                    base_storage = 2  # GB
                    storage_per_service = 1  # GB
                    estimates["storage_gb"] = f"{base_storage + (service_count * storage_per_service)}"
                    
                    # Estimate network bandwidth
                    if service_count <= 3:
                        estimates["network_bandwidth"] = "Low (< 100 Mbps)"
                    elif service_count <= 10:
                        estimates["network_bandwidth"] = "Medium (100-500 Mbps)"
                    else:
                        estimates["network_bandwidth"] = "High (> 500 Mbps)"
            
            except yaml.YAMLError:
                pass
        
        return estimates
    
    async def _estimate_deployment_timeline(self, file_contents: Dict[str, str]) -> Dict[str, Any]:
        """Estimate deployment timeline"""
        
        timeline = {
            "build_time_minutes": 0,
            "deployment_time_minutes": 0,
            "total_time_minutes": 0,
            "phases": []
        }
        
        # Estimate build time
        build_time = 5  # Base build time
        
        if "dockerfile" in file_contents:
            dockerfile_content = file_contents["dockerfile"]
            
            # Add time for each RUN instruction
            run_count = dockerfile_content.upper().count("RUN")
            build_time += run_count * 2
            
            # Add time for COPY/ADD operations
            copy_count = dockerfile_content.upper().count("COPY") + dockerfile_content.upper().count("ADD")
            build_time += copy_count * 1
            
            # Check for package installations
            if any(pkg in dockerfile_content.lower() for pkg in ["apt-get", "yum", "apk", "pip", "npm"]):
                build_time += 5
        
        # Estimate deployment time
        deployment_time = 2  # Base deployment time
        
        if "docker_compose" in file_contents:
            compose_content = file_contents["docker_compose"]
            
            try:
                compose_data = yaml.safe_load(compose_content)
                
                if compose_data and "services" in compose_data:
                    service_count = len(compose_data["services"])
                    deployment_time += service_count * 1
                    
                    # Add time for services with health checks
                    for service_config in compose_data["services"].values():
                        if "healthcheck" in service_config:
                            deployment_time += 2
            
            except yaml.YAMLError:
                deployment_time += 5  # Extra time for potential issues
        
        timeline["build_time_minutes"] = build_time
        timeline["deployment_time_minutes"] = deployment_time
        timeline["total_time_minutes"] = build_time + deployment_time
        
        # Create phases
        timeline["phases"] = [
            {"name": "Image Build", "estimated_time": build_time, "description": "Building Docker images"},
            {"name": "Service Deployment", "estimated_time": deployment_time, "description": "Deploying services"},
            {"name": "Health Check", "estimated_time": 3, "description": "Verifying service health"}
        ]
        
        return timeline
    
    async def _identify_risk_factors(self, file_contents: Dict[str, str]) -> List[Dict[str, Any]]:
        """Identify specific risk factors"""
        
        risk_factors = []
        
        if "dockerfile" in file_contents:
            dockerfile_content = file_contents["dockerfile"]
            
            if "FROM latest" in dockerfile_content:
                risk_factors.append({
                    "type": "image_tag",
                    "severity": "medium",
                    "description": "Using 'latest' tag can lead to unpredictable deployments",
                    "recommendation": "Use specific version tags"
                })
            
            if dockerfile_content.upper().count("RUN") > 10:
                risk_factors.append({
                    "type": "layer_optimization",
                    "severity": "low",
                    "description": "Many RUN instructions may increase image size",
                    "recommendation": "Combine RUN instructions where possible"
                })
        
        if "docker_compose" in file_contents:
            compose_content = file_contents["docker_compose"]
            
            try:
                compose_data = yaml.safe_load(compose_content)
                
                if compose_data and "services" in compose_data:
                    for service_name, service_config in compose_data["services"].items():
                        if "restart" not in service_config:
                            risk_factors.append({
                                "type": "restart_policy",
                                "severity": "medium",
                                "description": f"Service '{service_name}' has no restart policy",
                                "recommendation": "Add appropriate restart policy"
                            })
                        
                        if "healthcheck" not in service_config:
                            risk_factors.append({
                                "type": "health_check",
                                "severity": "low",
                                "description": f"Service '{service_name}' has no health check",
                                "recommendation": "Add health check for better monitoring"
                            })
            
            except yaml.YAMLError:
                risk_factors.append({
                    "type": "yaml_syntax",
                    "severity": "high",
                    "description": "Invalid YAML syntax in docker-compose.yml",
                    "recommendation": "Fix YAML syntax errors"
                })
        
        return risk_factors
    
    async def _generate_optimization_suggestions(self, file_contents: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate optimization suggestions"""
        
        suggestions = []
        
        if "dockerfile" in file_contents:
            dockerfile_content = file_contents["dockerfile"]
            
            # Multi-stage build suggestion
            if "FROM" in dockerfile_content and dockerfile_content.count("FROM") == 1:
                if any(cmd in dockerfile_content.upper() for cmd in ["RUN", "COPY", "ADD"]):
                    suggestions.append({
                        "category": "build_optimization",
                        "impact": "high",
                        "description": "Consider using multi-stage builds to reduce image size",
                        "implementation": "Add a second FROM instruction with a minimal base image"
                    })
            
            # .dockerignore suggestion
            if "COPY" in dockerfile_content and "." in dockerfile_content:
                suggestions.append({
                    "category": "build_optimization",
                    "impact": "medium",
                    "description": "Use .dockerignore to exclude unnecessary files",
                    "implementation": "Create .dockerignore file to exclude .git, node_modules, etc."
                })
        
        if "docker_compose" in file_contents:
            compose_content = file_contents["docker_compose"]
            
            try:
                compose_data = yaml.safe_load(compose_content)
                
                if compose_data and "services" in compose_data:
                    # Resource limits suggestion
                    services_without_limits = []
                    for service_name, service_config in compose_data["services"].items():
                        if "deploy" not in service_config or "resources" not in service_config.get("deploy", {}):
                            services_without_limits.append(service_name)
                    
                    if services_without_limits:
                        suggestions.append({
                            "category": "resource_optimization",
                            "impact": "high",
                            "description": f"Add resource limits for services: {', '.join(services_without_limits)}",
                            "implementation": "Add deploy.resources.limits configuration for each service"
                        })
            
            except yaml.YAMLError:
                pass
        
        return suggestions
    
    # Helper methods
    def _check_dockerfile_syntax(self, content: str) -> int:
        """Check for Dockerfile syntax issues"""
        issues = 0
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if line.upper().startswith('FROM') and ':' not in line and ' AS ' not in line:
                    issues += 1
        
        return issues
    
    def _check_dockerfile_best_practices(self, content: str) -> int:
        """Check for Dockerfile best practices violations"""
        issues = 0
        
        if 'USER root' in content or 'USER 0' in content:
            issues += 1
        
        if content.count('RUN') > 8:
            issues += 1
        
        return issues
    
    def _estimate_image_size_impact(self, content: str) -> float:
        """Estimate image size impact"""
        impact = 0
        
        if 'FROM ubuntu' in content.lower() or 'FROM debian' in content.lower():
            impact += 5
        elif 'FROM alpine' in content.lower():
            impact += 1
        
        return impact
    
    def _check_layer_optimization(self, content: str) -> int:
        """Check layer optimization issues"""
        issues = 0
        
        # Check for unnecessary package manager cache
        if 'apt-get' in content and 'rm -rf /var/lib/apt/lists/*' not in content:
            issues += 1
        
        return issues
    
    def _check_dependency_management(self, content: str) -> int:
        """Check dependency management issues"""
        issues = 0
        
        if 'latest' in content.lower():
            issues += 1
        
        return issues
    
    def _check_compose_build_configs(self, content: str) -> int:
        """Check docker-compose build configurations"""
        issues = 0
        
        try:
            compose_data = yaml.safe_load(content)
            
            if compose_data and "services" in compose_data:
                for service_config in compose_data["services"].values():
                    if "build" in service_config and "context" not in service_config["build"]:
                        issues += 1
        
        except yaml.YAMLError:
            issues += 1
        
        return issues
    
    def _check_port_conflicts(self, services: Dict) -> int:
        """Check for port conflicts"""
        conflicts = 0
        used_ports = {}
        
        for service_name, service_config in services.items():
            if "ports" in service_config:
                for port_mapping in service_config["ports"]:
                    if isinstance(port_mapping, str):
                        host_port = port_mapping.split(':')[0]
                        if host_port in used_ports:
                            conflicts += 1
                        else:
                            used_ports[host_port] = service_name
        
        return conflicts
    
    def _check_service_dependencies(self, services: Dict) -> int:
        """Check service dependencies"""
        issues = 0
        
        for service_name, service_config in services.items():
            if "depends_on" in service_config:
                dependencies = service_config["depends_on"]
                if isinstance(dependencies, list):
                    for dep in dependencies:
                        if dep not in services:
                            issues += 1
        
        return issues
    
    def _check_resource_limits(self, services: Dict) -> int:
        """Check for missing resource limits"""
        issues = 0
        
        for service_config in services.values():
            if "deploy" not in service_config or "resources" not in service_config.get("deploy", {}):
                issues += 1
        
        return issues
    
    def _check_health_checks(self, services: Dict) -> int:
        """Check for missing health checks"""
        issues = 0
        
        for service_name, service_config in services.items():
            if "healthcheck" not in service_config:
                issues += 1
        
        return issues
    
    def _check_restart_policies(self, services: Dict) -> int:
        """Check for missing restart policies"""
        issues = 0
        
        for service_name, service_config in services.items():
            if "restart" not in service_config:
                issues += 1
        
        return issues
    
    def _check_environment_config(self, services: Dict) -> int:
        """Check environment configuration"""
        issues = 0
        
        for service_name, service_config in services.items():
            if "environment" in service_config:
                env_vars = service_config["environment"]
                if isinstance(env_vars, dict):
                    for key, value in env_vars.items():
                        if "password" in key.lower() or "secret" in key.lower():
                            issues += 1
        
        return issues
    
    def _check_dockerfile_security(self, content: str) -> int:
        """Check Dockerfile security issues"""
        issues = 0
        
        if 'sudo' in content:
            issues += 1
        
        if content.count('ADD') > content.count('COPY'):
            issues += 1
        
        return issues
    
    def _check_privileged_containers(self, services: Dict) -> int:
        """Check for privileged containers"""
        issues = 0
        
        for service_name, service_config in services.items():
            if service_config.get("privileged", False):
                issues += 1
        
        return issues
    
    def _check_network_exposure(self, services: Dict) -> int:
        """Check network exposure"""
        issues = 0
        
        for service_name, service_config in services.items():
            if "ports" in service_config:
                for port_mapping in service_config["ports"]:
                    if isinstance(port_mapping, str) and ':' not in port_mapping:
                        issues += 1
        
        return issues
    
    def _check_env_secrets(self, content: str) -> int:
        """Check for secrets in environment file"""
        issues = 0
        
        lines = content.split('\n')
        for line in lines:
            if any(secret in line.lower() for secret in ['password', 'secret', 'key', 'token']):
                issues += 1
        
        return issues
    
    def _parse_memory_string(self, memory_str: str) -> float:
        """Parse memory string to GB"""
        memory_str = memory_str.lower()
        
        if memory_str.endswith('g'):
            return float(memory_str[:-1])
        elif memory_str.endswith('m'):
            return float(memory_str[:-1]) / 1024
        elif memory_str.endswith('k'):
            return float(memory_str[:-1]) / 1024 / 1024
        else:
            return float(memory_str) / 1024 / 1024 / 1024
    
    def _estimate_service_resources(self, service_name: str, service_config: Dict) -> tuple:
        """Estimate CPU and memory for a service"""
        # Base estimates
        cpu_estimate = 0.1
        memory_estimate = 0.1  # GB
        
        # Adjust based on service name patterns
        service_name_lower = service_name.lower()
        
        if 'db' in service_name_lower or 'database' in service_name_lower:
            cpu_estimate = 0.5
            memory_estimate = 1.0
        elif 'cache' in service_name_lower or 'redis' in service_name_lower:
            cpu_estimate = 0.2
            memory_estimate = 0.5
        elif 'api' in service_name_lower or 'app' in service_name_lower:
            cpu_estimate = 0.3
            memory_estimate = 0.5
        elif 'web' in service_name_lower or 'nginx' in service_name_lower:
            cpu_estimate = 0.2
            memory_estimate = 0.2
        
        return cpu_estimate, memory_estimate
