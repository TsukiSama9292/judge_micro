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

class OJMicroservice:
    """C/C++ 微服務 OJ 系統的 Python 介面"""
    
    # Docker 映像名稱
    DOCKER_IMAGES = {
        'c': 'tsukisama9292/judger-runner:c',
        'cpp': 'tsukisama9292/judger-runner:c_plus_plus'
    }
    
    # 支援的語言標準
    LANGUAGE_STANDARDS = {
        'c': ['c99', 'c11', 'c17', 'c23'],
        'cpp': ['c++11', 'c++14', 'c++17', 'c++20', 'c++23']
    }
    
    def __init__(self):
        """初始化 Docker 客戶端"""
        try:
            self.docker_client = docker.from_env()
            print("✅ Docker 客戶端初始化成功")
        except DockerException as e:
            print(f"❌ Docker 客戶端初始化失敗: {e}")
            raise
    
    def __del__(self):
        """清理資源"""
        if hasattr(self, 'docker_client'):
            self.docker_client.close()
    
    def create_config(self, 
                     language: str,
                     solve_params: List[Dict[str, Any]], 
                     expected: Dict[str, Any],
                     function_type: str = "int",
                     standard: Optional[str] = None,
                     compiler_flags: str = "-Wall -Wextra -O2") -> Dict[str, Any]:
        """
        創建配置文件內容
        
        Args:
            language: 'c' 或 'cpp'
            solve_params: 函數參數列表
            expected: 期望結果
            function_type: 函數返回類型
            standard: 語言標準 (如 c11, c++20)
            compiler_flags: 編譯器標誌
        """
        config = {
            "solve_params": solve_params,
            "expected": expected,
            "function_type": function_type
        }
        
        if standard:
            if language == 'c':
                config["c_standard"] = standard
            elif language == 'cpp':
                config["cpp_standard"] = standard
            config["compiler_flags"] = compiler_flags
        
        return config
    
    def run_test(self, 
                 language: str,
                 user_code: str,
                 config: Dict[str, Any],
                 timeout: int = 30) -> Dict[str, Any]:
        """
        使用 Docker 容器執行測試 - 一氣呵成版本
        
        Args:
            language: 'c' 或 'cpp'
            user_code: 用戶代碼內容
            config: 配置文件內容
            timeout: 超時時間（秒）
        
        Returns:
            包含執行結果的字典
        """
        if language not in self.DOCKER_IMAGES:
            raise ValueError(f"不支援的語言: {language}")
        
        image_name = self.DOCKER_IMAGES[language]
        container = None
        
        try:
            # # 拉取最新映像
            # print(f"🔄 拉取 Docker 映像: {image_name}")
            # self.docker_client.images.pull(image_name)
            
            # 創建並啟動容器
            print(f"🚀 啟動容器...")
            container = self.docker_client.containers.run(
                image_name,
                command="sleep infinity",  # 保持容器運行
                detach=True,
                remove=False  # 暫時不自動刪除，需要手動控制
            )
            
            # 1. 複製用戶代碼到容器
            user_filename = "user.c" if language == 'c' else "user.cpp"
            print(f"📝 複製用戶代碼到容器: {user_filename}")
            
            # 創建臨時文件
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f".{language}") as f:
                f.write(user_code)
                temp_user_file = f.name
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                temp_config_file = f.name
            
            try:
                # 複製文件到容器
                container.put_archive('/app', 
                    self._create_tar([
                        (temp_user_file, user_filename),
                        (temp_config_file, 'config.json')
                    ]))
                
                # 2. 執行測試命令
                print(f"⚙️ 執行測試命令...")
                exec_result = container.exec_run(
                    "bash -c 'make clean && make build && make test'",
                    workdir='/app'
                )
                
                print(f"📋 執行日誌:\n{exec_result.output.decode('utf-8')}")
                
                # 3. 立即讀取結果文件
                print(f"📖 讀取測試結果...")
                try:
                    archive, _ = container.get_archive('/app/result.json')
                    result_content = self._extract_file_from_tar(archive)
                    result_json = json.loads(result_content)
                    print("✅ 測試執行完成，結果已獲取")
                    return result_json
                    
                except Exception as e:
                    print(f"⚠️ 無法讀取 result.json: {e}")
                    return {
                        "status": "ERROR",
                        "message": f"無法讀取結果文件: {e}",
                        "logs": exec_result.output.decode('utf-8'),
                        "exit_code": exec_result.exit_code
                    }
                    
            finally:
                # 清理臨時文件
                os.unlink(temp_user_file)
                os.unlink(temp_config_file)
                
        except Exception as e:
            print(f"❌ 執行失敗: {e}")
            return {
                "status": "ERROR",
                "message": str(e),
                "logs": ""
            }
        finally:
            # 4. 立即關閉並移除容器
            if container:
                try:
                    print(f"🗑️ 關閉容器...")
                    container.stop(timeout=5)
                    container.remove()
                    print("✅ 容器已清理")
                except Exception as e:
                    print(f"⚠️ 清理容器時出錯: {e}")
    
    def _create_tar(self, files):
        """創建 tar 檔案包含多個文件"""
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
    
    def test_with_version(self,
                         language: str,
                         user_code: str,
                         solve_params: List[Dict[str, Any]],
                         expected: Dict[str, Any],
                         standard: Optional[str] = None,
                         timeout: int = 30) -> Dict[str, Any]:
        """
        使用指定語言版本執行測試
        
        Args:
            language: 'c' 或 'cpp'
            user_code: 用戶代碼
            solve_params: 函數參數
            expected: 期望結果
            standard: 語言標準
            timeout: 超時時間
        
        Returns:
            測試結果
        """
        # 驗證語言標準
        if standard and standard not in self.LANGUAGE_STANDARDS.get(language, []):
            print(f"⚠️ 警告: {standard} 可能不被 {language} 支援")
        
        # 創建配置
        config = self.create_config(
            language=language,
            solve_params=solve_params,
            expected=expected,
            standard=standard
        )
        
        print(f"🔧 使用配置: {json.dumps(config, indent=2, ensure_ascii=False)}")
        
        # 執行測試
        return self.run_test(language, user_code, config, timeout)