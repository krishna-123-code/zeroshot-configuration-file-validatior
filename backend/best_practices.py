import yaml
import re
from typing import Dict, List, Any

class BestPracticesAdvisor:
    def __init__(self):
        self.best_practice_rules = {
            "dockerfile": {
                "latest_tag": {
                    "pattern": r"FROM\s+.*latest",
                    "severity": "medium",
                    "message": "Avoid using 'latest' tag - use specific version tags",
                    "recommendation": "Use specific version tags (e.g., 'ubuntu:20.04' instead of 'ubuntu:latest')"
                },
                "root_user": {
                    "pattern": r"USER\s+(root|0)",
                    "severity": "high",
                    "message": "Running as root user is a security risk",
                    "recommendation": "Create and use a non-root user with minimal privileges"
                },
                "missing_healthcheck": {
                    "pattern": r"^(?!.*HEALTHCHECK).*",
                    "severity": "medium",
                    "message": "Missing HEALTHCHECK instruction",
                    "recommendation": "Add HEALTHCHECK instruction to monitor container health"
                },
                "sudo_usage": {
                    "pattern": r"sudo",
                    "severity": "medium",
                    "message": "Avoid using sudo in Dockerfile",
                    "recommendation": "Run commands directly without sudo or switch to non-root user"
                },
                "add_instead_of_copy": {
                    "pattern": r"ADD\s+(?!http)",
                    "severity": "low",
                    "message": "Prefer COPY over ADD for local files",
                    "recommendation": "Use COPY for local files, only use ADD for remote URLs or archives"
                },
                "package_cache_cleanup": {
                    "pattern": r"(apt-get|yum|apk)\s+install",
                    "severity": "medium",
                    "message": "Package manager cache not cleaned up",
                    "recommendation": "Clean package manager cache after installation to reduce image size"
                },
                "multiple_run_instructions": {
                    "pattern": r"(RUN.*\n){3,}",
                    "severity": "low",
                    "message": "Multiple RUN instructions can be combined",
                    "recommendation": "Combine RUN instructions with && to reduce layers"
                },
                "missing_expose": {
                    "pattern": r"^(?!.*EXPOSE).*",
                    "severity": "low",
                    "message": "Missing EXPOSE instruction for documentation",
                    "recommendation": "Add EXPOSE instruction to document which ports the application uses"
                },
                "workdir_missing": {
                    "pattern": r"^(?!.*WORKDIR).*",
                    "severity": "low",
                    "message": "Missing WORKDIR instruction",
                    "recommendation": "Set WORKDIR to avoid using absolute paths in subsequent instructions"
                },
                "environment_variables": {
                    "pattern": r"ENV\s+[A-Z_]+=",
                    "severity": "low",
                    "message": "Consider using ARG for build-time variables",
                    "recommendation": "Use ARG for build-time variables and ENV for runtime variables"
                }
            },
            "docker_compose": {
                "missing_restart_policy": {
                    "pattern": r"^(?!.*restart:).*",
                    "severity": "medium",
                    "message": "Missing restart policy for service",
                    "recommendation": "Add restart policy (e.g., 'restart: unless-stopped') for better reliability"
                },
                "missing_resource_limits": {
                    "pattern": r"^(?!.*deploy:.*resources:).*",
                    "severity": "high",
                    "message": "Missing resource limits for service",
                    "recommendation": "Add resource limits to prevent resource exhaustion"
                },
                "privileged_mode": {
                    "pattern": r"privileged:\s*true",
                    "severity": "critical",
                    "message": "Service running in privileged mode",
                    "recommendation": "Avoid privileged mode unless absolutely necessary"
                },
                "host_network_mode": {
                    "pattern": r"network_mode:\s*host",
                    "severity": "high",
                    "message": "Using host network mode",
                    "recommendation": "Avoid host network mode unless required for specific use cases"
                },
                "missing_healthcheck": {
                    "pattern": r"^(?!.*healthcheck:).*",
                    "severity": "medium",
                    "message": "Missing healthcheck for service",
                    "recommendation": "Add healthcheck configuration for better monitoring"
                },
                "environment_file_hardcoded": {
                    "pattern": r"\.env",
                    "severity": "low",
                    "message": "Hardcoded environment file reference",
                    "recommendation": "Use environment-specific files or environment variables"
                },
                "version_missing": {
                    "pattern": r"^(?!version:).*",
                    "severity": "low",
                    "message": "Missing compose file version",
                    "recommendation": "Specify compose file version for compatibility"
                }
            }
        }
    
    async def analyze_best_practices(self, file_contents: Dict[str, str]) -> List[Dict[str, Any]]:
        """Analyze configuration files for best practices violations"""
        
        suggestions = []
        
        # Analyze Dockerfile
        if file_contents.get("dockerfile") and file_contents["dockerfile"].strip():
            dockerfile_suggestions = await self._analyze_dockerfile_best_practices(
                file_contents["dockerfile"]
            )
            suggestions.extend(dockerfile_suggestions)
        
        # Analyze docker-compose.yml
        if file_contents.get("docker_compose") and file_contents["docker_compose"].strip():
            compose_suggestions = await self._analyze_docker_compose_best_practices(
                file_contents["docker_compose"]
            )
            suggestions.extend(compose_suggestions)
        
        # Analyze .env file
        if file_contents.get("env_file") and file_contents["env_file"].strip():
            env_suggestions = await self._analyze_env_best_practices(
                file_contents["env_file"]
            )
            suggestions.extend(env_suggestions)
        
        # Cross-file best practices
        cross_file_suggestions = await self._analyze_cross_file_best_practices(file_contents)
        suggestions.extend(cross_file_suggestions)
        
        return suggestions
    
    async def _analyze_dockerfile_best_practices(self, dockerfile_content: str) -> List[Dict[str, Any]]:
        """Analyze Dockerfile for best practices"""
        
        suggestions = []
        lines = dockerfile_content.split('\n')
        
        # Check each best practice rule
        for rule_name, rule_config in self.best_practice_rules["dockerfile"].items():
            if rule_name == "latest_tag":
                suggestions.extend(self._check_latest_tag(lines, rule_config))
            elif rule_name == "root_user":
                suggestions.extend(self._check_root_user(lines, rule_config))
            elif rule_name == "missing_healthcheck":
                suggestions.extend(self._check_missing_healthcheck(lines, rule_config))
            elif rule_name == "sudo_usage":
                suggestions.extend(self._check_sudo_usage(lines, rule_config))
            elif rule_name == "add_instead_of_copy":
                suggestions.extend(self._check_add_vs_copy(lines, rule_config))
            elif rule_name == "package_cache_cleanup":
                suggestions.extend(self._check_package_cache_cleanup(lines, rule_config))
            elif rule_name == "multiple_run_instructions":
                suggestions.extend(self._check_multiple_run_instructions(lines, rule_config))
            elif rule_name == "missing_expose":
                suggestions.extend(self._check_missing_expose(lines, rule_config))
            elif rule_name == "workdir_missing":
                suggestions.extend(self._check_workdir_missing(lines, rule_config))
            elif rule_name == "environment_variables":
                suggestions.extend(self._check_environment_variables(lines, rule_config))
        
        return suggestions
    
    async def _analyze_docker_compose_best_practices(self, compose_content: str) -> List[Dict[str, Any]]:
        """Analyze docker-compose.yml for best practices"""
        
        suggestions = []
        
        try:
            compose_data = yaml.safe_load(compose_content)
            
            if compose_data and "services" in compose_data:
                for service_name, service_config in compose_data["services"].items():
                    service_suggestions = self._analyze_service_best_practices(
                        service_name, service_config
                    )
                    suggestions.extend(service_suggestions)
            
            # Check for missing version
            if "version" not in compose_data:
                suggestions.append({
                    "type": "best_practice",
                    "file": "docker_compose",
                    "severity": "low",
                    "message": "Missing compose file version",
                    "recommendation": "Add 'version: \"3.8\"' or appropriate version",
                    "category": "versioning",
                    "service": None,
                    "line": None
                })
        
        except yaml.YAMLError:
            # YAML parsing error - this would be caught by validator
            pass
        
        return suggestions
    
    async def _analyze_env_best_practices(self, env_content: str) -> List[Dict[str, Any]]:
        """Analyze .env file for best practices"""
        
        suggestions = []
        lines = env_content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            # Check for sensitive data in .env
            if self._contains_sensitive_data(line):
                suggestions.append({
                    "type": "best_practice",
                    "file": "env_file",
                    "severity": "high",
                    "message": f"Sensitive data found in environment file at line {i}",
                    "recommendation": "Use secret management system for sensitive data",
                    "category": "security",
                    "line": i
                })
            
            # Check for default/development values
            if self._has_default_value(line):
                suggestions.append({
                    "type": "best_practice",
                    "file": "env_file",
                    "severity": "medium",
                    "message": f"Default/development value found at line {i}",
                    "recommendation": "Use environment-specific configuration files",
                    "category": "configuration",
                    "line": i
                })
        
        return suggestions
    
    async def _analyze_cross_file_best_practices(self, file_contents: Dict[str, str]) -> List[Dict[str, Any]]:
        """Analyze cross-file best practices"""
        
        suggestions = []
        
        # Check for consistency between Dockerfile and docker-compose
        if (file_contents.get("dockerfile") and file_contents["dockerfile"].strip() and 
            file_contents.get("docker_compose") and file_contents["docker_compose"].strip()):
            suggestions.extend(self._check_dockerfile_compose_consistency(
                file_contents["dockerfile"],
                file_contents["docker_compose"]
            ))
        
        # Check for environment variable consistency
        if (file_contents.get("docker_compose") and file_contents["docker_compose"].strip() and 
            file_contents.get("env_file") and file_contents["env_file"].strip()):
            suggestions.extend(self._check_env_consistency(
                file_contents["docker_compose"],
                file_contents["env_file"]
            ))
        
        return suggestions
    
    def _check_latest_tag(self, lines: List[str], rule_config: Dict) -> List[Dict[str, Any]]:
        """Check for latest tag usage"""
        
        suggestions = []
        
        for i, line in enumerate(lines, 1):
            if re.search(rule_config["pattern"], line, re.IGNORECASE):
                suggestions.append({
                    "type": "best_practice",
                    "file": "dockerfile",
                    "severity": rule_config["severity"],
                    "message": rule_config["message"],
                    "recommendation": rule_config["recommendation"],
                    "category": "image_management",
                    "line": i,
                    "rule": "latest_tag"
                })
        
        return suggestions
    
    def _check_root_user(self, lines: List[str], rule_config: Dict) -> List[Dict[str, Any]]:
        """Check for root user usage"""
        
        suggestions = []
        
        for i, line in enumerate(lines, 1):
            if re.search(rule_config["pattern"], line, re.IGNORECASE):
                suggestions.append({
                    "type": "best_practice",
                    "file": "dockerfile",
                    "severity": rule_config["severity"],
                    "message": rule_config["message"],
                    "recommendation": rule_config["recommendation"],
                    "category": "security",
                    "line": i,
                    "rule": "root_user"
                })
        
        return suggestions
    
    def _check_missing_healthcheck(self, lines: List[str], rule_config: Dict) -> List[Dict[str, Any]]:
        """Check for missing healthcheck"""
        
        suggestions = []
        has_healthcheck = any("HEALTHCHECK" in line.upper() for line in lines)
        
        if not has_healthcheck:
            suggestions.append({
                "type": "best_practice",
                "file": "dockerfile",
                "severity": rule_config["severity"],
                "message": rule_config["message"],
                "recommendation": rule_config["recommendation"],
                "category": "monitoring",
                "line": None,
                "rule": "missing_healthcheck"
            })
        
        return suggestions
    
    def _check_sudo_usage(self, lines: List[str], rule_config: Dict) -> List[Dict[str, Any]]:
        """Check for sudo usage"""
        
        suggestions = []
        
        for i, line in enumerate(lines, 1):
            if re.search(rule_config["pattern"], line, re.IGNORECASE):
                suggestions.append({
                    "type": "best_practice",
                    "file": "dockerfile",
                    "severity": rule_config["severity"],
                    "message": rule_config["message"],
                    "recommendation": rule_config["recommendation"],
                    "category": "security",
                    "line": i,
                    "rule": "sudo_usage"
                })
        
        return suggestions
    
    def _check_add_vs_copy(self, lines: List[str], rule_config: Dict) -> List[Dict[str, Any]]:
        """Check for ADD vs COPY usage"""
        
        suggestions = []
        
        for i, line in enumerate(lines, 1):
            if re.search(rule_config["pattern"], line, re.IGNORECASE):
                # Check if it's not a remote URL
                if not re.search(r"ADD\s+https?://", line, re.IGNORECASE):
                    suggestions.append({
                        "type": "best_practice",
                        "file": "dockerfile",
                        "severity": rule_config["severity"],
                        "message": rule_config["message"],
                        "recommendation": rule_config["recommendation"],
                        "category": "optimization",
                        "line": i,
                        "rule": "add_instead_of_copy"
                    })
        
        return suggestions
    
    def _check_package_cache_cleanup(self, lines: List[str], rule_config: Dict) -> List[Dict[str, Any]]:
        """Check for package cache cleanup"""
        
        suggestions = []
        
        for i, line in enumerate(lines, 1):
            if re.search(rule_config["pattern"], line, re.IGNORECASE):
                # Check if this RUN instruction cleans up cache
                run_block = self._get_run_block(lines, i - 1)
                if not self._has_cache_cleanup(run_block):
                    suggestions.append({
                        "type": "best_practice",
                        "file": "dockerfile",
                        "severity": rule_config["severity"],
                        "message": rule_config["message"],
                        "recommendation": rule_config["recommendation"],
                        "category": "optimization",
                        "line": i,
                        "rule": "package_cache_cleanup"
                    })
        
        return suggestions
    
    def _check_multiple_run_instructions(self, lines: List[str], rule_config: Dict) -> List[Dict[str, Any]]:
        """Check for multiple RUN instructions"""
        
        suggestions = []
        run_instructions = []
        
        for i, line in enumerate(lines, 1):
            if line.strip().upper().startswith("RUN"):
                run_instructions.append((i, line))
        
        if len(run_instructions) > 3:
            suggestions.append({
                "type": "best_practice",
                "file": "dockerfile",
                "severity": rule_config["severity"],
                "message": f"Found {len(run_instructions)} RUN instructions - consider combining",
                "recommendation": rule_config["recommendation"],
                "category": "optimization",
                "line": run_instructions[0][0],
                "rule": "multiple_run_instructions"
            })
        
        return suggestions
    
    def _check_missing_expose(self, lines: List[str], rule_config: Dict) -> List[Dict[str, Any]]:
        """Check for missing EXPOSE instruction"""
        
        suggestions = []
        has_expose = any("EXPOSE" in line.upper() for line in lines)
        
        if not has_expose:
            suggestions.append({
                "type": "best_practice",
                "file": "dockerfile",
                "severity": rule_config["severity"],
                "message": rule_config["message"],
                "recommendation": rule_config["recommendation"],
                "category": "documentation",
                "line": None,
                "rule": "missing_expose"
            })
        
        return suggestions
    
    def _check_workdir_missing(self, lines: List[str], rule_config: Dict) -> List[Dict[str, Any]]:
        """Check for missing WORKDIR instruction"""
        
        suggestions = []
        has_workdir = any("WORKDIR" in line.upper() for line in lines)
        
        if not has_workdir:
            suggestions.append({
                "type": "best_practice",
                "file": "dockerfile",
                "severity": rule_config["severity"],
                "message": rule_config["message"],
                "recommendation": rule_config["recommendation"],
                "category": "organization",
                "line": None,
                "rule": "workdir_missing"
            })
        
        return suggestions
    
    def _check_environment_variables(self, lines: List[str], rule_config: Dict) -> List[Dict[str, Any]]:
        """Check environment variable usage"""
        
        suggestions = []
        
        for i, line in enumerate(lines, 1):
            if re.search(rule_config["pattern"], line, re.IGNORECASE):
                # This is a basic check - could be enhanced
                suggestions.append({
                    "type": "best_practice",
                    "file": "dockerfile",
                    "severity": rule_config["severity"],
                    "message": rule_config["message"],
                    "recommendation": rule_config["recommendation"],
                    "category": "configuration",
                    "line": i,
                    "rule": "environment_variables"
                })
        
        return suggestions
    
    def _analyze_service_best_practices(self, service_name: str, service_config: Dict) -> List[Dict[str, Any]]:
        """Analyze individual service for best practices"""
        
        suggestions = []
        
        # Check restart policy
        if "restart" not in service_config:
            suggestions.append({
                "type": "best_practice",
                "file": "docker_compose",
                "severity": "medium",
                "message": f"Service '{service_name}' missing restart policy",
                "recommendation": "Add restart policy (e.g., 'restart: unless-stopped')",
                "category": "reliability",
                "service": service_name,
                "line": None
            })
        
        # Check resource limits
        if "deploy" not in service_config or "resources" not in service_config.get("deploy", {}):
            suggestions.append({
                "type": "best_practice",
                "file": "docker_compose",
                "severity": "high",
                "message": f"Service '{service_name}' missing resource limits",
                "recommendation": "Add resource limits to prevent resource exhaustion",
                "category": "resource_management",
                "service": service_name,
                "line": None
            })
        
        # Check privileged mode
        if service_config.get("privileged", False):
            suggestions.append({
                "type": "best_practice",
                "file": "docker_compose",
                "severity": "critical",
                "message": f"Service '{service_name}' running in privileged mode",
                "recommendation": "Avoid privileged mode unless absolutely necessary",
                "category": "security",
                "service": service_name,
                "line": None
            })
        
        # Check healthcheck
        if "healthcheck" not in service_config:
            suggestions.append({
                "type": "best_practice",
                "file": "docker_compose",
                "severity": "medium",
                "message": f"Service '{service_name}' missing healthcheck",
                "recommendation": "Add healthcheck configuration for better monitoring",
                "category": "monitoring",
                "service": service_name,
                "line": None
            })
        
        return suggestions
    
    def _contains_sensitive_data(self, line: str) -> bool:
        """Check if line contains sensitive data"""
        
        sensitive_patterns = [
            r".*[Pp]assword\s*=.*",
            r".*[Ss]ecret\s*=.*",
            r".*[Kk]ey\s*=.*",
            r".*[Tt]oken\s*=.*",
            r".*[Aa]pi[_-]?[Kk]ey\s*=.*"
        ]
        
        for pattern in sensitive_patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _has_default_value(self, line: str) -> bool:
        """Check if line has default/development value"""
        
        default_patterns = [
            r".*=.*test.*",
            r".*=.*dev.*",
            r".*=.*development.*",
            r".*=.*localhost.*",
            r".*=.*127\.0\.0\.1.*",
            r".*=.*example\.com.*"
        ]
        
        for pattern in default_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _check_dockerfile_compose_consistency(self, dockerfile_content: str, compose_content: str) -> List[Dict[str, Any]]:
        """Check consistency between Dockerfile and docker-compose"""
        
        suggestions = []
        
        try:
            compose_data = yaml.safe_load(compose_content)
            
            # Extract exposed ports from Dockerfile
            exposed_ports = []
            for line in dockerfile_content.split('\n'):
                if line.strip().upper().startswith('EXPOSE'):
                    parts = line.split()
                    if len(parts) > 1:
                        exposed_ports.extend(parts[1:])
            
            if compose_data and "services" in compose_data:
                for service_name, service_config in compose_data["services"].items():
                    if "build" in service_config and "ports" in service_config:
                        for port_mapping in service_config["ports"]:
                            if isinstance(port_mapping, str):
                                container_port = port_mapping.split(':')[-1]
                                if container_port not in exposed_ports:
                                    suggestions.append({
                                        "type": "best_practice",
                                        "file": "docker_compose",
                                        "severity": "low",
                                        "message": f"Service '{service_name}' maps port {container_port} but Dockerfile doesn't EXPOSE it",
                                        "recommendation": "Add EXPOSE instruction to Dockerfile or remove port mapping",
                                        "category": "consistency",
                                        "service": service_name
                                    })
        
        except yaml.YAMLError:
            pass
        
        return suggestions
    
    def _check_env_consistency(self, compose_content: str, env_content: str) -> List[Dict[str, Any]]:
        """Check environment variable consistency"""
        
        suggestions = []
        
        try:
            compose_data = yaml.safe_load(compose_content)
            env_vars = {}
            
            # Parse .env file
            for line in env_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
            
            if compose_data and "services" in compose_data:
                for service_name, service_config in compose_data["services"].items():
                    if "environment" in service_config:
                        env_section = service_config["environment"]
                        
                        if isinstance(env_section, dict):
                            for env_key, env_value in env_section.items():
                                if env_key in env_vars and env_vars[env_key] != env_value:
                                    suggestions.append({
                                        "type": "best_practice",
                                        "file": "docker_compose",
                                        "severity": "medium",
                                        "message": f"Service '{service_name}' environment variable '{env_key}' differs from .env file",
                                        "recommendation": "Ensure environment variable consistency across files",
                                        "category": "consistency",
                                        "service": service_name
                                    })
        
        except yaml.YAMLError:
            pass
        
        return suggestions
    
    def _get_run_block(self, lines: List[str], start_index: int) -> str:
        """Get the complete RUN instruction block"""
        
        run_block = lines[start_index]
        
        # Check for multi-line RUN instruction
        i = start_index + 1
        while i < len(lines):
            line = lines[i]
            if line.strip().startswith('RUN') or not line.startswith(' '):
                break
            run_block += '\n' + line
            i += 1
        
        return run_block
    
    def _has_cache_cleanup(self, run_block: str) -> bool:
        """Check if RUN block has cache cleanup"""
        
        cleanup_patterns = [
            r"rm\s+-rf\s+/var/lib/apt/lists/\*",
            r"yum\s+clean\s+all",
            r"apk\s+.*\s+--no-cache",
            r"apt-get\s+clean"
        ]
        
        for pattern in cleanup_patterns:
            if re.search(pattern, run_block, re.IGNORECASE):
                return True
        
        return False
    
    async def get_best_practices_summary(self, suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of best practices analysis"""
        
        summary = {
            "total_suggestions": len(suggestions),
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "by_category": {},
            "by_file": {},
            "top_issues": []
        }
        
        for suggestion in suggestions:
            # Count by severity
            severity = suggestion.get("severity", "low")
            summary["by_severity"][severity] += 1
            
            # Count by category
            category = suggestion.get("category", "general")
            if category not in summary["by_category"]:
                summary["by_category"][category] = 0
            summary["by_category"][category] += 1
            
            # Count by file
            file_name = suggestion.get("file", "unknown")
            if file_name not in summary["by_file"]:
                summary["by_file"][file_name] = 0
            summary["by_file"][file_name] += 1
        
        # Get top issues (critical and high severity)
        critical_high_issues = [
            s for s in suggestions 
            if s.get("severity") in ["critical", "high"]
        ]
        summary["top_issues"] = critical_high_issues[:5]
        
        return summary
