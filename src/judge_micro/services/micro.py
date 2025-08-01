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
from judge_micro.config.settings import setting
from judge_micro.docker.images import DOCKER_IMAGES

class JudgeMicroservice:
    
    DOCKER_IMAGES = DOCKER_IMAGES
    
    def __init__(self, docker_client=None, continue_on_timeout: bool = None):
        """Initialize Docker client
        
        Args:
            docker_client: Docker client instance
            continue_on_timeout: If True, continue execution even after timeout; 
                               If False, immediately stop container on timeout.
                               If None, use setting from configuration file.
        """
        try:
            if docker_client:
                self.docker_client = docker_client
            else:
                # Use default Docker client
                self.docker_client = default_docker_client
            
            # Use provided value or default from settings
            self.continue_on_timeout = continue_on_timeout if continue_on_timeout is not None else setting.continue_on_timeout
            print("🚀 Judge microservice is ready")
        except DockerException as e:
            print(f"❌ Docker client initialization failed: {e}")
            raise
    
    def __del__(self):
        """Clean up resources"""
        if hasattr(self, 'docker_client'):
            self.docker_client.close()
    
    def run_microservice(self, 
                        language: str, 
                        user_code: str, 
                        config: Dict[str, Any],
                        show_logs: bool = False,
                        compile_timeout: int = None,
                        execution_timeout: int = None) -> Dict[str, Any]:
        """
        Efficient microservice execution - Create->Execute->Destroy in one go
        
        Args:
            language: 'c', 'cpp', 'python', or specific python version like 'python-3.11'
            user_code: User's code
            config: Test configuration
            show_logs: Whether to show detailed logs
            compile_timeout: Maximum compilation time in seconds (uses setting.compile_timeout if None)
            execution_timeout: Maximum execution time in seconds (uses setting.container_timeout if None)
        """
        if language not in self.DOCKER_IMAGES:
            raise ValueError(f"Unsupported language: {language}")
        
        # Use provided timeouts or defaults from settings
        compile_timeout_val = compile_timeout if compile_timeout is not None else getattr(setting, 'compile_timeout', 30)  # Default 30s for compilation
        execution_timeout_val = execution_timeout if execution_timeout is not None else setting.container_timeout
        image_name = self.DOCKER_IMAGES[language]
        container = None
        start_time = time.time()
        
        # Check if this is a Python language
        is_python = language.startswith('python')
        
        try:
            # 1. Quickly create container (don't wait for full startup)
            if show_logs:
                print(f"🏗️ Creating {language} microservice container...")
            
            container = self.docker_client.containers.create(
                image_name,
                cpu_quota=int(100000* setting.container_cpu),  # CPU limit
                mem_limit=setting.container_mem,  # Memory limit
                privileged=False,  # No privileged mode needed
                network_disabled=True,  # Disable network
                command="sleep infinity",
                detach=True
            )
            container.start()
            
            # 2. Prepare and upload files
            if is_python:
                user_filename = "user.py"
            else:
                user_filename = "user.c" if language == 'c' else "user.cpp"
            
            # Create tar archive containing all files
            tar_data = self._create_file_tar(user_code, config, user_filename)
            
            # 3. Upload and extract all files at once (automatically overwrites same-name files)
            container.put_archive('/app', tar_data)
            
            # 4. For non-Python languages, compile the code (with compilation timeout constraint)
            if not is_python:
                if show_logs:
                    print(f"🔨 Compiling code (timeout: {compile_timeout_val}s)...")
                
                compile_start_time = time.time()
                
                try:
                    compile_result = container.exec_run(
                        f"bash -c 'timeout {compile_timeout_val} bash -c \"make clean >/dev/null 2>&1 && make build >/dev/null 2>&1\"'",
                        workdir='/app'
                    )
                    
                    compile_execution_time = time.time() - compile_start_time
                    
                    # Check if compilation exceeded timeout
                    if compile_execution_time > compile_timeout_val:
                        if show_logs:
                            print(f"⏰ Compilation timeout ({compile_timeout_val}s exceeded)...")
                        container.stop(timeout=1)
                        return {
                            "status": "COMPILE_TIMEOUT",
                            "message": f"Compilation exceeded timeout limit of {compile_timeout_val} seconds",
                            "execution_time": time.time() - start_time,
                            "compile_execution_time": compile_execution_time
                        }
                    
                    if compile_result.exit_code != 0:
                        # Check if it's a timeout exit code (124 from timeout command)
                        if compile_result.exit_code == 124:
                            return {
                                "status": "COMPILE_TIMEOUT",
                                "message": f"Compilation exceeded timeout limit of {compile_timeout_val} seconds",
                                "execution_time": time.time() - start_time,
                                "compile_execution_time": compile_execution_time
                            }
                        else:
                            return {
                                "status": "COMPILE_ERROR",
                                "message": "Compilation failed",
                                "compile_output": compile_result.output.decode('utf-8', errors='ignore'),
                                "execution_time": time.time() - start_time,
                                "compile_execution_time": compile_execution_time
                            }
                            
                except Exception as compile_error:
                    return {
                        "status": "COMPILE_ERROR",
                        "message": f"Compilation error: {compile_error}",
                        "execution_time": time.time() - start_time,
                        "compile_execution_time": time.time() - compile_start_time
                    }
            else:
                # For Python, we skip compilation step
                compile_start_time = time.time()
                compile_execution_time = 0
                if show_logs:
                    print(f"🐍 Python detected, skipping compilation...")
            
            # 5. Now run the test with execution timeout constraint
            if show_logs:
                test_msg = "⚙️ Running Python test" if is_python else "⚙️ Running test"
                print(f"{test_msg} (timeout: {execution_timeout_val}s)...")
            
            test_start_time = time.time()
            
            # Check if we should handle timeout
            if self.continue_on_timeout:
                # Execute without timeout handling - let it complete
                exec_result = container.exec_run(
                    "bash -c 'make test >/dev/null 2>&1'",
                    workdir='/app'
                )
            else:
                # Execute with timeout - stop container if it exceeds timeout
                try:

                    exec_result = container.exec_run(
                        "bash -c 'timeout {execution_timeout_val} make test >/dev/null 2>&1'".format(execution_timeout_val=execution_timeout_val),
                        workdir='/app'
                    )
                    
                    # Check if execution time exceeded timeout
                    test_execution_time = time.time() - test_start_time
                    if test_execution_time > execution_timeout_val:
                        if show_logs:
                            print(f"⏰ Test execution timeout ({execution_timeout_val}s exceeded), stopping container...")
                        container.stop(timeout=1)
                        return {
                            "status": "TIMEOUT",
                            "message": f"Test execution exceeded timeout limit of {execution_timeout_val} seconds",
                            "execution_time": time.time() - start_time,
                            "test_execution_time": test_execution_time,
                            "compile_execution_time": time.time() - compile_start_time
                        }
                    
                    # Check if it's a timeout exit code (124 from timeout command)
                    if exec_result.exit_code == 124:
                        return {
                            "status": "TIMEOUT",
                            "message": f"Test execution exceeded timeout limit of {execution_timeout_val} seconds",
                            "execution_time": time.time() - start_time,
                            "test_execution_time": test_execution_time,
                            "compile_execution_time": time.time() - compile_start_time
                        }
                        
                except Exception as timeout_error:
                    return {
                        "status": "TIMEOUT_ERROR",
                        "message": f"Timeout handling error: {timeout_error}",
                        "execution_time": time.time() - start_time,
                        "test_execution_time": time.time() - test_start_time,
                        "compile_execution_time": time.time() - compile_start_time
                    }
            
            # 6. Immediately get results
            try:
                archive, _ = container.get_archive('/app/result.json')
                result_content = self._extract_result_from_tar(archive)
                result_json = json.loads(result_content)
                
                elapsed = time.time() - start_time
                test_elapsed = time.time() - test_start_time
                compile_elapsed = time.time() - compile_start_time
                if show_logs:
                    print(f"⚡ Microservice completed (total: {elapsed:.3f}s, compile: {compile_elapsed:.3f}s, test: {test_elapsed:.3f}s)")
                
                # Add timing information to result
                result_json["total_execution_time"] = elapsed
                result_json["test_execution_time"] = test_elapsed
                result_json["compile_execution_time"] = compile_elapsed
                
                return result_json
                
            except Exception as e:
                return {
                    "status": "ERROR",
                    "message": f"Unable to read result: {e}",
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
            # 7. Immediately clean up container (core microservice feature)
            if container:
                try:
                    if show_logs:
                        print(f"🗑️ Destroying container...")
                    container.stop(timeout=1)
                    container.remove()
                    if show_logs:
                        print(f"✅ Container destroyed")
                except Exception as e:
                    if show_logs:
                        print(f"⚠️ Error during container cleanup: {e}")
    
    def _create_file_tar(self, user_code: str, config: Dict[str, Any], user_filename: str):
        """Efficiently create tar containing all files, ensuring proper overwrite of same-name files"""
        import tarfile
        import io
        import time
        
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            # Add user code file
            user_data = user_code.encode('utf-8')
            user_info = tarfile.TarInfo(name=user_filename)
            user_info.size = len(user_data)
            user_info.mode = 0o644  # Set file permissions to rw-r--r--
            user_info.mtime = time.time()  # Set current timestamp
            user_info.type = tarfile.REGTYPE  # Explicitly specify as regular file
            tar.addfile(user_info, io.BytesIO(user_data))
            
            # Add configuration file
            config_data = json.dumps(config, indent=2).encode('utf-8')
            config_info = tarfile.TarInfo(name='config.json')
            config_info.size = len(config_data)
            config_info.mode = 0o644  # Set file permissions to rw-r--r--
            config_info.mtime = time.time()  # Set current timestamp
            config_info.type = tarfile.REGTYPE  # Explicitly specify as regular file
            tar.addfile(config_info, io.BytesIO(config_data))
        
        tar_stream.seek(0)
        return tar_stream.getvalue()
    
    def _extract_result_from_tar(self, archive):
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
        raise Exception("Unable to find result file")
    
    def test_with_version(self,
                         language: str,
                         user_code: str,
                         solve_params: List[Dict[str, Any]],
                         expected: Dict[str, Any],
                         standard: Optional[str] = None,
                         show_logs: bool = False,
                         compile_timeout: int = None,
                         execution_timeout: int = None) -> Dict[str, Any]:
        """
        Execute microservice test using specified version
        
        Args:
            language: Programming language ('c', 'cpp', 'python', or specific python version like 'python-3.11')
            user_code: User's source code
            solve_params: Parameters for solving
            expected: Expected results
            standard: Language standard (e.g., 'c11', 'cpp20') - ignored for Python
            show_logs: Whether to show execution logs
            compile_timeout: Maximum compilation time in seconds (uses setting.compile_timeout if None)
            execution_timeout: Maximum execution time in seconds (uses setting.container_timeout if None)
        """
        # Create configuration
        config = {
            "solve_params": solve_params,
            "expected": expected,
            "function_type": "int"
        }
        
        # For non-Python languages, add compiler settings
        if standard and not language.startswith('python'):
            if language == 'c':
                config["c_standard"] = standard
            elif language == 'cpp':
                config["cpp_standard"] = standard
            config["compiler_flags"] = "-Wall -Wextra -O2"
        
        if show_logs:
            version_info = f" ({standard})" if standard and not language.startswith('python') else ""
            print(f"🔧 Configuration: {language}{version_info}")
        
        return self.run_microservice(language, user_code, config, show_logs, compile_timeout, execution_timeout)
    
    def batch_test(self, tests: List[Dict[str, Any]], show_progress: bool = True) -> List[Dict[str, Any]]:
        """
        Execute batch microservice tests
        
        Args:
            tests: List of tests, each containing language, user_code, solve_params, expected, etc.
            show_progress: Whether to show progress
        """
        results = []
        total = len(tests)
        
        for i, test in enumerate(tests, 1):
            if show_progress:
                print(f"📊 Executing test {i}/{total} ({test.get('language', 'unknown')})")
            
            result = self.test_with_version(**test)
            results.append(result)
            
            if show_progress:
                status = "✅" if result.get('status') == 'SUCCESS' else "❌"
                print(f"{status} Test {i} completed")
        
        return results

    def optimized_batch_test(self, 
                           language: str,
                           user_code: str,
                           configs: List[Dict[str, Any]],
                           show_progress: bool = True,
                           compile_timeout: int = None,
                           execution_timeout: int = None) -> List[Dict[str, Any]]:
        """
        Execute optimized batch tests for same language and user code with different configs.
        For compiled languages (C/C++): compiles once and runs multiple test configurations without recompilation.
        For Python: skips compilation and runs multiple test configurations directly.
        
        Args:
            language: Programming language ('c', 'cpp', 'python', or specific python version like 'python-3.11')
            user_code: User's source code (same for all tests)
            configs: List of test configurations (different test data)
            show_progress: Whether to show progress
            compile_timeout: Maximum compilation time in seconds (ignored for Python)
            execution_timeout: Maximum execution time in seconds per test
        
        Returns:
            List of test results for each configuration
        """
        if language not in self.DOCKER_IMAGES:
            raise ValueError(f"Unsupported language: {language}")
        
        if not configs:
            return []
        
        # Use provided timeouts or defaults from settings
        compile_timeout_val = compile_timeout if compile_timeout is not None else getattr(setting, 'compile_timeout', 30)
        execution_timeout_val = execution_timeout if execution_timeout is not None else setting.container_timeout
        image_name = self.DOCKER_IMAGES[language]
        container = None
        start_time = time.time()
        results = []
        
        # Check if this is a Python language
        is_python = language.startswith('python')
        
        try:
            if show_progress:
                print(f"🏗️ Creating {language} container for optimized batch execution...")
            
            # 1. Create and start container
            container = self.docker_client.containers.create(
                image_name,
                cpu_quota=int(100000 * setting.container_cpu),
                mem_limit=setting.container_mem,
                privileged=False,
                network_disabled=True,
                command="sleep infinity",
                detach=True
            )
            container.start()
            
            # 2. Upload user code and handle compilation
            if is_python:
                user_filename = "user.py"
            else:
                user_filename = "user.c" if language == 'c' else "user.cpp"
            
            # Upload user code file only
            user_tar_data = self._create_user_code_tar(user_code, user_filename)
            container.put_archive('/app', user_tar_data)
            
            # 3. For non-Python languages, compile once
            if not is_python:
                if show_progress:
                    print(f"🔨 Compiling code once (timeout: {compile_timeout_val}s)...")
                
                compile_start_time = time.time()
                
                try:
                    # Compile the user code once
                    compile_result = container.exec_run(
                        f"bash -c 'timeout {compile_timeout_val} bash -c \"make clean >/dev/null 2>&1 && make build >/dev/null 2>&1\"'",
                        workdir='/app'
                    )
                    
                    compile_execution_time = time.time() - compile_start_time
                    
                    # Check compilation result
                    if compile_execution_time > compile_timeout_val:
                        if show_progress:
                            print(f"⏰ Compilation timeout ({compile_timeout_val}s exceeded)...")
                        return [{
                            "status": "COMPILE_TIMEOUT",
                            "message": f"Compilation exceeded timeout limit of {compile_timeout_val} seconds",
                            "execution_time": time.time() - start_time,
                            "compile_execution_time": compile_execution_time,
                            "config_index": i
                        } for i in range(len(configs))]
                    
                    if compile_result.exit_code != 0:
                        if compile_result.exit_code == 124:
                            error_result = {
                                "status": "COMPILE_TIMEOUT",
                                "message": f"Compilation exceeded timeout limit of {compile_timeout_val} seconds",
                                "execution_time": time.time() - start_time,
                                "compile_execution_time": compile_execution_time
                            }
                        else:
                            error_result = {
                                "status": "COMPILE_ERROR",
                                "message": "Compilation failed",
                                "compile_output": compile_result.output.decode('utf-8', errors='ignore'),
                                "execution_time": time.time() - start_time,
                                "compile_execution_time": compile_execution_time
                            }
                        
                        # Return same error for all configs since compilation failed
                        return [dict(error_result, config_index=i) for i in range(len(configs))]
                            
                except Exception as compile_error:
                    error_result = {
                        "status": "COMPILE_ERROR",
                        "message": f"Compilation error: {compile_error}",
                        "execution_time": time.time() - start_time,
                        "compile_execution_time": time.time() - compile_start_time
                    }
                    return [dict(error_result, config_index=i) for i in range(len(configs))]
                
                if show_progress:
                    print(f"✅ Compilation successful! Running {len(configs)} test configurations...")
            else:
                # For Python, skip compilation
                compile_start_time = time.time()
                compile_execution_time = 0
                if show_progress:
                    print(f"🐍 Python detected, skipping compilation. Running {len(configs)} test configurations...")
            
            # 4. Run tests with different configurations
            for i, config in enumerate(configs):
                if show_progress:
                    print(f"⚙️ Running test configuration {i+1}/{len(configs)} (timeout: {execution_timeout_val}s)...")
                
                test_start_time = time.time()
                
                try:
                    # Upload new config.json for this test
                    config_tar_data = self._create_config_tar(config)
                    container.put_archive('/app', config_tar_data)
                    
                    # Run test with the new configuration
                    if self.continue_on_timeout:
                        exec_result = container.exec_run(
                            "bash -c 'make test >/dev/null 2>&1'",
                            workdir='/app'
                        )
                    else:
                        exec_result = container.exec_run(
                            f"bash -c 'timeout {execution_timeout_val} make test >/dev/null 2>&1'",
                            workdir='/app'
                        )
                        
                        test_execution_time = time.time() - test_start_time
                        if test_execution_time > execution_timeout_val:
                            if show_progress:
                                print(f"⏰ Test {i+1} timeout ({execution_timeout_val}s exceeded)...")
                            results.append({
                                "status": "TIMEOUT",
                                "message": f"Test execution exceeded timeout limit of {execution_timeout_val} seconds",
                                "execution_time": time.time() - start_time,
                                "test_execution_time": test_execution_time,
                                "compile_execution_time": compile_execution_time,
                                "config_index": i
                            })
                            continue
                        
                        if exec_result.exit_code == 124:
                            results.append({
                                "status": "TIMEOUT",
                                "message": f"Test execution exceeded timeout limit of {execution_timeout_val} seconds",
                                "execution_time": time.time() - start_time,
                                "test_execution_time": test_execution_time,
                                "compile_execution_time": compile_execution_time,
                                "config_index": i
                            })
                            continue
                    
                    # Get test results
                    try:
                        archive, _ = container.get_archive('/app/result.json')
                        result_content = self._extract_result_from_tar(archive)
                        result_json = json.loads(result_content)
                        
                        test_elapsed = time.time() - test_start_time
                        total_elapsed = time.time() - start_time
                        
                        # Add timing and config information
                        result_json["total_execution_time"] = total_elapsed
                        result_json["test_execution_time"] = test_elapsed
                        result_json["compile_execution_time"] = compile_execution_time
                        result_json["config_index"] = i
                        
                        results.append(result_json)
                        
                        if show_progress:
                            status = "✅" if result_json.get('status') == 'SUCCESS' else "❌"
                            print(f"{status} Test {i+1} completed (test: {test_elapsed:.3f}s)")
                            
                    except Exception as e:
                        results.append({
                            "status": "ERROR",
                            "message": f"Unable to read result: {e}",
                            "exit_code": exec_result.exit_code,
                            "execution_time": time.time() - start_time,
                            "test_execution_time": time.time() - test_start_time,
                            "compile_execution_time": compile_execution_time,
                            "config_index": i
                        })
                        
                except Exception as test_error:
                    results.append({
                        "status": "ERROR",
                        "message": f"Test execution error: {test_error}",
                        "execution_time": time.time() - start_time,
                        "test_execution_time": time.time() - test_start_time,
                        "compile_execution_time": compile_execution_time,
                        "config_index": i
                    })
            
            if show_progress:
                total_elapsed = time.time() - start_time
                print(f"🎉 Optimized batch execution completed! Total time: {total_elapsed:.3f}s (compile once + {len(configs)} tests)")
            
            return results
                
        except Exception as e:
            return [{
                "status": "ERROR", 
                "message": str(e),
                "execution_time": time.time() - start_time,
                "config_index": i
            } for i in range(len(configs))]
        finally:
            # Clean up container
            if container:
                try:
                    if show_progress:
                        print(f"🗑️ Destroying container...")
                    container.stop(timeout=1)
                    container.remove()
                    if show_progress:
                        print(f"✅ Container destroyed")
                except Exception as e:
                    if show_progress:
                        print(f"⚠️ Error during container cleanup: {e}")

    def _create_user_code_tar(self, user_code: str, user_filename: str):
        """Create tar containing only user code file"""
        import tarfile
        import io
        import time
        
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            # Add user code file
            user_data = user_code.encode('utf-8')
            user_info = tarfile.TarInfo(name=user_filename)
            user_info.size = len(user_data)
            user_info.mode = 0o644
            user_info.mtime = time.time()
            user_info.type = tarfile.REGTYPE
            tar.addfile(user_info, io.BytesIO(user_data))
        
        tar_stream.seek(0)
        return tar_stream.getvalue()

    def _create_config_tar(self, config: Dict[str, Any]):
        """Create tar containing only config.json file"""
        import tarfile
        import io
        import time
        
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            # Add configuration file
            config_data = json.dumps(config, indent=2).encode('utf-8')
            config_info = tarfile.TarInfo(name='config.json')
            config_info.size = len(config_data)
            config_info.mode = 0o644
            config_info.mtime = time.time()
            config_info.type = tarfile.REGTYPE
            tar.addfile(config_info, io.BytesIO(config_data))
        
        tar_stream.seek(0)
        return tar_stream.getvalue()

# Create judge microservice instance
print("🚀 Creating judge microservice instance...")
judge_micro = JudgeMicroservice()