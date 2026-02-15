import subprocess
import json
import os
import re
from typing import Dict, List, Any
from pathlib import Path

class SecurityScanner:
    def __init__(self):
        self.critical_severity_levels = ["CRITICAL", "HIGH"]
        self.warning_severity_levels = ["MEDIUM", "LOW"]
    
    async def scan_security(self, file_contents: Dict[str, str], temp_dir: str) -> List[Dict[str, Any]]:
        """Perform comprehensive security scanning"""
        
        security_issues = []
        
        # Scan Dockerfile with Hadolint (security rules)
        if file_contents.get("dockerfile") and file_contents["dockerfile"].strip():
            dockerfile_issues = await self._scan_dockerfile_security(
                file_contents["dockerfile"], temp_dir
            )
            security_issues.extend(dockerfile_issues)
        
        # Scan with Trivy if available
        if file_contents.get("dockerfile") and file_contents["dockerfile"].strip():
            trivy_issues = await self._scan_with_trivy(file_contents["dockerfile"], temp_dir)
            security_issues.extend(trivy_issues)
        
        # Scan docker-compose for security issues
        if file_contents.get("docker_compose") and file_contents["docker_compose"].strip():
            compose_issues = await self._scan_docker_compose_security(
                file_contents["docker_compose"]
            )
            security_issues.extend(compose_issues)
        
        # Scan .env for security issues
        if file_contents.get("env_file") and file_contents["env_file"].strip():
            env_issues = await self._scan_env_security(file_contents["env_file"])
            security_issues.extend(env_issues)
        
        return security_issues
    
    async def _scan_dockerfile_security(self, dockerfile_content: str, temp_dir: str) -> List[Dict[str, Any]]:
        """Scan Dockerfile for security issues using Hadolint"""
        
        issues = []
        
        # Write Dockerfile to temp directory
        dockerfile_path = os.path.join(temp_dir, "Dockerfile")
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)
        
        try:
            # Run Hadolint with security focus
            result = subprocess.run(
                ["hadolint", "--failure-threshold", "warning", dockerfile_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                # Parse Hadolint output for security-related issues
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        issue_info = self._parse_hadolint_security_line(line)
                        if issue_info and self._is_security_related(issue_info):
                            issues.append(issue_info)
        
        except subprocess.TimeoutExpired:
            issues.append({
                "type": "security_issue",
                "file": "dockerfile",
                "message": "Security scan timed out",
                "severity": "warning",
                "line": None,
                "rule": "timeout",
                "scanner": "hadolint"
            })
        except FileNotFoundError:
            # Hadolint not available, do basic security checks
            issues.extend(self._basic_dockerfile_security_scan(dockerfile_content))
        
        return issues
    
    async def _scan_with_trivy(self, dockerfile_content: str, temp_dir: str) -> List[Dict[str, Any]]:
        """Scan Docker image with Trivy"""
        
        issues = []
        
        # Write Dockerfile to temp directory
        dockerfile_path = os.path.join(temp_dir, "Dockerfile")
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)
        
        try:
            # Build a temporary image name
            image_name = "zeroguard-temp-scan"
            
            # Build Docker image
            build_result = subprocess.run(
                ["docker", "build", "-t", image_name, temp_dir],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if build_result.returncode == 0:
                # Scan with Trivy
                trivy_result = subprocess.run(
                    ["trivy", "image", "--format", "json", image_name],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if trivy_result.returncode == 0:
                    # Parse Trivy JSON output
                    trivy_data = json.loads(trivy_result.stdout)
                    trivy_issues = self._parse_trivy_output(trivy_data)
                    issues.extend(trivy_issues)
                
                # Cleanup temporary image
                subprocess.run(
                    ["docker", "rmi", "-f", image_name],
                    capture_output=True,
                    timeout=30
                )
            else:
                issues.append({
                    "type": "security_issue",
                    "file": "dockerfile",
                    "message": f"Failed to build Docker image for Trivy scan: {build_result.stderr}",
                    "severity": "warning",
                    "line": None,
                    "rule": "build_failure",
                    "scanner": "trivy"
                })
        
        except subprocess.TimeoutExpired:
            issues.append({
                "type": "security_issue",
                "file": "dockerfile",
                "message": "Trivy scan timed out",
                "severity": "warning",
                "line": None,
                "rule": "timeout",
                "scanner": "trivy"
            })
        except FileNotFoundError:
            issues.append({
                "type": "security_issue",
                "file": "dockerfile",
                "message": "Trivy or Docker not available for security scanning",
                "severity": "info",
                "line": None,
                "rule": "scanner_unavailable",
                "scanner": "trivy"
            })
        except Exception as e:
            issues.append({
                "type": "security_issue",
                "file": "dockerfile",
                "message": f"Trivy scan failed: {str(e)}",
                "severity": "warning",
                "line": None,
                "rule": "scan_error",
                "scanner": "trivy"
            })
        
        return issues
    
    async def _scan_docker_compose_security(self, compose_content: str) -> List[Dict[str, Any]]:
        """Scan docker-compose.yml for security issues"""
        
        issues = []
        
        try:
            import yaml
            compose_data = yaml.safe_load(compose_content)
            
            if compose_data and "services" in compose_data:
                for service_name, service_config in compose_data["services"].items():
                    service_issues = self._scan_service_security(service_name, service_config)
                    issues.extend(service_issues)
        
        except Exception as e:
            issues.append({
                "type": "security_issue",
                "file": "docker_compose",
                "message": f"Failed to parse docker-compose for security scan: {str(e)}",
                "severity": "warning",
                "line": None,
                "rule": "parse_error",
                "scanner": "builtin"
            })
        
        return issues
    
    async def _scan_env_security(self, env_content: str) -> List[Dict[str, Any]]:
        """Scan .env file for security issues"""
        
        issues = []
        lines = env_content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            # Check for potential secrets in environment variables
            if self._looks_like_secret(line):
                issues.append({
                    "type": "security_issue",
                    "file": "env_file",
                    "message": f"Potential secret detected in environment variable at line {i}",
                    "severity": "high",
                    "line": i,
                    "rule": "secret_in_env",
                    "scanner": "builtin"
                })
            
            # Check for insecure configurations
            if self._is_insecure_env_config(line):
                issues.append({
                    "type": "security_issue",
                    "file": "env_file",
                    "message": f"Insecure configuration detected at line {i}: {line}",
                    "severity": "medium",
                    "line": i,
                    "rule": "insecure_config",
                    "scanner": "builtin"
                })
        
        return issues
    
    def _parse_hadolint_security_line(self, line: str) -> Dict[str, Any]:
        """Parse Hadolint output for security issues"""
        
        match = re.match(r'^.*?:(\d+):(\w+)\s+(.+?)\s+\((\w+)\)$', line)
        
        if match:
            line_num, severity, message, code = match.groups()
            return {
                "type": "security_issue",
                "file": "dockerfile",
                "message": message,
                "severity": severity.lower(),
                "line": int(line_num),
                "rule": code,
                "scanner": "hadolint"
            }
        
        return None
    
    def _is_security_related(self, issue: Dict[str, Any]) -> bool:
        """Check if Hadolint issue is security-related"""
        
        security_rules = [
            "DL3002",  # Last USER should not be root
            "DL3008",  # Pin versions in apt-get install
            "DL3009",  # Delete the apt-get lists after installing
            "DL3013",  # Pin versions in pip
            "DL3018",  # Pin versions in apk add
            "DL3042",  # Avoid use of workdir
            "DL3058",  # Multiple consecutive `RUN` instructions
            "DL4000",  # MAINTAINER is deprecated
            "DL4001",  # Either use Wget or Curl but not both
            "DL4006",  # Set the SHELL option
            "SC1015",  # Use shebang to specify interpreter
            "SC2039",  # In POSIX sh, something is undefined
            "SC2086",  # Double quote to prevent globbing
            "SC2155",  # Declare and assign separately
        ]
        
        return issue.get("rule", "") in security_rules
    
    def _basic_dockerfile_security_scan(self, dockerfile_content: str) -> List[Dict[str, Any]]:
        """Basic security scan without external tools"""
        
        issues = []
        lines = dockerfile_content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            # Check for root user
            if line.upper().startswith('USER') and 'root' in line.lower():
                issues.append({
                    "type": "security_issue",
                    "file": "dockerfile",
                    "message": "Running as root user is not recommended",
                    "severity": "high",
                    "line": i,
                    "rule": "root_user",
                    "scanner": "builtin"
                })
            
            # Check for sudo usage
            if 'sudo' in line.lower():
                issues.append({
                    "type": "security_issue",
                    "file": "dockerfile",
                    "message": "Avoid using sudo in Dockerfile",
                    "severity": "medium",
                    "line": i,
                    "rule": "sudo_usage",
                    "scanner": "builtin"
                })
            
            # Check for adding sensitive files
            if line.upper().startswith('ADD') or line.upper().startswith('COPY'):
                parts = line.split()
                if len(parts) > 1:
                    source = parts[1]
                    if any(sensitive in source.lower() for sensitive in ['.env', 'secret', 'key', 'password']):
                        issues.append({
                            "type": "security_issue",
                            "file": "dockerfile",
                            "message": f"Potentially sensitive file being copied: {source}",
                            "severity": "high",
                            "line": i,
                            "rule": "sensitive_file_copy",
                            "scanner": "builtin"
                        })
        
        return issues
    
    def _parse_trivy_output(self, trivy_data: Dict) -> List[Dict[str, Any]]:
        """Parse Trivy JSON output"""
        
        issues = []
        
        try:
            if "Results" in trivy_data:
                for result in trivy_data["Results"]:
                    if "Vulnerabilities" in result:
                        for vuln in result["Vulnerabilities"]:
                            severity = vuln.get("Severity", "UNKNOWN").lower()
                            
                            issues.append({
                                "type": "security_issue",
                                "file": "dockerfile",
                                "message": f"{vuln.get('Title', 'Unknown vulnerability')} in {vuln.get('PkgName', 'unknown package')}",
                                "severity": severity,
                                "line": None,
                                "rule": "vulnerability",
                                "scanner": "trivy",
                                "vulnerability_id": vuln.get("VulnerabilityID", ""),
                                "package": vuln.get("PkgName", ""),
                                "installed_version": vuln.get("InstalledVersion", ""),
                                "fixed_version": vuln.get("FixedVersion", ""),
                                "cvss_score": vuln.get("CVSS", {}).get("nvd", {}).get("V3Score"),
                                "references": vuln.get("References", [])
                            })
        
        except Exception as e:
            issues.append({
                "type": "security_issue",
                "file": "dockerfile",
                "message": f"Failed to parse Trivy output: {str(e)}",
                "severity": "warning",
                "line": None,
                "rule": "parse_error",
                "scanner": "trivy"
            })
        
        return issues
    
    def _scan_service_security(self, service_name: str, service_config: Dict) -> List[Dict[str, Any]]:
        """Scan individual service for security issues"""
        
        issues = []
        
        # Check for privileged mode
        if service_config.get("privileged", False):
            issues.append({
                "type": "security_issue",
                "file": "docker_compose",
                "message": f"Service '{service_name}' is running in privileged mode",
                "severity": "high",
                "line": None,
                "rule": "privileged_mode",
                "scanner": "builtin",
                "service": service_name
            })
        
        # Check for running as root
        if "user" in service_config and service_config["user"] == "root":
            issues.append({
                "type": "security_issue",
                "file": "docker_compose",
                "message": f"Service '{service_name}' is running as root user",
                "severity": "high",
                "line": None,
                "rule": "root_user",
                "scanner": "builtin",
                "service": service_name
            })
        
        # Check for Docker socket mounting
        if "volumes" in service_config:
            for volume in service_config["volumes"]:
                if "/var/run/docker.sock" in str(volume):
                    issues.append({
                        "type": "security_issue",
                        "file": "docker_compose",
                        "message": f"Service '{service_name}' is mounting Docker socket",
                        "severity": "critical",
                        "line": None,
                        "rule": "docker_socket_mount",
                        "scanner": "builtin",
                        "service": service_name
                    })
        
        # Check for capabilities
        if "cap_add" in service_config:
            dangerous_caps = ["SYS_ADMIN", "NET_ADMIN", "SYS_PTRACE"]
            for cap in service_config["cap_add"]:
                if cap in dangerous_caps:
                    issues.append({
                        "type": "security_issue",
                        "file": "docker_compose",
                        "message": f"Service '{service_name}' has dangerous capability: {cap}",
                        "severity": "high",
                        "line": None,
                        "rule": "dangerous_capability",
                        "scanner": "builtin",
                        "service": service_name,
                        "capability": cap
                    })
        
        return issues
    
    def _looks_like_secret(self, line: str) -> bool:
        """Check if line looks like it contains a secret"""
        
        secret_patterns = [
            r'.*[Pp]assword\s*=\s*.+',
            r'.*[Ss]ecret\s*=\s*.+',
            r'.*[Aa]pi[_-]?[Kk]ey\s*=\s*.+',
            r'.*[Tt]oken\s*=\s*.+',
            r'.*[Kk]ey\s*=\s*.+',
            r'.*[Aa]ccess[_-]?[Tt]oken\s*=\s*.+',
            r'.*[Rr]efresh[_-]?[Tt]oken\s*=\s*.+',
            r'.*[Pp]rivate[_-]?[Kk]ey\s*=\s*.+',
        ]
        
        for pattern in secret_patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _is_insecure_env_config(self, line: str) -> bool:
        """Check for insecure environment configurations"""
        
        insecure_patterns = [
            r'.*[Dd]ebug\s*=\s*true',
            r'.*[Tt]est\s*=\s*true',
            r'.*[Dd]evelopment\s*=\s*true',
            r'.*[Ii]nsecure\s*=\s*true',
            r'.*[Ss]sl[_-]?[Vv]erify\s*=\s*false',
            r'.*[Cc]ert[_-]?[Vv]erify\s*=\s*false',
        ]
        
        for pattern in insecure_patterns:
            if re.match(pattern, line):
                return True
        
        return False
