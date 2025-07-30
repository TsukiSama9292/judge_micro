#!/usr/bin/env python3
"""
Config-Driven OJ Runner - Python Version
----------------------------------------
- harness.py is universal and never changes
- config.json defines input values, types and function signature
- User function receives inputs as parameters
- Type-safe with Python type hints
- Enhanced error handling with exceptions

Example config.json:
{
  "solve_params": [
    {"name": "a", "type": "int", "input_value": 3},
    {"name": "b", "type": "int", "input_value": 4}
  ],
  "expected": {"a": 6, "b": 9},
  "function_type": "int"
}

User writes only:
  def solve(a: int, b: int) -> int:
      a = a * 2
      b = b + 5
      return 0
"""

import json
import sys
import os
import subprocess
import time
import resource
import tempfile
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import ast
import textwrap


class Timer:
    """High-precision timer for measuring execution time."""
    
    def __init__(self):
        self.start_time = 0
    
    def start(self):
        self.start_time = time.perf_counter()
    
    def elapsed_ms(self) -> float:
        return (time.perf_counter() - self.start_time) * 1000.0


class ResourceMonitor:
    """Monitor resource usage during execution."""
    
    def __init__(self):
        self.start_usage = None
    
    def start(self):
        self.start_usage = resource.getrusage(resource.RUSAGE_SELF)
    
    def get_stats(self) -> Dict[str, float]:
        if self.start_usage is None:
            return {"cpu_utime": 0, "cpu_stime": 0, "maxrss_mb": 0}
            
        end_usage = resource.getrusage(resource.RUSAGE_SELF)
        
        return {
            "cpu_utime": end_usage.ru_utime - self.start_usage.ru_utime,
            "cpu_stime": end_usage.ru_stime - self.start_usage.ru_stime,
            "maxrss_mb": end_usage.ru_maxrss / 1024.0  # Convert to MB
        }


class CodeGenerator:
    """Generate Python test code based on configuration."""
    
    @staticmethod
    def generate_test_main(config: Dict[str, Any], user_file: str = "user.py") -> str:
        """Generate main test code that calls the user's solve function."""
        
        # Get function configuration
        function_type = config.get("function_type", "int")
        params = config.get("solve_params", [])
        
        # Extract module name from user file
        module_name = os.path.splitext(user_file)[0]
        
        # Build imports and user function signature
        code_lines = [
            "#!/usr/bin/env python3",
            "# Auto-generated test main for Python OJ Runner",
            "",
            "import sys",
            "import json",
            "from typing import Any, Dict, List, Optional, Union",
            f"from {module_name} import solve",
            "",
            "def main():",
            "    try:",
        ]
        
        # Initialize parameters with input values
        for param in params:
            name = param["name"]
            param_type = param["type"]
            input_value = param["input_value"]
            
            formatted_value = CodeGenerator._format_value(param_type, input_value)
            code_lines.append(f"        {name} = {formatted_value}")
        
        code_lines.append("")
        code_lines.append("        # Call solve function")
        
        # Build function call
        param_names = [param["name"] for param in params]
        param_str = ", ".join(param_names)
        
        if function_type == "void" or function_type == "None":
            code_lines.append(f"        result = solve({param_str})")
            code_lines.append("        function_result = None")
        else:
            code_lines.append(f"        result = solve({param_str})")
            code_lines.append("        function_result = result")
        
        code_lines.append("")
        code_lines.append("        # Handle tuple return (for parameter modifications)")
        code_lines.append("        if isinstance(result, tuple):")
        code_lines.append(f"            expected_params = {len(params)}")
        code_lines.append("            if len(result) == expected_params + 1:")
        code_lines.append("                # Format: (param1, param2, ..., return_value)")
        for i, param in enumerate(params):
            name = param["name"]
            code_lines.append(f"                {name} = result[{i}]")
        code_lines.append("                function_result = result[-1]")
        code_lines.append("            elif len(result) == expected_params:")
        code_lines.append("                # Format: (param1, param2, ...) with void return")
        for i, param in enumerate(params):
            name = param["name"]
            code_lines.append(f"                {name} = result[{i}]")
        code_lines.append("                function_result = None")
        
        code_lines.append("")
        code_lines.append("        # Write results to file for verification")
        code_lines.append("        with open('function_result.txt', 'w') as result_file:")
        
        # Write parameter results (for mutable parameters)
        for param in params:
            name = param["name"]
            param_type = param["type"]
            output_format = CodeGenerator._format_output(param_type, name)
            code_lines.append(f"            result_file.write(f'{name}:{output_format}\\n')")
        
        # Write return value
        if function_type == "void" or function_type == "None":
            code_lines.append("            result_file.write('return_value:None\\n')")
        else:
            code_lines.append("            result_file.write(f'return_value:{function_result}\\n')")
        
        code_lines.extend([
            "",
            "        # No automatic stdout output - let user code control stdout completely",
            "",
            "    except Exception as e:",
            "        import traceback",
            "        print(f'Runtime error: {e}', file=sys.stderr)",
            "        traceback.print_exc(file=sys.stderr)",
            "        return 1",
            "",
            "    return 0",
            "",
            "",
            "if __name__ == '__main__':",
            "    sys.exit(main())"
        ])
        
        return "\n".join(code_lines)
    
    @staticmethod
    def _format_value(param_type: str, value: Any) -> str:
        """Format input value according to Python type."""
        if param_type == "str" or param_type == "string":
            return repr(str(value))
        elif param_type == "list" or param_type.startswith("List") or param_type.startswith("vector"):
            return repr(list(value) if hasattr(value, '__iter__') and not isinstance(value, str) else [value])
        elif param_type == "dict" or param_type.startswith("Dict"):
            return repr(dict(value) if isinstance(value, dict) else {})
        elif param_type == "bool":
            return repr(bool(value))
        elif param_type == "float" or param_type == "double":
            return repr(float(value))
        elif param_type == "int" or param_type == "long":
            return repr(int(value))
        else:
            # For any other type, try to convert appropriately
            return repr(value)
    
    @staticmethod
    def _format_output(param_type: str, name: str) -> str:
        """Format output value for writing to result file."""
        if param_type == "str" or param_type == "string":
            return f'"{{{name}}}"'
        elif param_type == "list" or param_type.startswith("List") or param_type.startswith("vector"):
            # Convert list to JSON format
            return f"{{json.dumps({name})}}"
        elif param_type == "dict" or param_type.startswith("Dict"):
            # Convert dict to JSON format
            return f"{{json.dumps({name})}}"
        else:
            return f"{{{name}}}"


