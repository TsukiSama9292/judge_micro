"""
Environment variables and configuration settings for this application
These variables can be defined in .env.local or .env files

Parameter descriptions:
- container_cpu: CPU limit per container, default is 0.5, this feature limits based on CPU runtime, a relatively fine-grained method
- container_mem: Memory limit per container, default is 128m
- container_timeout: Default execution timeout in seconds, default is 30
- continue_on_timeout: Whether to continue execution after timeout, default is False
- docker_ssh_remote: Default is False, whether to use remote Docker SSH connection
- docker_client: Determines whether to use local Docker client or remote SSH connection based on docker_ssh_remote value
- If docker_ssh_remote is True, the following configurations are required:
  - host: Remote Docker host IP
  - port: SSH port, default is 22
  - key_path: SSH private key path, default is ~/.ssh/id_rsa
  - username: SSH username, default is root
  - password: SSH password, default is empty string
"""

import os
from dotenv import load_dotenv
from pydantic.v1 import BaseSettings
import docker

# Load environment variables: .env.local first, then .env (which overrides .env.local)
load_dotenv(".env.local", override=False)
load_dotenv(".env", override=True)

class Settings(BaseSettings):
    """
    Settings for the application, loaded from environment variables or a .env file.
    """
    container_cpu: float = float(os.getenv("CONTAINER_CPU", 0.5))
    container_mem: str = os.getenv("CONTAINER_MEM", "128m")
    
    compile_timeout: int = int(os.getenv("COMPILE_TIMEOUT", 10))
    container_timeout: int = int(os.getenv("CONTAINER_TIMEOUT", 10))
    continue_on_timeout: bool = os.getenv("CONTINUE_ON_TIMEOUT", "false").lower() in ("true", "1", "yes")
    
    docker_ssh_remote: bool = os.getenv("DOCKER_SSH_REMOTE", "false").lower() in ("true", "1", "yes")

    DOCKER_SSH_HOST: str = os.getenv("DOCKER_SSH_HOST", "127.0.0.1")
    DOCKER_SSH_PORT: int = int(os.getenv("DOCKER_SSH_PORT", 22))
    DOCKER_SSH_KEY_PATH: str = os.getenv("DOCKER_SSH_KEY_PATH", "~/.ssh/id_rsa")
    DOCKER_SSH_USER: str = os.getenv("DOCKER_SSH_USER", "root")
    DOCKER_SSH_PASSWORD: str = os.getenv("DOCKER_SSH_PASSWORD", "password")

# Initialize settings
setting = Settings()