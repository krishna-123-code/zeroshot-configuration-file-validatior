import yaml
import re
from typing import Dict, List, Any, Tuple

class DependencyGraphGenerator:
    def __init__(self):
        self.node_types = {
            "service": "service",
            "volume": "volume", 
            "network": "network",
            "external": "external",
            "database": "database",
            "cache": "cache",
            "api": "api",
            "web": "web"
        }
        
        self.edge_types = {
            "depends_on": "depends_on",
            "volume_mount": "volume_mount",
            "network_connection": "network_connection",
            "environment_link": "environment_link",
            "port_binding": "port_binding"
        }
    
    async def generate_graph(self, file_contents: Dict[str, str]) -> Dict[str, Any]:
        """Generate dependency graph from configuration files"""
        
        nodes = []
        edges = []
        
        if file_contents.get("docker_compose") and file_contents["docker_compose"].strip():
            compose_content = file_contents["docker_compose"]
            
            try:
                compose_data = yaml.safe_load(compose_content)
                
                if compose_data and "services" in compose_data:
                    # Generate service nodes and edges
                    service_nodes, service_edges = await self._generate_service_dependencies(
                        compose_data["services"]
                    )
                    nodes.extend(service_nodes)
                    edges.extend(service_edges)
                    
                    # Generate volume nodes and edges
                    if "volumes" in compose_data:
                        volume_nodes, volume_edges = await self._generate_volume_dependencies(
                            compose_data["volumes"], compose_data["services"]
                        )
                        nodes.extend(volume_nodes)
                        edges.extend(volume_edges)
                    
                    # Generate network nodes and edges
                    if "networks" in compose_data:
                        network_nodes, network_edges = await self._generate_network_dependencies(
                            compose_data["networks"], compose_data["services"]
                        )
                        nodes.extend(network_nodes)
                        edges.extend(network_edges)
                
                # Add external dependencies from environment variables
                if file_contents.get("env_file") and file_contents["env_file"].strip():
                    env_nodes, env_edges = await self._generate_env_dependencies(
                        file_contents["env_file"], nodes
                    )
                    nodes.extend(env_nodes)
                    edges.extend(env_edges)
            
            except yaml.YAMLError:
                # Return error node if YAML is invalid
                nodes.append({
                    "id": "parse_error",
                    "type": "error",
                    "label": "Parse Error",
                    "description": "Invalid docker-compose.yml syntax",
                    "position": {"x": 0, "y": 0},
                    "data": {"error": "YAML parsing failed"}
                })
        
        # Analyze graph metrics
        graph_metrics = self._calculate_graph_metrics(nodes, edges)
        
        # Identify critical paths
        critical_paths = self._identify_critical_paths(nodes, edges)
        
        # Detect circular dependencies
        circular_deps = self._detect_circular_dependencies(nodes, edges)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metrics": graph_metrics,
            "critical_paths": critical_paths,
            "circular_dependencies": circular_deps,
            "layout": self._suggest_layout(nodes, edges)
        }
    
    async def _generate_service_dependencies(self, services: Dict) -> Tuple[List[Dict], List[Dict]]:
        """Generate service nodes and dependency edges"""
        
        nodes = []
        edges = []
        
        # Create service nodes
        for service_name, service_config in services.items():
            node_type = self._determine_service_type(service_name, service_config)
            
            node = {
                "id": service_name,
                "type": node_type,
                "label": service_name,
                "description": self._generate_service_description(service_name, service_config),
                "position": self._calculate_node_position(service_name, len(services)),
                "data": {
                    "image": service_config.get("image", ""),
                    "build": service_config.get("build", ""),
                    "ports": service_config.get("ports", []),
                    "environment": service_config.get("environment", {}),
                    "restart": service_config.get("restart", ""),
                    "depends_on": service_config.get("depends_on", []),
                    "healthcheck": service_config.get("healthcheck", {}),
                    "volumes": service_config.get("volumes", []),
                    "networks": service_config.get("networks", [])
                }
            }
            nodes.append(node)
            
            # Create dependency edges
            if "depends_on" in service_config:
                dependencies = service_config["depends_on"]
                
                if isinstance(dependencies, list):
                    for dep in dependencies:
                        edge = {
                            "id": f"{service_name}_depends_on_{dep}",
                            "source": service_name,
                            "target": dep,
                            "type": self.edge_types["depends_on"],
                            "label": "depends on",
                            "data": {
                                "dependency_type": "service_dependency",
                                "required": True
                            }
                        }
                        edges.append(edge)
                
                elif isinstance(dependencies, dict):
                    for dep, dep_config in dependencies.items():
                        condition = dep_config.get("condition", "service_started")
                        edge = {
                            "id": f"{service_name}_depends_on_{dep}",
                            "source": service_name,
                            "target": dep,
                            "type": self.edge_types["depends_on"],
                            "label": f"depends on ({condition})",
                            "data": {
                                "dependency_type": "service_dependency",
                                "condition": condition,
                                "required": True
                            }
                        }
                        edges.append(edge)
        
        return nodes, edges
    
    async def _generate_volume_dependencies(
        self, 
        volumes: Dict, 
        services: Dict
    ) -> Tuple[List[Dict], List[Dict]]:
        """Generate volume nodes and mount edges"""
        
        nodes = []
        edges = []
        
        # Create volume nodes
        for volume_name, volume_config in volumes.items():
            node = {
                "id": f"volume_{volume_name}",
                "type": self.node_types["volume"],
                "label": f"Volume: {volume_name}",
                "description": f"Storage volume: {volume_name}",
                "position": self._calculate_volume_position(volume_name, len(volumes)),
                "data": {
                    "driver": volume_config.get("driver", "local"),
                    "external": volume_config.get("external", False),
                    "driver_opts": volume_config.get("driver_opts", {}),
                    "labels": volume_config.get("labels", {})
                }
            }
            nodes.append(node)
        
        # Create volume mount edges
        for service_name, service_config in services.items():
            if "volumes" in service_config:
                for volume_mount in service_config["volumes"]:
                    if isinstance(volume_mount, str):
                        # Parse volume mount string
                        parts = volume_mount.split(':')
                        if len(parts) >= 1:
                            volume_name = parts[0]
                            if volume_name.startswith('./'):
                                volume_name = f"volume_{volume_name.replace('./', '').replace('/', '_')}"
                            elif not volume_name.startswith('/'):
                                volume_name = f"volume_{volume_name}"
                            
                            edge = {
                                "id": f"{service_name}_mounts_{volume_name}",
                                "source": service_name,
                                "target": volume_name,
                                "type": self.edge_types["volume_mount"],
                                "label": "mounts",
                                "data": {
                                    "mount_path": parts[1] if len(parts) > 1 else "",
                                    "read_only": len(parts) > 2 and "ro" in parts[2],
                                    "mount_type": "bind" if volume_name.startswith('/') or volume_name.startswith('./') else "volume"
                                }
                            }
                            edges.append(edge)
        
        return nodes, edges
    
    async def _generate_network_dependencies(
        self, 
        networks: Dict, 
        services: Dict
    ) -> Tuple[List[Dict], List[Dict]]:
        """Generate network nodes and connection edges"""
        
        nodes = []
        edges = []
        
        # Create network nodes
        for network_name, network_config in networks.items():
            node = {
                "id": f"network_{network_name}",
                "type": self.node_types["network"],
                "label": f"Network: {network_name}",
                "description": f"Network: {network_name}",
                "position": self._calculate_network_position(network_name, len(networks)),
                "data": {
                    "driver": network_config.get("driver", "bridge"),
                    "external": network_config.get("external", False),
                    "driver_opts": network_config.get("driver_opts", {}),
                    "labels": network_config.get("labels", {}),
                    "ipam": network_config.get("ipam", {})
                }
            }
            nodes.append(node)
        
        # Create network connection edges
        for service_name, service_config in services.items():
            if "networks" in service_config:
                network_connections = service_config["networks"]
                
                if isinstance(network_connections, list):
                    for network_name in network_connections:
                        edge = {
                            "id": f"{service_name}_connects_{network_name}",
                            "source": service_name,
                            "target": f"network_{network_name}",
                            "type": self.edge_types["network_connection"],
                            "label": "connects to",
                            "data": {
                                "connection_type": "network"
                            }
                        }
                        edges.append(edge)
                
                elif isinstance(network_connections, dict):
                    for network_name, network_config in network_connections.items():
                        edge = {
                            "id": f"{service_name}_connects_{network_name}",
                            "source": service_name,
                            "target": f"network_{network_name}",
                            "type": self.edge_types["network_connection"],
                            "label": "connects to",
                            "data": {
                                "connection_type": "network",
                                "aliases": network_config.get("aliases", []),
                                "ipv4_address": network_config.get("ipv4_address", ""),
                                "ipv6_address": network_config.get("ipv6_address", "")
                            }
                        }
                        edges.append(edge)
        
        return nodes, edges
    
    async def _generate_env_dependencies(
        self, 
        env_content: str, 
        existing_nodes: List[Dict]
    ) -> Tuple[List[Dict], List[Dict]]:
        """Generate external dependency nodes from environment variables"""
        
        nodes = []
        edges = []
        
        # Parse environment variables
        env_vars = {}
        lines = env_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
        
        # Identify external service dependencies
        external_services = self._identify_external_services(env_vars)
        
        for ext_service in external_services:
            node_id = f"external_{ext_service['name'].lower().replace(' ', '_')}"
            
            # Check if node already exists
            if not any(node["id"] == node_id for node in existing_nodes + nodes):
                node = {
                    "id": node_id,
                    "type": self.node_types["external"],
                    "label": ext_service["name"],
                    "description": f"External service: {ext_service['name']}",
                    "position": self._calculate_external_position(ext_service["name"]),
                    "data": {
                        "service_type": ext_service["type"],
                        "connection_info": ext_service.get("connection_info", {}),
                        "protocol": ext_service.get("protocol", "unknown")
                    }
                }
                nodes.append(node)
            
            # Create edges to services that use this external service
            for env_var in ext_service["env_vars"]:
                for existing_node in existing_nodes:
                    if existing_node["type"] in ["service", "database", "cache", "api", "web"]:
                        # Check if this service has the environment variable
                        service_env = existing_node["data"].get("environment", {})
                        if env_var in service_env or any(env_var in str(v) for v in service_env.values()):
                            edge = {
                                "id": f"{existing_node['id']}_uses_{node_id}",
                                "source": existing_node["id"],
                                "target": node_id,
                                "type": self.edge_types["environment_link"],
                                "label": f"uses ({env_var})",
                                "data": {
                                    "env_var": env_var,
                                    "connection_type": "external_dependency"
                                }
                            }
                            edges.append(edge)
        
        return nodes, edges
    
    def _determine_service_type(self, service_name: str, service_config: Dict) -> str:
        """Determine the type of service based on name and configuration"""
        
        name_lower = service_name.lower()
        image = service_config.get("image", "").lower()
        
        # Check for common service patterns
        if any(db in name_lower or db in image for db in ["db", "database", "postgres", "mysql", "mongodb"]):
            return self.node_types["database"]
        elif any(cache in name_lower or cache in image for cache in ["cache", "redis", "memcached"]):
            return self.node_types["cache"]
        elif any(api in name_lower or api in image for api in ["api", "backend", "server"]):
            return self.node_types["api"]
        elif any(web in name_lower or web in image for web in ["web", "frontend", "nginx", "apache"]):
            return self.node_types["web"]
        else:
            return self.node_types["service"]
    
    def _generate_service_description(self, service_name: str, service_config: Dict) -> str:
        """Generate description for service node"""
        
        description_parts = []
        
        if "image" in service_config:
            description_parts.append(f"Image: {service_config['image']}")
        
        if "build" in service_config:
            description_parts.append("Built from source")
        
        if "ports" in service_config and service_config["ports"]:
            ports = [str(p) for p in service_config["ports"]]
            description_parts.append(f"Ports: {', '.join(ports)}")
        
        if "depends_on" in service_config and service_config["depends_on"]:
            deps = service_config["depends_on"]
            if isinstance(deps, list):
                description_parts.append(f"Depends on: {', '.join(deps)}")
        
        return "; ".join(description_parts) if description_parts else f"Service: {service_name}"
    
    def _calculate_node_position(self, service_name: str, total_services: int) -> Dict[str, float]:
        """Calculate position for service node in graph layout"""
        
        # Use a simple circular layout for services
        import math
        
        index = hash(service_name) % total_services
        angle = (2 * math.pi * index) / total_services
        radius = 200
        
        return {
            "x": radius * math.cos(angle),
            "y": radius * math.sin(angle)
        }
    
    def _calculate_volume_position(self, volume_name: str, total_volumes: int) -> Dict[str, float]:
        """Calculate position for volume node"""
        
        # Position volumes on the left side
        index = hash(volume_name) % total_volumes
        y_spacing = 100
        
        return {
            "x": -300,
            "y": (index - total_volumes / 2) * y_spacing
        }
    
    def _calculate_network_position(self, network_name: str, total_networks: int) -> Dict[str, float]:
        """Calculate position for network node"""
        
        # Position networks on the right side
        index = hash(network_name) % total_networks
        y_spacing = 100
        
        return {
            "x": 300,
            "y": (index - total_networks / 2) * y_spacing
        }
    
    def _calculate_external_position(self, service_name: str) -> Dict[str, float]:
        """Calculate position for external service node"""
        
        # Position external services at the bottom
        index = hash(service_name) % 10
        x_spacing = 150
        
        return {
            "x": (index - 5) * x_spacing,
            "y": 300
        }
    
    def _identify_external_services(self, env_vars: Dict[str, str]) -> List[Dict[str, Any]]:
        """Identify external services from environment variables"""
        
        external_services = []
        
        # Common patterns for external services
        patterns = {
            "database": [
                r".*[Dd]atabase.*[Uu]rl",
                r".*[Dd][Bb].*[Hh]ost",
                r".*[Mm]ongo.*[Uu]ri",
                r".*[Pp]ostgres.*[Uu]rl",
                r".*[Mm]ysql.*[Hh]ost"
            ],
            "redis": [
                r".*[Rr]edis.*[Uu]rl",
                r".*[Rr]edis.*[Hh]ost"
            ],
            "message_queue": [
                r".*[Rr]abbit.*[Uu]rl",
                r".*[Kk]afka.*[Bb]ootstrap",
                r".*[Qq]ueue.*[Uu]rl"
            ],
            "email": [
                r".*[Ss][Mm][Tt][Pp].*[Hh]ost",
                r".*[Ee]mail.*[Uu]rl"
            ],
            "storage": [
                r".*[Ss]3.*[Uu]rl",
                r".*[Bb]ucket.*[Uu]rl",
                r".*[Ss]torage.*[Uu]rl"
            ],
            "api": [
                r".*[Aa][Pp][Ii].*[Uu]rl",
                r".*[Ee]xternal.*[Aa][Pp][Ii]"
            ]
        }
        
        for service_type, regex_patterns in patterns.items():
            for pattern in regex_patterns:
                for env_var, env_value in env_vars.items():
                    if re.match(pattern, env_var):
                        # Extract service name from env_var or env_value
                        service_name = self._extract_service_name(env_var, env_value, service_type)
                        
                        external_services.append({
                            "name": service_name,
                            "type": service_type,
                            "env_vars": [env_var],
                            "connection_info": {env_var: env_value},
                            "protocol": self._guess_protocol(env_value)
                        })
        
        return external_services
    
    def _extract_service_name(self, env_var: str, env_value: str, service_type: str) -> str:
        """Extract service name from environment variable"""
        
        # Try to extract from environment variable name
        parts = env_var.lower().split('_')
        
        # Look for meaningful parts
        meaningful_parts = []
        for part in parts:
            if part not in ['url', 'host', 'uri', 'connection', 'db', 'api']:
                meaningful_parts.append(part.capitalize())
        
        if meaningful_parts:
            return ' '.join(meaningful_parts)
        
        # Fallback to service type
        return service_type.capitalize()
    
    def _guess_protocol(self, connection_string: str) -> str:
        """Guess protocol from connection string"""
        
        connection_string_lower = connection_string.lower()
        
        if connection_string_lower.startswith('http://'):
            return 'http'
        elif connection_string_lower.startswith('https://'):
            return 'https'
        elif connection_string_lower.startswith('mongodb://'):
            return 'mongodb'
        elif connection_string_lower.startswith('postgres://'):
            return 'postgresql'
        elif connection_string_lower.startswith('mysql://'):
            return 'mysql'
        elif connection_string_lower.startswith('redis://'):
            return 'redis'
        elif connection_string_lower.startswith('amqp://'):
            return 'amqp'
        else:
            return 'unknown'
    
    def _calculate_graph_metrics(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
        """Calculate graph metrics"""
        
        service_nodes = [n for n in nodes if n["type"] in ["service", "database", "cache", "api", "web"]]
        total_dependencies = len([e for e in edges if e["type"] == "depends_on"])
        
        # Calculate average dependencies per service
        avg_deps = total_dependencies / len(service_nodes) if service_nodes else 0
        
        # Find most connected service
        connection_counts = {}
        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            
            connection_counts[source] = connection_counts.get(source, 0) + 1
            connection_counts[target] = connection_counts.get(target, 0) + 1
        
        most_connected = max(connection_counts.items(), key=lambda x: x[1]) if connection_counts else None
        
        return {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "service_count": len(service_nodes),
            "average_dependencies": round(avg_deps, 2),
            "most_connected_service": most_connected[0] if most_connected else None,
            "max_connections": most_connected[1] if most_connected else 0,
            "graph_density": round(len(edges) / (len(nodes) * (len(nodes) - 1) / 2), 3) if len(nodes) > 1 else 0
        }
    
    def _identify_critical_paths(self, nodes: List[Dict], edges: List[Dict]) -> List[List[str]]:
        """Identify critical paths in the dependency graph"""
        
        # Build adjacency list
        graph = {}
        for node in nodes:
            graph[node["id"]] = []
        
        for edge in edges:
            if edge["type"] == "depends_on":
                graph[edge["source"]].append(edge["target"])
        
        # Find all paths from leaf nodes (no outgoing dependencies) to root nodes
        critical_paths = []
        
        # Find leaf nodes (services that others depend on)
        all_nodes = set(graph.keys())
        target_nodes = set()
        for edge in edges:
            if edge["type"] == "depends_on":
                target_nodes.add(edge["target"])
        
        leaf_nodes = target_nodes - set(edge["source"] for edge in edges if edge["type"] == "depends_on")
        
        # For each leaf node, find all paths to services that depend on it
        for leaf in leaf_nodes:
            paths = self._find_paths_to_node(graph, leaf)
            for path in paths:
                if len(path) > 1:  # Only include paths with multiple nodes
                    critical_paths.append(path)
        
        return critical_paths[:10]  # Return top 10 critical paths
    
    def _find_paths_to_node(self, graph: Dict, target: str) -> List[List[str]]:
        """Find all paths that lead to the target node"""
        
        paths = []
        
        def dfs(current: str, path: List[str], visited: set):
            if current == target:
                paths.append(path.copy())
                return
            
            if current in visited:
                return
            
            visited.add(current)
            
            for neighbor in graph.get(current, []):
                path.append(neighbor)
                dfs(neighbor, path, visited)
                path.pop()
            
            visited.remove(current)
        
        for start_node in graph.keys():
            if start_node != target:
                dfs(start_node, [start_node], set())
        
        return paths
    
    def _detect_circular_dependencies(self, nodes: List[Dict], edges: List[Dict]) -> List[List[str]]:
        """Detect circular dependencies in the graph"""
        
        # Build adjacency list for dependency edges
        graph = {}
        for node in nodes:
            graph[node["id"]] = []
        
        for edge in edges:
            if edge["type"] == "depends_on":
                graph[edge["source"]].append(edge["target"])
        
        # Detect cycles using DFS
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                path.append(neighbor)
                dfs(neighbor, path)
                path.pop()
            
            rec_stack.remove(node)
        
        for node in graph.keys():
            if node not in visited:
                dfs(node, [node])
        
        return cycles
    
    def _suggest_layout(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
        """Suggest optimal layout for the graph"""
        
        node_count = len(nodes)
        edge_count = len(edges)
        
        # Determine layout based on graph complexity
        if node_count <= 10:
            layout_type = "force_directed"
            description = "Force-directed layout for small graphs"
        elif node_count <= 25:
            layout_type = "hierarchical"
            description = "Hierarchical layout for medium graphs"
        else:
            layout_type = "circular"
            description = "Circular layout for large graphs"
        
        # Calculate optimal spacing
        spacing = max(100, min(200, 1000 / max(node_count, 1)))
        
        return {
            "type": layout_type,
            "description": description,
            "node_spacing": spacing,
            "edge_length": spacing * 1.5,
            "iterations": 100 if layout_type == "force_directed" else 0,
            "clustering_enabled": node_count > 15
        }