class ResultAnalyzer:
    """Analyze and compare execution results."""
    
    @staticmethod
    def parse_output(output: str, expected: Dict[str, Any]) -> Dict[str, Any]:
        """Parse execution output and extract actual results."""
        actual = {}
        
        # Read results from function_result.txt instead of stdout
        try:
            with open("function_result.txt", "r") as result_file:
                for line in result_file:
                    line = line.strip()
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key and value:
                            try:
                                # Try to parse as JSON first (handles complex types)
                                if value.startswith(('[', '{', '"')):
                                    actual[key] = json.loads(value)
                                # Handle special cases
                                elif value.lower() == "none":
                                    actual[key] = None
                                elif value.lower() == "true":
                                    actual[key] = True
                                elif value.lower() == "false":
                                    actual[key] = False
                                # Try numeric parsing
                                elif "." in value:
                                    actual[key] = float(value)
                                else:
                                    actual[key] = int(value)
                            except (json.JSONDecodeError, ValueError):
                                # Keep as string if parsing fails
                                actual[key] = value
        except FileNotFoundError:
            pass  # Return empty dict if no result file
        
        return actual
    
    @staticmethod
    def compare_results(expected: Dict[str, Any], actual: Dict[str, Any]) -> bool:
        """Compare expected and actual results."""
        for key, expected_value in expected.items():
            if key not in actual:
                return False
            
            actual_value = actual[key]
            
            # Handle floating point comparison with tolerance
            if isinstance(expected_value, float) and isinstance(actual_value, (int, float)):
                if abs(float(expected_value) - float(actual_value)) > 1e-9:
                    return False
            elif expected_value != actual_value:
                return False
        
        return True


