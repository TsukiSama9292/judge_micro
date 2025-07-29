import docker
import paramiko
import os
from typing import Dict, Any, Optional

class RemoteDockerManager:
    """Remote Docker Manager - Manage remote Docker through SSH connection"""
    
    def __init__(self, host: str, username: str, key_path: Optional[str] = None, 
                 password: Optional[str] = None, port: int = 22):
        """
        Initialize remote Docker connection
        
        Args:
            host: Remote host IP or domain name
            username: SSH username
            key_path: SSH private key path (preferred)
            password: SSH password (used when no private key)
            port: SSH port, default 22
        """
        self.host = host
        self.username = username
        self.port = port
        self.ssh_client = None
        self.docker_client = None
        
        # Establish SSH connection
        self._connect_ssh(key_path, password)
        
        # Establish Docker connection
        self._connect_docker()
    
    def _connect_ssh(self, key_path: Optional[str], password: Optional[str]):
        """Establish SSH connection"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if key_path and os.path.exists(key_path):
                # Connect using private key
                print(f"🔑 Connecting using private key to {self.username}@{self.host}:{self.port}")
                self.ssh_client.connect(
                    hostname=self.host,
                    username=self.username,
                    key_filename=key_path,
                    port=self.port,
                    timeout=10
                )
            elif password:
                # Connect using password
                print(f"🔒 Connecting using password to {self.username}@{self.host}:{self.port}")
                self.ssh_client.connect(
                    hostname=self.host,
                    username=self.username,
                    password=password,
                    port=self.port,
                    timeout=10
                )
            else:
                # Try using default private key
                default_key = os.path.expanduser("~/.ssh/id_rsa")
                if os.path.exists(default_key):
                    print(f"🔑 Connecting using default private key to {self.username}@{self.host}:{self.port}")
                    self.ssh_client.connect(
                        hostname=self.host,
                        username=self.username,
                        key_filename=default_key,
                        port=self.port,
                        timeout=10
                    )
                else:
                    raise ValueError("Private key path or password is required")
            
            print("✅ SSH connection successful")
            
        except Exception as e:
            print(f"❌ SSH connection failed: {e}")
            raise
    
    def _connect_docker(self):
        """Establish remote Docker connection"""
        try:
            # Check if remote has Docker
            stdin, stdout, stderr = self.ssh_client.exec_command("docker --version")
            exit_code = stdout.channel.recv_exit_status()
            
            if exit_code != 0:
                error = stderr.read().decode().strip()
                raise Exception(f"Remote system doesn't have Docker installed or Docker service is not running: {error}")
            
            docker_version = stdout.read().decode().strip()
            print(f"🐳 Remote Docker version: {docker_version}")
            
            # Try multiple connection methods
            connection_methods = [
                # Method 1: SSH tunnel connection (recommended)
                f"ssh://{self.username}@{self.host}:{self.port}",
                # Method 2: If localhost, try direct connection
                "unix://var/run/docker.sock" if self.host in ['127.0.0.1', 'localhost'] else None,
                # Method 3: TCP connection (if Docker daemon exposed port)
                f"tcp://{self.host}:2376" if self.host not in ['127.0.0.1', 'localhost'] else None,
                f"tcp://{self.host}:2375" if self.host not in ['127.0.0.1', 'localhost'] else None,
            ]
            
            # Filter out None values
            connection_methods = [method for method in connection_methods if method is not None]
            
            last_error = None
            for method in connection_methods:
                try:
                    print(f"🔄 Trying connection method: {method}")
                    
                    # Create Docker client
                    if method.startswith("ssh://"):
                        # SSH connection needs special handling
                        self.docker_client = docker.DockerClient(base_url=method)
                    else:
                        self.docker_client = docker.DockerClient(base_url=method)
                    
                    # Test connection
                    info = self.docker_client.info()
                    print(f"✅ Remote Docker connection successful (using: {method})")
                    print(f"   System: {info.get('OperatingSystem', 'Unknown')}")
                    print(f"   Architecture: {info.get('Architecture', 'Unknown')}")
                    print(f"   Containers: {info.get('Containers', 0)}")
                    print(f"   Images: {info.get('Images', 0)}")
                    return  # Successfully connected, exit method
                    
                except Exception as e:
                    last_error = e
                    print(f"   ❌ Connection failed: {e}")
                    if self.docker_client:
                        try:
                            self.docker_client.close()
                        except:
                            pass
                        self.docker_client = None
                    continue
            
            # All methods failed
            raise Exception(f"All Docker connection methods failed. Last error: {last_error}")
            
        except Exception as e:
            print(f"❌ Remote Docker connection failed: {e}")
            print("💡 Ensure Docker is installed on remote system and current user has access permissions")
            print("💡 For remote connection, may need to configure Docker daemon TCP port")
            raise
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute shell command on remote host"""
        try:
            print(f"🔄 Executing remote command: {command}")
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            
            exit_code = stdout.channel.recv_exit_status()
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            result = {
                "command": command,
                "exit_code": exit_code,
                "output": output,
                "error": error,
                "success": exit_code == 0
            }
            
            if exit_code == 0:
                print(f"✅ Command executed successfully")
                if output:
                    print(f"Output: {output}")
            else:
                print(f"❌ Command execution failed (exit code: {exit_code})")
                if error:
                    print(f"Error: {error}")
            
            return result
            
        except Exception as e:
            print(f"❌ Command execution exception: {e}")
            return {
                "command": command,
                "exit_code": -1,
                "output": "",
                "error": str(e),
                "success": False
            }
    
    def list_containers(self, all_containers: bool = False) -> list:
        """List remote containers"""
        print(f"📦 Remote containers list ({'all' if all_containers else 'running'}):")
        
        # Use SSH command directly to get container info (more reliable)
        try:
            # Use docker ps command, -a means show all containers (including stopped ones)
            if all_containers:
                cmd = "docker ps -a --format 'table {{.Names}}\\t{{.ID}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}'"
            else:
                cmd = "docker ps --format 'table {{.Names}}\\t{{.ID}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}'"
            
            result = self.execute_command(cmd)
            if not result["success"]:
                print(f"❌ Failed to get container list: {result['error']}")
                return []
            
            lines = result["output"].split('\n')
            if len(lines) <= 1:
                print("   (No containers)")
                return []
            
            # Parse container information
            container_info = []
            for line in lines[1:]:  # Skip header line
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 4:
                        name = parts[0].strip()
                        container_id = parts[1].strip()
                        image = parts[2].strip()
                        status = parts[3].strip()
                        ports = parts[4].strip() if len(parts) > 4 else ""
                        
                        # Add status icon
                        status_lower = status.lower()
                        if 'up' in status_lower and 'minute' in status_lower:
                            status_icon = '🟢'  # Running
                        elif 'up' in status_lower:
                            status_icon = '🟢'  # Running
                        elif 'exited (0)' in status_lower:
                            status_icon = '⚫'  # Normal exit
                        elif 'exited' in status_lower:
                            status_icon = '🔴'  # Abnormal exit
                        elif 'stopped' in status_lower:
                            status_icon = '🔴'  # Stopped
                        elif 'paused' in status_lower:
                            status_icon = '🟡'  # Paused
                        elif 'created' in status_lower:
                            status_icon = '🔵'  # Created
                        elif 'restarting' in status_lower:
                            status_icon = '🔄'  # Restarting
                        elif 'removing' in status_lower:
                            status_icon = '🗑️'  # Removing
                        elif 'dead' in status_lower:
                            status_icon = '💀'  # Dead
                        else:
                            status_icon = '❓'  # Unknown status
                        
                        info = {
                            "id": container_id,
                            "name": name,
                            "image": image,
                            "status": status,
                            "ports": ports
                        }
                        container_info.append(info)
                        
                        # Formatted display
                        print(f"   {status_icon} {name} ({container_id[:12]}) - {image}")
                        print(f"      Status: {status}")
                        if ports:
                            print(f"      Ports: {ports}")
            
            return container_info
            
        except Exception as e:
            print(f"❌ Failed to get container list: {e}")
            
            # Last fallback method: try using Docker Python API
            try:
                print("💡 Trying Docker Python API...")
                
                # Call directly without passing parameters
                if all_containers:
                    # Try different ways to get all containers
                    containers = self.docker_client.containers.list()
                    all_containers_list = []
                    try:
                        # Try to get stopped containers
                        stopped_containers = self.docker_client.api.containers(all=True)
                        containers = [self.docker_client.containers.get(c['Id']) for c in stopped_containers]
                    except:
                        pass
                else:
                    containers = self.docker_client.containers.list()
                
                if not containers:
                    print("   (No containers)")
                    return []
                
                container_info = []
                for container in containers:
                    try:
                        info = {
                            "id": getattr(container, 'short_id', 'unknown'),
                            "name": getattr(container, 'name', 'unknown'),
                            "image": str(container.image.tags[0]) if hasattr(container, 'image') and container.image.tags else 'unknown',
                            "status": getattr(container, 'status', 'unknown'),
                            "ports": getattr(container, 'ports', {})
                        }
                        container_info.append(info)
                        print(f"   📦 {info['name']} ({info['id']}) - {info['image']} - {info['status']}")
                    except Exception as container_error:
                        print(f"   • Failed to get container info: {container_error}")
                
                return container_info
                
            except Exception as api_error:
                print(f"   Docker API fallback method also failed: {api_error}")
                return []
    
    def list_images(self) -> list:
        """List remote images"""
        try:
            images = self.docker_client.images.list()
            print(f"🖼️  Remote images list:")
            
            if not images:
                print("   (No images)")
                return []
            
            image_info = []
            for image in images:
                try:
                    tags = image.tags if hasattr(image, 'tags') and image.tags else ["<none>:<none>"]
                    
                    # Safely get size
                    size_mb = 0
                    if hasattr(image, 'attrs') and 'Size' in image.attrs:
                        size_mb = image.attrs['Size'] / 1024 / 1024
                    
                    info = {
                        "id": image.short_id,
                        "tags": tags,
                        "size": f"{size_mb:.1f} MB"
                    }
                    image_info.append(info)
                    
                    print(f"   • {tags[0]} ({info['id']}) - {info['size']}")
                except Exception as image_error:
                    print(f"   • Failed to get image info: {image_error}")
                    continue
            
            return image_info
            
        except Exception as e:
            print(f"❌ Failed to get images list: {e}")
            print(f"   Detailed error: {type(e).__name__}: {str(e)}")
            return []
    
    def run_container(self, image: str, command: str = None, **kwargs) -> Optional[str]:
        """Run container on remote host"""
        try:
            print(f"🚀 Running container on remote host: {image}")
            
            # Set default parameters
            run_kwargs = {
                "detach": True,
                "remove": False,
                **kwargs
            }
            
            if command:
                run_kwargs["command"] = command
            
            container = self.docker_client.containers.run(image, **run_kwargs)
            
            print(f"✅ Container started successfully: {container.name} ({container.short_id})")
            return container.id
            
        except Exception as e:
            print(f"❌ Container startup failed: {e}")
            return None
    
    def stop_container(self, container_id_or_name: str) -> bool:
        """Stop remote container"""
        try:
            container = self.docker_client.containers.get(container_id_or_name)
            container.stop()
            print(f"🛑 Container stopped: {container.name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to stop container: {e}")
            return False
    
    def remove_container(self, container_id_or_name: str, force: bool = False) -> bool:
        """Remove remote container"""
        try:
            container = self.docker_client.containers.get(container_id_or_name)
            container.remove(force=force)
            print(f"🗑️  Container removed: {container.name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to remove container: {e}")
            return False
    
    def pull_image(self, image: str) -> bool:
        """Pull remote image"""
        try:
            print(f"📥 Pulling image: {image}")
            image_obj = self.docker_client.images.pull(image)
            print(f"✅ Image pulled successfully: {image}")
            return True
            
        except Exception as e:
            print(f"❌ Image pull failed: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get remote system information"""
        try:
            # Docker information
            docker_info = self.docker_client.info()
            
            # System information
            system_info = {}
            
            # CPU information
            result = self.execute_command("nproc")
            if result["success"]:
                system_info["cpu_cores"] = int(result["output"])
            
            # Memory information
            result = self.execute_command("free -h")
            if result["success"]:
                system_info["memory_info"] = result["output"]
            
            # Disk information
            result = self.execute_command("df -h /")
            if result["success"]:
                system_info["disk_info"] = result["output"]
            
            # System load
            result = self.execute_command("uptime")
            if result["success"]:
                system_info["uptime"] = result["output"]
            
            return {
                "docker": docker_info,
                "system": system_info
            }
            
        except Exception as e:
            print(f"❌ Failed to get system information: {e}")
            return {}
    
    def close(self):
        """Close connections"""
        if self.docker_client:
            self.docker_client.close()
            print("🔒 Docker connection closed")
        
        if self.ssh_client:
            self.ssh_client.close()
            print("🔒 SSH connection closed")