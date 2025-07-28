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
from .basic import OJMicroservice

# 添加一些實用的輔助方法到 OJMicroservice 類
class OJMicroserviceExtended(OJMicroservice):
    """擴展的 OJ 微服務類，包含更多實用功能"""
    
    def run_custom_command(self,
                          language: str,
                          user_code: str,
                          config: Dict[str, Any],
                          custom_command: str = "make clean && make build && make test",
                          timeout: int = 30) -> Dict[str, Any]:
        """
        使用自定義命令執行測試
        
        Args:
            language: 'c' 或 'cpp'
            user_code: 用戶代碼內容
            config: 配置文件內容
            custom_command: 自定義執行命令
            timeout: 超時時間（秒）
        """
        if language not in self.DOCKER_IMAGES:
            raise ValueError(f"不支援的語言: {language}")
        
        image_name = self.DOCKER_IMAGES[language]
        
        # 創建臨時目錄
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 寫入用戶代碼
            if language == 'c':
                user_file = temp_path / "user.c"
            else:
                user_file = temp_path / "user.cpp"
            
            user_file.write_text(user_code, encoding='utf-8')
            
            # 寫入配置文件
            config_file = temp_path / "config.json"
            config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding='utf-8')
            
            try:
                print(f"🔄 拉取 Docker 映像: {image_name}")
                self.docker_client.images.pull(image_name)
                
                print(f"🚀 執行命令: {custom_command}")
                container = self.docker_client.containers.run(
                    image_name,
                    command=f"bash -c '{custom_command}'",
                    volumes={str(temp_path): {'bind': '/app', 'mode': 'rw'}},
                    working_dir='/app',
                    detach=True,
                    remove=True
                )
                
                # 等待容器完成
                result = container.wait(timeout=timeout)
                logs = container.logs().decode('utf-8')
                
                print(f"📋 執行日誌:\n{logs}")
                
                # 嘗試讀取結果文件
                result_file = temp_path / "result.json"
                if result_file.exists():
                    result_json = json.loads(result_file.read_text(encoding='utf-8'))
                    print("✅ 命令執行完成")
                    return result_json
                else:
                    # 如果沒有結果文件，返回基本信息
                    return {
                        "status": "COMPLETED" if result['StatusCode'] == 0 else "ERROR",
                        "exit_code": result['StatusCode'],
                        "logs": logs,
                        "message": "命令執行完成，但未生成 result.json"
                    }
                    
            except Exception as e:
                print(f"❌ 執行失敗: {e}")
                return {
                    "status": "ERROR",
                    "message": str(e),
                    "logs": ""
                }
    
    def debug_test(self,
                   language: str,
                   user_code: str,
                   config: Dict[str, Any],
                   timeout: int = 30) -> Dict[str, Any]:
        """
        調試模式：執行測試並返回詳細信息
        """
        print("🐛 調試模式：執行完整的構建和測試流程")
        return self.run_custom_command(
            language=language,
            user_code=user_code,
            config=config,
            custom_command="make clean && make build && make test && ls -la",
            timeout=timeout
        )

# 創建擴展版本的實例
print("🔧 創建擴展版 OJ 微服務實例...")
oj_ext = OJMicroserviceExtended()