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
from judge_micro.docker.client import default_docker_client

class JudgeMicroservice:
    """每次創建新容器並立即銷毀"""
    
    DOCKER_IMAGES = {
        'c': 'tsukisama9292/judge_micro:c',
        'cpp': 'tsukisama9292/judge_micro:c_plus_plus'
    }
    
    def __init__(self, docker_client=None):
        """初始化 Docker 客戶端"""
        try:
            if docker_client:
                self.docker_client = docker_client
            else:
                # 使用預設的 Docker 客戶端
                self.docker_client = default_docker_client
            print("🚀 高效率微服務已就緒")
        except DockerException as e:
            print(f"❌ Docker 客戶端初始化失敗: {e}")
            raise
    
    def __del__(self):
        """清理資源"""
        if hasattr(self, 'docker_client'):
            self.docker_client.close()
    
    def run_microservice(self, 
                        language: str, 
                        user_code: str, 
                        config: Dict[str, Any],
                        show_logs: bool = False) -> Dict[str, Any]:
        """
        高效率微服務執行 - 創建->執行->銷毀一氣呵成
        
        Args:
            language: 'c' 或 'cpp'
            user_code: 用戶代碼
            config: 測試配置
            show_logs: 是否顯示詳細日誌
        """
        if language not in self.DOCKER_IMAGES:
            raise ValueError(f"不支援的語言: {language}")
        
        image_name = self.DOCKER_IMAGES[language]
        container = None
        start_time = time.time()
        
        try:
            # 1. 快速創建容器（不等待完全啟動）
            if show_logs:
                print(f"🏗️ 創建 {language} 微服務容器...")
            
            container = self.docker_client.containers.create(
                image_name,
                command="sleep infinity",
                detach=True
            )
            container.start()
            
            # 2. 準備並上傳文件
            user_filename = "user.c" if language == 'c' else "user.cpp"
            
            # 創建 tar 檔案包含所有文件
            tar_data = self._create_file_tar(user_code, config, user_filename)
            
            # 3. 一次性上傳並解壓縮所有文件（會自動覆蓋同名文件）
            container.put_archive('/app', tar_data)
            
            # 驗證文件是否正確上傳和覆蓋（調試）
            # if show_logs:
            #     # 檢查上傳前的文件內容
            #     pre_check = container.exec_run(f"cat /app/{user_filename} 2>/dev/null || echo 'FILE_NOT_EXISTS'", workdir='/app')
            #     print(f"📄 上傳前 {user_filename} 內容預覽:")
            #     print(f"   {pre_check.output.decode('utf-8')[:100]}...")
                
            #     # 檢查文件是否存在和時間戳
            #     check_result = container.exec_run(f"ls -la /app/{user_filename} /app/config.json", workdir='/app')
            #     if check_result.exit_code == 0:
            #         print(f"✅ 文件上傳成功: {user_filename}, config.json")
            #         print(f"📊 文件詳情:\n{check_result.output.decode('utf-8')}")
                    
            #         # 驗證文件內容是否正確
            #         content_check = container.exec_run(f"head -5 /app/{user_filename}", workdir='/app')
            #         print(f"📝 {user_filename} 文件內容前5行:")
            #         print(f"   {content_check.output.decode('utf-8')}")
            #     else:
            #         print(f"⚠️ 文件上傳可能有問題")
            
            # 4. 執行測試（靜默模式提升速度）
            if show_logs:
                print(f"⚙️ 執行測試...")
            
            exec_result = container.exec_run(
                "bash -c 'make clean >/dev/null 2>&1 && make build >/dev/null 2>&1 && make test >/dev/null 2>&1'",
                workdir='/app'
            )
            
            # 5. 立即獲取結果
            try:
                archive, _ = container.get_archive('/app/result.json')
                result_content = self._extract_result_from_tar(archive)
                result_json = json.loads(result_content)
                
                elapsed = time.time() - start_time
                if show_logs:
                    print(f"⚡ 微服務完成 ({elapsed:.3f}s)")
                
                return result_json
                
            except Exception as e:
                return {
                    "status": "ERROR",
                    "message": f"無法讀取結果: {e}",
                    "exit_code": exec_result.exit_code,
                    "execution_time": time.time() - start_time
                }
                
        except Exception as e:
            return {
                "status": "ERROR", 
                "message": str(e),
                "execution_time": time.time() - start_time
            }
        finally:
            # 6. 立即清理容器（微服務核心特性）
            if container:
                try:
                    if show_logs:
                        print(f"🗑️ 銷毀容器...")
                    container.stop(timeout=1)
                    container.remove()
                    if show_logs:
                        print(f"✅ 容器已銷毀")
                except Exception as e:
                    if show_logs:
                        print(f"⚠️ 清理容器時出錯: {e}")
    
    def _create_file_tar(self, user_code: str, config: Dict[str, Any], user_filename: str):
        """高效創建包含所有文件的 tar，確保正確覆蓋同名文件"""
        import tarfile
        import io
        import time
        
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            # 添加用戶代碼文件
            user_data = user_code.encode('utf-8')
            user_info = tarfile.TarInfo(name=user_filename)
            user_info.size = len(user_data)
            user_info.mode = 0o644  # 設置文件權限為 rw-r--r--
            user_info.mtime = time.time()  # 設置當前時間戳
            user_info.type = tarfile.REGTYPE  # 明確指定為普通文件
            tar.addfile(user_info, io.BytesIO(user_data))
            
            # 添加配置文件
            config_data = json.dumps(config, indent=2).encode('utf-8')
            config_info = tarfile.TarInfo(name='config.json')
            config_info.size = len(config_data)
            config_info.mode = 0o644  # 設置文件權限為 rw-r--r--
            config_info.mtime = time.time()  # 設置當前時間戳
            config_info.type = tarfile.REGTYPE  # 明確指定為普通文件
            tar.addfile(config_info, io.BytesIO(config_data))
        
        tar_stream.seek(0)
        return tar_stream.getvalue()
    
    def _extract_result_from_tar(self, archive):
        """高效提取結果文件"""
        import tarfile
        import io
        
        tar_stream = io.BytesIO()
        for chunk in archive:
            tar_stream.write(chunk)
        tar_stream.seek(0)
        
        with tarfile.open(fileobj=tar_stream, mode='r') as tar:
            for member in tar.getmembers():
                if member.isfile() and member.name.endswith('result.json'):
                    f = tar.extractfile(member)
                    if f:
                        return f.read().decode('utf-8')
        raise Exception("無法找到結果文件")
    
    def test_with_version(self,
                         language: str,
                         user_code: str,
                         solve_params: List[Dict[str, Any]],
                         expected: Dict[str, Any],
                         standard: Optional[str] = None,
                         show_logs: bool = False) -> Dict[str, Any]:
        """
        使用指定版本執行微服務測試
        """
        # 創建配置
        config = {
            "solve_params": solve_params,
            "expected": expected,
            "function_type": "int"
        }
        
        if standard:
            if language == 'c':
                config["c_standard"] = standard
            elif language == 'cpp':
                config["cpp_standard"] = standard
            config["compiler_flags"] = "-Wall -Wextra -O2"
        
        if show_logs:
            print(f"🔧 配置: {language}" + (f" ({standard})" if standard else ""))
        
        return self.run_microservice(language, user_code, config, show_logs)
    
    def batch_test(self, tests: List[Dict[str, Any]], show_progress: bool = True) -> List[Dict[str, Any]]:
        """
        批量執行微服務測試
        
        Args:
            tests: 測試列表，每個包含 language, user_code, solve_params, expected 等
            show_progress: 是否顯示進度
        """
        results = []
        total = len(tests)
        
        for i, test in enumerate(tests, 1):
            if show_progress:
                print(f"📊 執行測試 {i}/{total} ({test.get('language', 'unknown')})")
            
            result = self.test_with_version(**test)
            results.append(result)
            
            if show_progress:
                status = "✅" if result.get('status') == 'SUCCESS' else "❌"
                print(f"{status} 測試 {i} 完成")
        
        return results

# 創建高效率微服務實例
print("🚀 創建高效率微服務實例...")
judge_micro = JudgeMicroservice()