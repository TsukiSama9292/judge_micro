import json
import os
import subprocess
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import docker
from docker.errors import DockerException

class OJMicroserviceFast:
    """高速版本的 OJ 微服務 - 使用容器重用優化"""
    
    # Docker 映像名稱
    DOCKER_IMAGES = {
        'c': 'tsukisama9292/judger-runner:c',
        'cpp': 'tsukisama9292/judger-runner:c_plus_plus'
    }
    
    def __init__(self):
        """初始化 Docker 客戶端和容器池"""
        try:
            self.docker_client = docker.from_env()
            self.containers = {}  # 容器池
            print("✅ 高速版 Docker 客戶端初始化成功")
        except DockerException as e:
            print(f"❌ Docker 客戶端初始化失敗: {e}")
            raise
    
    def __del__(self):
        """清理所有容器和資源"""
        self.cleanup_all()
        if hasattr(self, 'docker_client'):
            self.docker_client.close()
    
    def get_or_create_container(self, language: str):
        """獲取或創建容器"""
        if language not in self.containers or not self._is_container_running(self.containers[language]):
            # 創建新容器
            image_name = self.DOCKER_IMAGES[language]
            print(f"🔄 創建新的 {language} 容器...")
            
            container = self.docker_client.containers.run(
                image_name,
                command="sleep infinity",
                detach=True,
                remove=False
            )
            self.containers[language] = container
            print(f"✅ {language} 容器已就緒")
        
        return self.containers[language]
    
    def _is_container_running(self, container):
        """檢查容器是否正在運行"""
        try:
            container.reload()
            return container.status == 'running'
        except:
            return False
    
    def run_test_fast(self, language: str, user_code: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """高速執行測試 - 重用容器"""
        start_time = time.time()
        
        try:
            # 1. 獲取或創建容器
            container = self.get_or_create_container(language)
            
            # 2. 準備文件
            user_filename = "user.c" if language == 'c' else "user.cpp"
            
            # 創建臨時文件
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f".{language}") as f:
                f.write(user_code)
                temp_user_file = f.name
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json") as f:
                json.dump(config, f, indent=2)
                temp_config_file = f.name
            
            try:
                # 3. 快速複製文件到容器
                container.put_archive('/app', 
                    self._create_tar([
                        (temp_user_file, user_filename),
                        (temp_config_file, 'config.json')
                    ]))
                
                # 4. 執行測試命令（一條命令完成所有操作）
                exec_result = container.exec_run(
                    "bash -c 'make clean > /dev/null 2>&1 && make build > /dev/null 2>&1 && make test > /dev/null 2>&1'",
                    workdir='/app'
                )
                
                # 5. 立即讀取結果
                try:
                    archive, _ = container.get_archive('/app/result.json')
                    result_content = self._extract_file_from_tar(archive)
                    result_json = json.loads(result_content)
                    
                    elapsed = time.time() - start_time
                    print(f"⚡ 高速測試完成 ({elapsed:.2f}s)")
                    return result_json
                    
                except Exception as e:
                    return {
                        "status": "ERROR",
                        "message": f"無法讀取結果: {e}",
                        "exit_code": exec_result.exit_code
                    }
                    
            finally:
                # 清理臨時文件
                os.unlink(temp_user_file)
                os.unlink(temp_config_file)
                
        except Exception as e:
            return {
                "status": "ERROR",
                "message": str(e)
            }
    
    def _create_tar(self, files):
        """創建 tar 檔案"""
        import tarfile
        import io
        
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            for src_path, dst_name in files:
                tar.add(src_path, arcname=dst_name)
        tar_stream.seek(0)
        return tar_stream.getvalue()
    
    def _extract_file_from_tar(self, archive):
        """從 tar 檔案中提取文件內容"""
        import tarfile
        import io
        
        tar_stream = io.BytesIO()
        for chunk in archive:
            tar_stream.write(chunk)
        tar_stream.seek(0)
        
        with tarfile.open(fileobj=tar_stream, mode='r') as tar:
            for member in tar.getmembers():
                if member.isfile():
                    f = tar.extractfile(member)
                    if f:
                        return f.read().decode('utf-8')
        raise Exception("無法從 tar 檔案中找到文件")
    
    def cleanup_all(self):
        """清理所有容器"""
        for lang, container in self.containers.items():
            try:
                print(f"🗑️ 清理 {lang} 容器...")
                container.stop(timeout=2)
                container.remove()
            except:
                pass
        self.containers.clear()
        print("✅ 所有容器已清理")

# 創建高速版實例
print("⚡ 創建高速版 OJ 微服務實例...")
oj_fast = OJMicroserviceFast()