class OJRunner:
    """Main runner class that orchestrates the execution."""
    
    @staticmethod
    def run(config_file: str, result_file: str) -> int:
        """Run the complete OJ evaluation process."""
        try:
            # Load configuration
            config = OJRunner._load_config(config_file)
            
            # Detect user file
            user_file = OJRunner._detect_user_file()
            
            # Generate test file
            compile_timer = Timer()
            compile_timer.start()
            
            test_code = CodeGenerator.generate_test_main(config, user_file)
            with open("test_main.py", "w") as f:
                f.write(test_code)
            
            # Check Python syntax
            compile_result = OJRunner._check_syntax(user_file)
            compile_time = compile_timer.elapsed_ms()
            
            if not compile_result["success"]:
                OJRunner._save_error_result(
                    result_file, "COMPILE_ERROR", "Syntax error", 
                    compile_result["error"], compile_result["exit_code"], compile_time
                )
                return 4
            
            # Execute program
            monitor = ResourceMonitor()
            exec_timer = Timer()
            monitor.start()
            exec_timer.start()
            
            exec_result = OJRunner._execute_program(config)
            exec_time = exec_timer.elapsed_ms()
            stats = monitor.get_stats()
            
            if not exec_result["success"]:
                OJRunner._save_error_result(
                    result_file, "RUNTIME_ERROR", "Execution failed",
                    exec_result["error"], exec_result["exit_code"], 
                    compile_time, exec_time, stats
                )
                return 5
            
            # Analyze results
            result = {
                "status": "SUCCESS",
                "stdout": exec_result["output"],
                "stderr": exec_result["error"],
                "time_ms": exec_time,
                "cpu_utime": stats["cpu_utime"],
                "cpu_stime": stats["cpu_stime"],
                "maxrss_mb": stats["maxrss_mb"],
                "compile_time_ms": compile_time
            }
            
            # Compare with expected results
            if "expected" in config:
                expected = config["expected"]
                actual = ResultAnalyzer.parse_output(exec_result["output"], expected)
                
                result["expected"] = expected
                result["actual"] = actual
                result["match"] = ResultAnalyzer.compare_results(expected, actual)
                
                if not result["match"]:
                    result["status"] = "WRONG_ANSWER"
            
            OJRunner._save_result(result_file, result)
            return 0
            
        except Exception as e:
            OJRunner._save_error_result(
                result_file, "ERROR", "Internal error", str(e), -1
            )
            return 1
    
    @staticmethod
    def _detect_user_file() -> str:
        """Detect the user file name."""
        # Check common patterns
        user_files = [
            "user.py",
            "solution.py", 
            "solve.py",
            "main.py"
        ]
        
        for filename in user_files:
            if os.path.exists(filename):
                return filename
        
        # If no standard files found, look for any .py file that's not harness or test_main
        for file in os.listdir("."):
            if (file.endswith(".py") and 
                file not in ["harness.py", "test_main.py"] and
                not file.startswith("__")):
                return file
        
        return "user.py"  # Default fallback
    
    @staticmethod
    def _load_config(filename: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Cannot load config file {filename}: {e}")
    
    @staticmethod
    def _check_syntax(user_file: str = "user.py") -> Dict[str, Any]:
        """Check Python syntax for both user file and test_main.py."""
        try:
            # Check user file syntax
            if os.path.exists(user_file):
                with open(user_file, "r") as f:
                    user_code = f.read()
                
                try:
                    ast.parse(user_code)
                except SyntaxError as e:
                    return {
                        "success": False,
                        "error": f"Syntax error in {user_file}: {e}",
                        "exit_code": 1
                    }
            else:
                return {
                    "success": False,
                    "error": f"User file {user_file} not found",
                    "exit_code": 1
                }
            
            # Check test_main.py syntax
            with open("test_main.py", "r") as f:
                test_code = f.read()
            
            try:
                ast.parse(test_code)
            except SyntaxError as e:
                return {
                    "success": False,
                    "error": f"Syntax error in test_main.py: {e}",
                    "exit_code": 1
                }
            
            return {"success": True, "error": "", "exit_code": 0}
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to check syntax: {e}",
                "exit_code": 1
            }
    
    @staticmethod
    def _execute_program(config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Python program."""
        try:
            # Get Python interpreter from config or use default
            python_cmd = config.get("python_interpreter", "python3")
            
            # Get timeout from config or use default (30 seconds)
            timeout = config.get("timeout", 30)
            
            # Create temporary files for stdout and stderr
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as stdout_file, \
                 tempfile.NamedTemporaryFile(mode='w+', delete=False) as stderr_file:
                
                stdout_path = stdout_file.name
                stderr_path = stderr_file.name
            
            try:
                # Execute the program
                process = subprocess.run(
                    [python_cmd, "test_main.py"],
                    stdout=open(stdout_path, 'w'),
                    stderr=open(stderr_path, 'w'),
                    timeout=timeout,
                    cwd=os.getcwd()
                )
                
                # Read outputs
                with open(stdout_path, 'r') as f:
                    stdout_content = f.read()
                
                with open(stderr_path, 'r') as f:
                    stderr_content = f.read()
                
                success = (process.returncode == 0)
                
                return {
                    "success": success,
                    "output": stdout_content,
                    "error": stderr_content,
                    "exit_code": process.returncode
                }
                
            finally:
                # Clean up temporary files
                try:
                    os.unlink(stdout_path)
                    os.unlink(stderr_path)
                except OSError:
                    pass
                    
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Execution timed out after {timeout} seconds",
                "exit_code": 124
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Execution failed: {e}",
                "exit_code": 1
            }
    
    @staticmethod
    def _save_result(filename: str, result: Dict[str, Any]):
        """Save execution result to JSON file."""
        try:
            with open(filename, "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save result: {e}", file=sys.stderr)
    
    @staticmethod
    def _save_error_result(filename: str, status: str, error: str, details: str, 
                          exit_code: int, compile_time: float = 0, 
                          exec_time: float = 0, stats: Optional[Dict[str, float]] = None):
        """Save error result to JSON file."""
        result = {
            "status": status,
            "error": error,
            "stderr": details,
            "exit_code": exit_code,
            "compile_time_ms": compile_time
        }
        
        if exec_time > 0:
            result["time_ms"] = exec_time
            if stats:
                result.update(stats)
        
        OJRunner._save_result(filename, result)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} config.json [result.json]", file=sys.stderr)
        return 1
    
    config_file = sys.argv[1]
    
    # Auto-generate result filename if not provided
    if len(sys.argv) >= 3:
        result_file = sys.argv[2]
    else:
        # Detect user filename and generate result filename
        user_filename = OJRunner._detect_user_file()
        
        # Extract base name without extension
        base_name = os.path.splitext(user_filename)[0]
        result_file = f"result_{base_name}.json"
        
        print(f"Auto-generated result file: {result_file}", file=sys.stderr)
    
    return OJRunner.run(config_file, result_file)


if __name__ == "__main__":
    sys.exit(main())