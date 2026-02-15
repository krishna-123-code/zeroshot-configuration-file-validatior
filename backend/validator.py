import yaml
import re
import os
import subprocess
from typing import Dict, List, Any
from pathlib import Path

class ConfigValidator:
    def __init__(self):
        self.dockerfile_keywords = [
            'FROM', 'RUN', 'CMD', 'LABEL', 'EXPOSE', 'ENV', 'ADD', 'COPY',
            'ENTRYPOINT', 'VOLUME', 'USER', 'WORKDIR', 'ARG', 'ONBUILD',
            'STOPSIGNAL', 'HEALTHCHECK', 'SHELL'
        ]
    
    async def validate_syntax(self, file_contents: Dict[str, str], temp_dir: str) -> List[Dict[str, Any]]:
        """Validate syntax of Dockerfile and docker-compose.yml"""
        
        syntax_errors = []
        
        # Validate Dockerfile
        if file_contents.get("dockerfile") and file_contents["dockerfile"].strip():
            dockerfile_errors = await self._validate_dockerfile_syntax(
                file_contents["dockerfile"], temp_dir
            )
            syntax_errors.extend(dockerfile_errors)
        
        # Validate docker-compose.yml
        if file_contents.get("docker_compose") and file_contents["docker_compose"].strip():
            compose_errors = await self._validate_docker_compose_syntax(
                file_contents["docker_compose"], temp_dir
            )
            syntax_errors.extend(compose_errors)
        
        # Validate .env file
        if file_contents.get("env_file") and file_contents["env_file"].strip():
            env_errors = await self._validate_env_syntax(file_contents["env_file"])
            syntax_errors.extend(env_errors)
        
        return syntax_errors
    
    async def detect_logic_conflicts(self, file_contents: Dict[str, str]) -> List[Dict[str, Any]]:
        """Detect logic conflicts across multiple files"""
        
        conflicts = []
        
        # Cross-file analysis
        if (file_contents.get("dockerfile") and file_contents["dockerfile"].strip() and 
            file_contents.get("docker_compose") and file_contents["docker_compose"].strip()):
            conflicts.extend(self._check_dockerfile_compose_conflicts(
                file_contents["dockerfile"],
                file_contents["docker_compose"]
            ))
        
        if (file_contents.get("docker_compose") and file_contents["docker_compose"].strip() and 
            file_contents.get("env_file") and file_contents["env_file"].strip()):
            conflicts.extend(self._check_compose_env_conflicts(
                file_contents["docker_compose"],
                file_contents["env_file"]
            ))
        
        # Port conflicts
        if file_contents.get("docker_compose") and file_contents["docker_compose"].strip():
            conflicts.extend(self._check_port_conflicts(file_contents["docker_compose"]))
        
        # Service dependencies
        if file_contents.get("docker_compose") and file_contents["docker_compose"].strip():
            conflicts.extend(self._check_service_dependencies(file_contents["docker_compose"]))
        
        return conflicts
    
    async def _validate_dockerfile_syntax(self, dockerfile_content: str, temp_dir: str) -> List[Dict[str, Any]]:
        """Validate Dockerfile syntax using Hadolint"""
        
        errors = []
        
        # Write Dockerfile to temp directory
        dockerfile_path = os.path.join(temp_dir, "Dockerfile")
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)
        
        try:
            # Run Hadolint
            result = subprocess.run(
                ["hadolint", dockerfile_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                # Parse Hadolint output
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        error_info = self._parse_hadolint_line(line)
                        if error_info:
                            errors.append(error_info)
        
        except subprocess.TimeoutExpired:
            errors.append({
                "type": "syntax_error",
                "file": "dockerfile",
                "message": "Hadolint validation timed out",
                "severity": "warning",
                "line": None,
                "rule": "timeout"
            })
        except FileNotFoundError:
            # Hadolint not installed, do basic validation
            errors.extend(self._basic_dockerfile_validation(dockerfile_content))
        
        return errors
    
    async def _validate_docker_compose_syntax(self, compose_content: str, temp_dir: str) -> List[Dict[str, Any]]:
        """Validate docker-compose.yml syntax"""
        
        errors = []
        
        try:
            # Parse YAML
            compose_data = yaml.safe_load(compose_content)
            
            if not isinstance(compose_data, dict):
                errors.append({
                    "type": "syntax_error",
                    "file": "docker_compose",
                    "message": "Invalid YAML structure - root must be a dictionary",
                    "severity": "error",
                    "line": 1,
                    "rule": "yaml_structure"
                })
                return errors
            
            # Check required fields
            if "version" not in compose_data and "services" not in compose_data:
                errors.append({
                    "type": "syntax_error",
                    "file": "docker_compose",
                    "message": "Missing 'services' section in docker-compose.yml",
                    "severity": "error",
                    "line": None,
                    "rule": "missing_services"
                })
            
            # Validate services
            if "services" in compose_data:
                services = compose_data["services"]
                if not isinstance(services, dict):
                    errors.append({
                        "type": "syntax_error",
                        "file": "docker_compose",
                        "message": "'services' must be a dictionary",
                        "severity": "error",
                        "line": None,
                        "rule": "invalid_services_type"
                    })
                else:
                    for service_name, service_config in services.items():
                        service_errors = self._validate_service_config(
                            service_name, service_config
                        )
                        errors.extend(service_errors)
        
        except yaml.YAMLError as e:
            errors.append({
                "type": "syntax_error",
                "file": "docker_compose",
                "message": f"YAML parsing error: {str(e)}",
                "severity": "error",
                "line": getattr(e, 'problem_mark', {}).get('line', None),
                "rule": "yaml_parse_error"
            })
        
        return errors
    
    async def _validate_env_syntax(self, env_content: str) -> List[Dict[str, Any]]:
        """Validate .env file syntax"""
        
        errors = []
        lines = env_content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Check for valid KEY=VALUE format
            if '=' not in line:
                errors.append({
                    "type": "syntax_error",
                    "file": "env_file",
                    "message": f"Invalid environment variable format at line {i}: {line}",
                    "severity": "warning",
                    "line": i,
                    "rule": "env_format"
                })
                continue
            
            # Check for invalid characters in key
            key, value = line.split('=', 1)
            if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', key):
                errors.append({
                    "type": "syntax_error",
                    "file": "env_file",
                    "message": f"Invalid environment variable name at line {i}: {key}",
                    "severity": "warning",
                    "line": i,
                    "rule": "env_name_format"
                })
        
        return errors
    
    def _parse_hadolint_line(self, line: str) -> Dict[str, Any]:
        """Parse Hadolint output line"""
        
        # Hadolint format: /path/to/Dockerfile:line:severity message (code)
        match = re.match(r'^.*?:(\d+):(\w+)\s+(.+?)\s+\((\w+)\)$', line)
        
        if match:
            line_num, severity, message, code = match.groups()
            return {
                "type": "syntax_error",
                "file": "dockerfile",
                "message": message,
                "severity": severity.lower(),
                "line": int(line_num),
                "rule": code
            }
        
        return None
    
    def _basic_dockerfile_validation(self, dockerfile_content: str) -> List[Dict[str, Any]]:
        """Basic Dockerfile validation without Hadolint"""
        
        errors = []
        lines = dockerfile_content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            # Check if instruction is valid
            parts = line.split()
            if parts and parts[0].upper() not in self.dockerfile_keywords:
                errors.append({
                    "type": "syntax_error",
                    "file": "dockerfile",
                    "message": f"Invalid Dockerfile instruction: {parts[0]}",
                    "severity": "error",
                    "line": i,
                    "rule": "invalid_instruction"
                })
        
        # Check for FROM instruction
        has_from = any(line.strip().upper().startswith('FROM') for line in lines)
        if not has_from:
            errors.append({
                "type": "syntax_error",
                "file": "dockerfile",
                "message": "Dockerfile must start with FROM instruction",
                "severity": "error",
                "line": 1,
                "rule": "missing_from"
            })
        
        return errors
    
    def _validate_service_config(self, service_name: str, service_config: Any) -> List[Dict[str, Any]]:
        """Validate individual service configuration"""
        
        errors = []
        
        if not isinstance(service_config, dict):
            errors.append({
                "type": "syntax_error",
                "file": "docker_compose",
                "message": f"Service '{service_name}' configuration must be a dictionary",
                "severity": "error",
                "line": None,
                "rule": "invalid_service_config"
            })
            return errors
        
        # Check for image or build
        if "image" not in service_config and "build" not in service_config:
            errors.append({
                "type": "syntax_error",
                "file": "docker_compose",
                "message": f"Service '{service_name}' must have either 'image' or 'build' configuration",
                "severity": "error",
                "line": None,
                "rule": "missing_image_or_build"
            })
        
        # Validate ports if present
        if "ports" in service_config:
            ports = service_config["ports"]
            if not isinstance(ports, list):
                errors.append({
                    "type": "syntax_error",
                    "file": "docker_compose",
                    "message": f"Service '{service_name}' ports must be a list",
                    "severity": "error",
                    "line": None,
                    "rule": "invalid_ports_format"
                })
        
        return errors
    
    def _check_dockerfile_compose_conflicts(self, dockerfile_content: str, compose_content: str) -> List[Dict[str, Any]]:
        """Check for conflicts between Dockerfile and docker-compose"""
        
        conflicts = []
        
        try:
            compose_data = yaml.safe_load(compose_content)
            
            # Check if compose uses build but Dockerfile has EXPOSE that conflicts with compose ports
            if compose_data and "services" in compose_data:
                for service_name, service_config in compose_data["services"].items():
                    if "build" in service_config and "ports" in service_config:
                        # Check if Dockerfile EXPOSE ports match compose ports
                        exposed_ports = self._extract_exposed_ports(dockerfile_content)
                        compose_ports = service_config["ports"]
                        
                        for port_mapping in compose_ports:
                            if isinstance(port_mapping, str):
                                # Extract container port from "host:container" or just "container"
                                container_port = port_mapping.split(':')[-1]
                                if container_port not in exposed_ports:
                                    conflicts.append({
                                        "type": "logic_conflict",
                                        "file": "docker_compose",
                                        "message": f"Service '{service_name}' maps port {container_port} but Dockerfile doesn't EXPOSE this port",
                                        "severity": "warning",
                                        "service": service_name,
                                        "conflict_type": "port_expose_mismatch"
                                    })
        
        except yaml.YAMLError:
            pass  # Already handled in syntax validation
        
        return conflicts
    
    def _check_compose_env_conflicts(self, compose_content: str, env_content: str) -> List[Dict[str, Any]]:
        """Check for conflicts between docker-compose and .env file"""
        
        conflicts = []
        
        try:
            compose_data = yaml.safe_load(compose_content)
            env_vars = self._parse_env_file(env_content)
            
            if compose_data and "services" in compose_data:
                for service_name, service_config in compose_data["services"].items():
                    if "environment" in service_config:
                        env_section = service_config["environment"]
                        
                        if isinstance(env_section, dict):
                            for env_key, env_value in env_section.items():
                                if env_key in env_vars and env_vars[env_key] != env_value:
                                    conflicts.append({
                                        "type": "logic_conflict",
                                        "file": "docker_compose",
                                        "message": f"Service '{service_name}' environment variable '{env_key}' conflicts with .env file value",
                                        "severity": "warning",
                                        "service": service_name,
                                        "conflict_type": "env_value_conflict",
                                        "env_key": env_key,
                                        "compose_value": env_value,
                                        "env_file_value": env_vars[env_key]
                                    })
        
        except yaml.YAMLError:
            pass
        
        return conflicts
    
    def _check_port_conflicts(self, compose_content: str) -> List[Dict[str, Any]]:
        """Check for port conflicts in docker-compose"""
        
        conflicts = []
        
        try:
            compose_data = yaml.safe_load(compose_content)
            used_ports = {}
            
            if compose_data and "services" in compose_data:
                for service_name, service_config in compose_data["services"].items():
                    if "ports" in service_config:
                        for port_mapping in service_config["ports"]:
                            if isinstance(port_mapping, str):
                                # Extract host port from "host:container" or just "host"
                                host_port = port_mapping.split(':')[0]
                                
                                if host_port in used_ports:
                                    conflicts.append({
                                        "type": "logic_conflict",
                                        "file": "docker_compose",
                                        "message": f"Port {host_port} is used by both '{used_ports[host_port]}' and '{service_name}' services",
                                        "severity": "error",
                                        "service": service_name,
                                        "conflict_type": "port_conflict",
                                        "port": host_port,
                                        "conflicting_service": used_ports[host_port]
                                    })
                                else:
                                    used_ports[host_port] = service_name
        
        except yaml.YAMLError:
            pass
        
        return conflicts
    
    def _check_service_dependencies(self, compose_content: str) -> List[Dict[str, Any]]:
        """Check for undefined service dependencies"""
        
        conflicts = []
        
        try:
            compose_data = yaml.safe_load(compose_content)
            
            if compose_data and "services" in compose_data:
                defined_services = set(compose_data["services"].keys())
                
                for service_name, service_config in compose_data["services"].items():
                    if "depends_on" in service_config:
                        dependencies = service_config["depends_on"]
                        
                        if isinstance(dependencies, list):
                            for dep in dependencies:
                                if dep not in defined_services:
                                    conflicts.append({
                                        "type": "logic_conflict",
                                        "file": "docker_compose",
                                        "message": f"Service '{service_name}' depends on undefined service '{dep}'",
                                        "severity": "error",
                                        "service": service_name,
                                        "conflict_type": "undefined_dependency",
                                        "missing_service": dep
                                    })
                        
                        elif isinstance(dependencies, dict):
                            for dep in dependencies.keys():
                                if dep not in defined_services:
                                    conflicts.append({
                                        "type": "logic_conflict",
                                        "file": "docker_compose",
                                        "message": f"Service '{service_name}' depends on undefined service '{dep}'",
                                        "severity": "error",
                                        "service": service_name,
                                        "conflict_type": "undefined_dependency",
                                        "missing_service": dep
                                    })
        
        except yaml.YAMLError:
            pass
        
        return conflicts
    
    def _extract_exposed_ports(self, dockerfile_content: str) -> List[str]:
        """Extract EXPOSE ports from Dockerfile"""
        
        exposed_ports = []
        lines = dockerfile_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.upper().startswith('EXPOSE'):
                parts = line.split()
                if len(parts) > 1:
                    exposed_ports.extend(parts[1:])
        
        return exposed_ports
    
    def _parse_env_file(self, env_content: str) -> Dict[str, str]:
        """Parse .env file content into dictionary"""
        
        env_vars = {}
        lines = env_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
        
        return env_vars
