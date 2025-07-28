"""
設定該應用的環境變量和配置
這些變量可以在 .env.local 或 .env 文件中定義

參數介紹：
- container_cpu: 每個容器的 CPU 限制，默認為 0.5，這個功能是照 CPU 運行時間去限制的，算是比較細膩的方法
- container_mem: 每個容器的內存限制，默認為 128m
- docker_ssh_remote: 預設為 False，是否使用遠端 Docker SSH 連接
- docker_client: 根據 docker_ssh_remote 的值來決定使用本地 Docker 客戶端還是遠端 SSH 連接
- 如果 docker_ssh_remote 為 True，則需要提供以下配置：
  - host: 遠端 Docker 主機的 IP
  - port: SSH 端口，默認為 22
  - key_path: SSH 私鑰路徑，默認為 ~/.ssh/id_rsa
  - username: SSH 用戶名，默認為 root
  - password: SSH 密碼，默認為空字符串
"""

import os
from dotenv import load_dotenv
from pydantic.v1 import BaseSettings
import docker

# 加載環境變量: .env.local 和 .env(優先)
load_dotenv(".env.local", override=False)
load_dotenv(".env", override=True)

class Settings(BaseSettings):
    """
    Settings for the application, loaded from environment variables or a .env file.
    """
    container_cpu: float = float(os.getenv("CONTAINER_CPU", 0.5))
    container_mem: str = os.getenv("CONTAINER_MEM", "128m")
    
    docker_ssh_remote: bool = os.getenv("DOCKER_SSH_REMOTE", "false").lower() in ("true", "1", "yes")

    DOCKER_SSH_HOST: str = os.getenv("DOCKER_SSH_HOST", "127.0.0.1")
    DOCKER_SSH_PORT: int = int(os.getenv("DOCKER_SSH_PORT", 22))
    DOCKER_SSH_KEY_PATH: str = os.getenv("DOCKER_SSH_KEY_PATH", "~/.ssh/id_rsa")
    DOCKER_SSH_USER: str = os.getenv("DOCKER_SSH_USER", "root")
    DOCKER_SSH_PASSWORD: str = os.getenv("DOCKER_SSH_PASSWORD", "password")

# 初始化設定
setting = Settings()