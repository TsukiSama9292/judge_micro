"""
Docker SSH 遠端連接示例
======================

這個示例展示如何使用 Python 的 Docker 套件通過 SSH 連接到遠端的 Linux 系統，
並在遠端機器上管理 Docker 容器。

安裝需求：
```bash
pip install docker paramiko
```

或使用項目依賴：
```bash
pip install -e .  # 已包含 docker 和 paramiko
```
"""

import docker
import paramiko
import os
import sys
from typing import Dict, Any, Optional
import json


class RemoteDockerManager:
    """遠端 Docker 管理器 - 通過 SSH 連接管理遠端 Docker"""
    
    def __init__(self, host: str, username: str, key_path: Optional[str] = None, 
                 password: Optional[str] = None, port: int = 22):
        """
        初始化遠端 Docker 連接
        
        Args:
            host: 遠端主機 IP 或域名
            username: SSH 用戶名
            key_path: SSH 私鑰路徑（優先使用）
            password: SSH 密碼（當沒有私鑰時使用）
            port: SSH 端口，默認 22
        """
        self.host = host
        self.username = username
        self.port = port
        self.ssh_client = None
        self.docker_client = None
        
        # 建立 SSH 連接
        self._connect_ssh(key_path, password)
        
        # 建立 Docker 連接
        self._connect_docker()
    
    def _connect_ssh(self, key_path: Optional[str], password: Optional[str]):
        """建立 SSH 連接"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if key_path and os.path.exists(key_path):
                # 使用私鑰連接
                print(f"🔑 使用私鑰連接到 {self.username}@{self.host}:{self.port}")
                self.ssh_client.connect(
                    hostname=self.host,
                    username=self.username,
                    key_filename=key_path,
                    port=self.port,
                    timeout=10
                )
            elif password:
                # 使用密碼連接
                print(f"🔒 使用密碼連接到 {self.username}@{self.host}:{self.port}")
                self.ssh_client.connect(
                    hostname=self.host,
                    username=self.username,
                    password=password,
                    port=self.port,
                    timeout=10
                )
            else:
                # 嘗試使用默認私鑰
                default_key = os.path.expanduser("~/.ssh/id_rsa")
                if os.path.exists(default_key):
                    print(f"🔑 使用默認私鑰連接到 {self.username}@{self.host}:{self.port}")
                    self.ssh_client.connect(
                        hostname=self.host,
                        username=self.username,
                        key_filename=default_key,
                        port=self.port,
                        timeout=10
                    )
                else:
                    raise ValueError("需要提供私鑰路徑或密碼")
            
            print("✅ SSH 連接成功")
            
        except Exception as e:
            print(f"❌ SSH 連接失敗: {e}")
            raise
    
    def _connect_docker(self):
        """建立遠端 Docker 連接"""
        try:
            # 檢查遠端是否有 Docker
            stdin, stdout, stderr = self.ssh_client.exec_command("docker --version")
            exit_code = stdout.channel.recv_exit_status()
            
            if exit_code != 0:
                error = stderr.read().decode().strip()
                raise Exception(f"遠端系統沒有安裝 Docker 或 Docker 服務未啟動: {error}")
            
            docker_version = stdout.read().decode().strip()
            print(f"🐳 遠端 Docker 版本: {docker_version}")
            
            # 嘗試多種連接方式
            connection_methods = [
                # 方法1：SSH 隧道連接（推薦）
                f"ssh://{self.username}@{self.host}:{self.port}",
                # 方法2：如果是本地回環，嘗試直接連接
                "unix://var/run/docker.sock" if self.host in ['127.0.0.1', 'localhost'] else None,
                # 方法3：TCP 連接（如果 Docker daemon 暴露了端口）
                f"tcp://{self.host}:2376" if self.host not in ['127.0.0.1', 'localhost'] else None,
                f"tcp://{self.host}:2375" if self.host not in ['127.0.0.1', 'localhost'] else None,
            ]
            
            # 過濾掉 None 值
            connection_methods = [method for method in connection_methods if method is not None]
            
            last_error = None
            for method in connection_methods:
                try:
                    print(f"🔄 嘗試連接方式: {method}")
                    
                    # 創建 Docker 客戶端
                    if method.startswith("ssh://"):
                        # SSH 連接需要特殊處理
                        self.docker_client = docker.DockerClient(base_url=method)
                    else:
                        self.docker_client = docker.DockerClient(base_url=method)
                    
                    # 測試連接
                    info = self.docker_client.info()
                    print(f"✅ 遠端 Docker 連接成功 (使用: {method})")
                    print(f"   系統: {info.get('OperatingSystem', 'Unknown')}")
                    print(f"   架構: {info.get('Architecture', 'Unknown')}")
                    print(f"   容器數: {info.get('Containers', 0)}")
                    print(f"   映像數: {info.get('Images', 0)}")
                    return  # 成功連接，退出方法
                    
                except Exception as e:
                    last_error = e
                    print(f"   ❌ 連接失敗: {e}")
                    if self.docker_client:
                        try:
                            self.docker_client.close()
                        except:
                            pass
                        self.docker_client = None
                    continue
            
            # 所有方法都失敗了
            raise Exception(f"所有 Docker 連接方法都失敗了。最後錯誤: {last_error}")
            
        except Exception as e:
            print(f"❌ 遠端 Docker 連接失敗: {e}")
            print("💡 確保遠端系統已安裝 Docker 且當前用戶有權限訪問")
            print("💡 如果是遠端連接，可能需要配置 Docker daemon 的 TCP 端口")
            raise
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """在遠端執行 Shell 命令"""
        try:
            print(f"🔄 執行遠端命令: {command}")
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
                print(f"✅ 命令執行成功")
                if output:
                    print(f"輸出: {output}")
            else:
                print(f"❌ 命令執行失敗 (退出碼: {exit_code})")
                if error:
                    print(f"錯誤: {error}")
            
            return result
            
        except Exception as e:
            print(f"❌ 命令執行異常: {e}")
            return {
                "command": command,
                "exit_code": -1,
                "output": "",
                "error": str(e),
                "success": False
            }
    
    def list_containers(self, all_containers: bool = False) -> list:
        """列出遠端容器"""
        print(f"📦 遠端容器列表 ({'全部' if all_containers else '運行中'}):")
        
        # 直接使用 SSH 命令獲取容器信息（更可靠）
        try:
            # 使用 docker ps 命令，-a 表示顯示所有容器（包括停止的）
            if all_containers:
                cmd = "docker ps -a --format 'table {{.Names}}\\t{{.ID}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}'"
            else:
                cmd = "docker ps --format 'table {{.Names}}\\t{{.ID}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}'"
            
            result = self.execute_command(cmd)
            if not result["success"]:
                print(f"❌ 獲取容器列表失敗: {result['error']}")
                return []
            
            lines = result["output"].split('\n')
            if len(lines) <= 1:
                print("   (無容器)")
                return []
            
            # 解析容器信息
            container_info = []
            for line in lines[1:]:  # 跳過標題行
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 4:
                        name = parts[0].strip()
                        container_id = parts[1].strip()
                        image = parts[2].strip()
                        status = parts[3].strip()
                        ports = parts[4].strip() if len(parts) > 4 else ""
                        
                        # 添加狀態圖示
                        status_lower = status.lower()
                        if 'up' in status_lower and 'minute' in status_lower:
                            status_icon = '🟢'  # 運行中
                        elif 'up' in status_lower:
                            status_icon = '🟢'  # 運行中
                        elif 'exited (0)' in status_lower:
                            status_icon = '⚫'  # 正常退出
                        elif 'exited' in status_lower:
                            status_icon = '🔴'  # 異常退出
                        elif 'stopped' in status_lower:
                            status_icon = '🔴'  # 停止
                        elif 'paused' in status_lower:
                            status_icon = '🟡'  # 暫停
                        elif 'created' in status_lower:
                            status_icon = '🔵'  # 已創建
                        elif 'restarting' in status_lower:
                            status_icon = '🔄'  # 重啟中
                        elif 'removing' in status_lower:
                            status_icon = '🗑️'  # 刪除中
                        elif 'dead' in status_lower:
                            status_icon = '💀'  # 死亡
                        else:
                            status_icon = '❓'  # 未知狀態
                        
                        info = {
                            "id": container_id,
                            "name": name,
                            "image": image,
                            "status": status,
                            "ports": ports
                        }
                        container_info.append(info)
                        
                        # 格式化顯示
                        print(f"   {status_icon} {name} ({container_id[:12]}) - {image}")
                        print(f"      狀態: {status}")
                        if ports:
                            print(f"      端口: {ports}")
            
            return container_info
            
        except Exception as e:
            print(f"❌ 獲取容器列表失敗: {e}")
            
            # 最後備用方法：嘗試使用 Docker Python API
            try:
                print("💡 嘗試使用 Docker Python API...")
                
                # 不傳遞參數，直接調用
                if all_containers:
                    # 嘗試不同的方式獲取所有容器
                    containers = self.docker_client.containers.list()
                    all_containers_list = []
                    try:
                        # 嘗試獲取已停止的容器
                        stopped_containers = self.docker_client.api.containers(all=True)
                        containers = [self.docker_client.containers.get(c['Id']) for c in stopped_containers]
                    except:
                        pass
                else:
                    containers = self.docker_client.containers.list()
                
                if not containers:
                    print("   (無容器)")
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
                        print(f"   • 容器資訊獲取失敗: {container_error}")
                
                return container_info
                
            except Exception as api_error:
                print(f"   Docker API 備用方法也失敗: {api_error}")
                return []
    
    def list_images(self) -> list:
        """列出遠端映像"""
        try:
            images = self.docker_client.images.list()
            print(f"🖼️  遠端映像列表:")
            
            if not images:
                print("   (無映像)")
                return []
            
            image_info = []
            for image in images:
                try:
                    tags = image.tags if hasattr(image, 'tags') and image.tags else ["<none>:<none>"]
                    
                    # 安全地獲取大小
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
                    print(f"   • 映像資訊獲取失敗: {image_error}")
                    continue
            
            return image_info
            
        except Exception as e:
            print(f"❌ 獲取映像列表失敗: {e}")
            print(f"   詳細錯誤: {type(e).__name__}: {str(e)}")
            return []
    
    def run_container(self, image: str, command: str = None, **kwargs) -> Optional[str]:
        """在遠端運行容器"""
        try:
            print(f"🚀 在遠端運行容器: {image}")
            
            # 設置默認參數
            run_kwargs = {
                "detach": True,
                "remove": False,
                **kwargs
            }
            
            if command:
                run_kwargs["command"] = command
            
            container = self.docker_client.containers.run(image, **run_kwargs)
            
            print(f"✅ 容器啟動成功: {container.name} ({container.short_id})")
            return container.id
            
        except Exception as e:
            print(f"❌ 容器啟動失敗: {e}")
            return None
    
    def stop_container(self, container_id_or_name: str) -> bool:
        """停止遠端容器"""
        try:
            container = self.docker_client.containers.get(container_id_or_name)
            container.stop()
            print(f"🛑 容器已停止: {container.name}")
            return True
            
        except Exception as e:
            print(f"❌ 停止容器失敗: {e}")
            return False
    
    def remove_container(self, container_id_or_name: str, force: bool = False) -> bool:
        """刪除遠端容器"""
        try:
            container = self.docker_client.containers.get(container_id_or_name)
            container.remove(force=force)
            print(f"🗑️  容器已刪除: {container.name}")
            return True
            
        except Exception as e:
            print(f"❌ 刪除容器失敗: {e}")
            return False
    
    def pull_image(self, image: str) -> bool:
        """拉取遠端映像"""
        try:
            print(f"📥 拉取映像: {image}")
            image_obj = self.docker_client.images.pull(image)
            print(f"✅ 映像拉取成功: {image}")
            return True
            
        except Exception as e:
            print(f"❌ 映像拉取失敗: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """獲取遠端系統資訊"""
        try:
            # Docker 資訊
            docker_info = self.docker_client.info()
            
            # 系統資訊
            system_info = {}
            
            # CPU 資訊
            result = self.execute_command("nproc")
            if result["success"]:
                system_info["cpu_cores"] = int(result["output"])
            
            # 記憶體資訊
            result = self.execute_command("free -h")
            if result["success"]:
                system_info["memory_info"] = result["output"]
            
            # 磁碟資訊
            result = self.execute_command("df -h /")
            if result["success"]:
                system_info["disk_info"] = result["output"]
            
            # 系統負載
            result = self.execute_command("uptime")
            if result["success"]:
                system_info["uptime"] = result["output"]
            
            return {
                "docker": docker_info,
                "system": system_info
            }
            
        except Exception as e:
            print(f"❌ 獲取系統資訊失敗: {e}")
            return {}
    
    def close(self):
        """關閉連接"""
        if self.docker_client:
            self.docker_client.close()
            print("🔒 Docker 連接已關閉")
        
        if self.ssh_client:
            self.ssh_client.close()
            print("🔒 SSH 連接已關閉")


def main():
    """主函數 - 演示用法"""
    print("🌐 Docker SSH 遠端連接示例")
    print("=" * 40)
    
    # 配置連接參數
    config = {
        "host": "127.0.0.1",  # 遠端主機 IP
        "username": "tsukisama9292",  # SSH 用戶名
        "key_path": os.path.expanduser("~/.ssh/id_rsa"),  # SSH 私鑰路徑
        # "password": "your_password",  # SSH 密碼（可選）
        "port": 22  # SSH 端口
    }
    
    # 檢查配置
    print("🔧 連接配置:")
    print(f"   主機: {config['host']}")
    print(f"   用戶: {config['username']}")
    print(f"   端口: {config['port']}")
    
    if config.get("key_path") and os.path.exists(config["key_path"]):
        print(f"   私鑰: {config['key_path']}")
    elif config.get("password"):
        print("   認證: 密碼")
    else:
        print("⚠️  未找到私鑰或密碼，將嘗試默認私鑰")
    
    print()
    
    try:
        # 創建遠端 Docker 管理器
        remote_docker = RemoteDockerManager(**config)
        
        print("\n" + "=" * 40)
        print("📊 系統資訊")
        print("=" * 40)
        
        # 獲取系統資訊
        info = remote_docker.get_system_info()
        if info:
            print("系統資源:")
            if "cpu_cores" in info["system"]:
                print(f"   CPU 核心: {info['system']['cpu_cores']}")
            if "uptime" in info["system"]:
                print(f"   系統運行時間: {info['system']['uptime']}")
        
        print("\n" + "=" * 40)
        print("🐳 Docker 管理")
        print("=" * 40)
        
        # 列出現有容器
        remote_docker.list_containers(all_containers=True)
        
        print()
        
        # 列出現有映像
        remote_docker.list_images()
        
        print("\n" + "=" * 40)
        print("🧪 測試容器操作")
        print("=" * 40)
        
        # 拉取測試映像
        test_image = "alpine:latest"
        if remote_docker.pull_image(test_image):
            
            # 運行測試容器
            container_id = remote_docker.run_container(
                image=test_image,
                command="echo 'Hello from remote Docker!'",
                name="ssh_test_container"
            )
            
            if container_id:
                # 等待容器執行完成
                import time
                time.sleep(2)
                
                # 查看容器狀態
                remote_docker.list_containers(all_containers=True)
                
                # 清理測試容器
                remote_docker.remove_container("ssh_test_container", force=True)
        
        print("\n✅ 演示完成")
        
    except Exception as e:
        print(f"❌ 演示失敗: {e}")
        return 1
    
    finally:
        # 關閉連接
        if 'remote_docker' in locals():
            remote_docker.close()
    
    return 0


if __name__ == "__main__":
    exit(main())
