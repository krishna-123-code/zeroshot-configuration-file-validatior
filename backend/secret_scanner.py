import re
import os
from typing import Dict, List, Any
from ai_engine import AIEngine

class SecretScanner:
    def __init__(self):
        self.ai_engine = AIEngine()
        
        # Regex patterns for common secret types
        self.secret_patterns = {
            "aws_access_key": r'AKIA[0-9A-Z]{16}',
            "aws_secret_key": r'[0-9a-zA-Z/+=]{40}',
            "github_token": r'ghp_[a-zA-Z0-9]{36}',
            "github_pat": r'github_pat_[a-zA-Z0-9_]{82}',
            "jwt_token": r'eyJ[a-zA-Z0-9\-_]+\.eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+',
            "api_key_generic": r'[Aa][Pp][Ii][_-]?[Kk][Ee][Yy].*?["\']([a-zA-Z0-9\-_]{16,})["\']',
            "secret_generic": r'[Ss][Ee][Cc][Rr][Ee][Tt].*?["\']([a-zA-Z0-9\-_]{16,})["\']',
            "password": r'[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd].*?["\']([^\s"\']{6,})["\']',
            "token": r'[Tt][Oo][Kk][Ee][Nn].*?["\']([a-zA-Z0-9\-_]{16,})["\']',
            "private_key": r'-----BEGIN (RSA |OPENSSH |DSA |EC |PGP )?PRIVATE KEY-----',
            "database_url": r'[Dd][Aa][Tt][Aa][Bb][Aa][Ss][Ee].*[Uu][Rr][Ll].*?["\']([^\s"\']+)["\']',
            "connection_string": r'[Cc][Oo][Nn][Nn][Ee][Cc][Tt][Ii][Oo][Nn].*[Ss][Tt][Rr][Ii][Nn][Gg].*?["\']([^\s"\']+)["\']',
            "slack_token": r'xox[baprs]-[a-zA-Z0-9-]+',
            "slack_webhook": r'https://hooks\.slack\.com/services/[A-Z0-9]{9}/[A-Z0-9]{9}/[a-zA-Z0-9]{24}',
            "google_api_key": r'AIza[0-9A-Za-z\-_]{35}',
            "heroku_api_key": r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            "mailgun_key": r'key-[0-9a-zA-Z]{32}',
            "twilio_key": r'SK[0-9a-fA-F]{32}',
            "stripe_key": r'sk_live_[0-9a-zA-Z]{24}',
            "docker_hub_token": r'dckr_pat_[a-zA-Z0-9_-]{114}',
            "npm_token": r'npm_[a-zA-Z0-9_-]{36}',
            "ssh_key": r'ssh-rsa [A-Za-z0-9+/]+[=]{0,3}(\s+.+)?',
        }
        
        # High-confidence patterns (less likely to be false positives)
        self.high_confidence_patterns = [
            "aws_access_key",
            "github_token", 
            "github_pat",
            "private_key",
            "slack_token",
            "slack_webhook",
            "google_api_key",
            "heroku_api_key",
            "mailgun_key",
            "twilio_key",
            "stripe_key",
            "docker_hub_token",
            "npm_token",
            "ssh_key"
        ]
        
        # Patterns that need AI confirmation
        self.ai_confirmation_patterns = [
            "api_key_generic",
            "secret_generic", 
            "password",
            "token",
            "database_url",
            "connection_string"
        ]
    
    async def scan_secrets(self, file_contents: Dict[str, str]) -> List[Dict[str, Any]]:
        """Scan all files for potential secrets"""
        
        detected_secrets = []
        
        for file_type, content in file_contents.items():
            if content and content.strip():  # Skip None, empty, or whitespace-only values
                secrets = await self._scan_file_for_secrets(content, file_type)
                detected_secrets.extend(secrets)
        
        return detected_secrets
    
    async def _scan_file_for_secrets(self, content: str, file_type: str) -> List[Dict[str, Any]]:
        """Scan a single file for secrets"""
        
        secrets = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments and empty lines
            if line.strip().startswith('#') or not line.strip():
                continue
            
            # Check each secret pattern
            for pattern_name, pattern in self.secret_patterns.items():
                matches = re.finditer(pattern, line, re.IGNORECASE)
                
                for match in matches:
                    secret_value = match.group(1) if match.groups() else match.group(0)
                    
                    # Determine initial confidence
                    if pattern_name in self.high_confidence_patterns:
                        confidence = 85
                        needs_ai_confirmation = False
                    else:
                        confidence = 60
                        needs_ai_confirmation = True
                    
                    # Determine severity based on pattern
                    severity = self._get_severity_for_pattern(pattern_name)
                    
                    secret_info = {
                        "type": "secret_detected",
                        "file": file_type,
                        "line": line_num,
                        "secret_type": pattern_name,
                        "secret_value": self._mask_secret(secret_value),
                        "raw_value": secret_value,
                        "confidence": confidence,
                        "severity": severity,
                        "pattern_matched": pattern,
                        "context": line.strip(),
                        "needs_ai_confirmation": needs_ai_confirmation
                    }
                    
                    # Use AI to confirm if needed
                    if needs_ai_confirmation:
                        ai_confirmation = await self._ai_confirm_secret(line, content)
                        if ai_confirmation["is_secret"]:
                            secret_info["confidence"] = ai_confirmation["confidence"]
                            secret_info["severity"] = ai_confirmation["severity"]
                            secret_info["ai_confirmed"] = True
                            secret_info["ai_secret_type"] = ai_confirmation["secret_type"]
                        else:
                            # AI says it's not a secret, skip
                            continue
                    
                    secrets.append(secret_info)
        
        return secrets
    
    async def _ai_confirm_secret(self, suspected_line: str, context: str) -> Dict[str, Any]:
        """Use AI to confirm if a line contains a secret"""
        
        try:
            # Get surrounding context (2 lines before and after)
            lines = context.split('\n')
            current_line_index = -1
            
            for i, line in enumerate(lines):
                if suspected_line.strip() == line.strip():
                    current_line_index = i
                    break
            
            if current_line_index >= 0:
                start = max(0, current_line_index - 2)
                end = min(len(lines), current_line_index + 3)
                context_lines = lines[start:end]
                context_str = '\n'.join(context_lines)
            else:
                context_str = suspected_line
            
            confirmation = await self.ai_engine.confirm_secret(suspected_line, context_str)
            return confirmation
            
        except Exception as e:
            # If AI confirmation fails, return default
            return {
                "is_secret": False,
                "confidence": 0,
                "secret_type": "unknown",
                "severity": "low"
            }
    
    def _get_severity_for_pattern(self, pattern_name: str) -> str:
        """Determine severity based on secret type"""
        
        critical_patterns = [
            "aws_access_key",
            "aws_secret_key",
            "github_token",
            "github_pat",
            "private_key",
            "stripe_key",
            "database_url",
            "connection_string"
        ]
        
        high_patterns = [
            "google_api_key",
            "slack_token",
            "slack_webhook",
            "heroku_api_key",
            "mailgun_key",
            "twilio_key",
            "docker_hub_token",
            "npm_token",
            "ssh_key"
        ]
        
        medium_patterns = [
            "api_key_generic",
            "secret_generic",
            "password",
            "token"
        ]
        
        if pattern_name in critical_patterns:
            return "critical"
        elif pattern_name in high_patterns:
            return "high"
        elif pattern_name in medium_patterns:
            return "medium"
        else:
            return "low"
    
    def _mask_secret(self, secret: str) -> str:
        """Mask secret for display purposes"""
        
        if len(secret) <= 8:
            return "*" * len(secret)
        elif len(secret) <= 16:
            return secret[:4] + "*" * (len(secret) - 8) + secret[-4:]
        else:
            return secret[:6] + "*" * (len(secret) - 12) + secret[-6:]
    
    async def scan_for_entropy_secrets(self, content: str, file_type: str) -> List[Dict[str, Any]]:
        """Scan for high-entropy strings that might be secrets"""
        
        secrets = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments and empty lines
            if line.strip().startswith('#') or not line.strip():
                continue
            
            # Find quoted strings
            quoted_strings = re.findall(r'["\']([^"\']{20,})["\']', line)
            
            for quoted_string in quoted_strings:
                # Calculate entropy
                entropy = self._calculate_entropy(quoted_string)
                
                # High entropy strings are likely secrets
                if entropy > 4.5:
                    # Check if it's not a common non-secret
                    if not self._is_common_non_secret(quoted_string):
                        secret_info = {
                            "type": "secret_detected",
                            "file": file_type,
                            "line": line_num,
                            "secret_type": "high_entropy_string",
                            "secret_value": self._mask_secret(quoted_string),
                            "raw_value": quoted_string,
                            "confidence": min(75, int(entropy * 15)),
                            "severity": "medium",
                            "entropy": entropy,
                            "context": line.strip(),
                            "needs_ai_confirmation": True
                        }
                        
                        # Use AI to confirm
                        ai_confirmation = await self._ai_confirm_secret(line, content)
                        if ai_confirmation["is_secret"]:
                            secret_info["confidence"] = ai_confirmation["confidence"]
                            secret_info["severity"] = ai_confirmation["severity"]
                            secret_info["ai_confirmed"] = True
                            secret_info["ai_secret_type"] = ai_confirmation["secret_type"]
                            secrets.append(secret_info)
        
        return secrets
    
    def _calculate_entropy(self, string: str) -> float:
        """Calculate Shannon entropy of a string"""
        
        import math
        from collections import Counter
        
        if not string:
            return 0
        
        # Count character frequencies
        counter = Counter(string)
        length = len(string)
        
        # Calculate entropy
        entropy = 0
        for count in counter.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _is_common_non_secret(self, string: str) -> bool:
        """Check if string is commonly not a secret"""
        
        common_non_secrets = [
            "http://", "https://", "ftp://", "sftp://",
            "localhost", "127.0.0.1", "0.0.0.0",
            "example.com", "test.com", "demo.com",
            "username", "password", "email", "admin",
            "user", "pass", "test", "dev", "prod",
            "development", "production", "staging",
            "true", "false", "yes", "no", "on", "off",
            "debug", "info", "warn", "error", "fatal",
            "application", "service", "server", "client",
            "database", "cache", "queue", "logger",
            "config", "settings", "options", "parameters"
        ]
        
        string_lower = string.lower()
        return any(common in string_lower for common in common_non_secrets)
    
    async def get_secret_summary(self, secrets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of detected secrets"""
        
        summary = {
            "total_secrets": len(secrets),
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "by_type": {},
            "by_file": {},
            "ai_confirmed": 0,
            "high_confidence": 0
        }
        
        for secret in secrets:
            # Count by severity
            severity = secret.get("severity", "low")
            summary["by_severity"][severity] += 1
            
            # Count by type
            secret_type = secret.get("secret_type", "unknown")
            if secret_type not in summary["by_type"]:
                summary["by_type"][secret_type] = 0
            summary["by_type"][secret_type] += 1
            
            # Count by file
            file_name = secret.get("file", "unknown")
            if file_name not in summary["by_file"]:
                summary["by_file"][file_name] = 0
            summary["by_file"][file_name] += 1
            
            # Count AI confirmed
            if secret.get("ai_confirmed", False):
                summary["ai_confirmed"] += 1
            
            # Count high confidence
            if secret.get("confidence", 0) >= 80:
                summary["high_confidence"] += 1
        
        return summary
