from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class LanguageType(str, Enum):
    """Supported programming language types"""
    C = "c"
    CPP = "cpp"


class ParameterType(str, Enum):
    """Supported parameter types"""
    INT = "int"
    FLOAT = "float"
    DOUBLE = "double"
    CHAR = "char"
    STRING = "string"
    ARRAY_INT = "array_int"
    ARRAY_FLOAT = "array_float"
    ARRAY_CHAR = "array_char"


class FunctionType(str, Enum):
    """Supported function return types"""
    INT = "int"
    FLOAT = "float"
    DOUBLE = "double"
    CHAR = "char"
    STRING = "string"
    VOID = "void"


class CStandard(str, Enum):
    """C language standards"""
    C89 = "c89"
    C99 = "c99"
    C11 = "c11"
    C17 = "c17"
    C23 = "c23"


class CppStandard(str, Enum):
    """C++ language standards"""
    CPP98 = "cpp98"
    CPP03 = "cpp03"
    CPP11 = "cpp11"
    CPP14 = "cpp14"
    CPP17 = "cpp17"
    CPP20 = "cpp20"
    CPP23 = "cpp23"


class JudgeStatus(str, Enum):
    """Judge evaluation status"""
    SUCCESS = "SUCCESS"
    COMPILE_ERROR = "COMPILE_ERROR"
    COMPILE_TIMEOUT = "COMPILE_TIMEOUT"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    TIMEOUT = "TIMEOUT"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    ERROR = "ERROR"


class SolveParameter(BaseModel):
    """Solve function parameter"""
    name: str = Field(..., description="Parameter name")
    type: ParameterType = Field(..., description="Parameter type")
    input_value: Union[int, float, str, List[Union[int, float, str]]] = Field(..., description="Input value")
    
    @field_validator('input_value')
    @classmethod
    def validate_input_value(cls, v, info):
        param_type = info.data.get('type')
        if param_type == ParameterType.INT and not isinstance(v, int):
            raise ValueError("INT type parameter must be an integer")
        elif param_type in [ParameterType.FLOAT, ParameterType.DOUBLE] and not isinstance(v, (int, float)):
            raise ValueError("FLOAT/DOUBLE type parameter must be a number")
        elif param_type == ParameterType.CHAR and not (isinstance(v, str) and len(v) == 1):
            raise ValueError("CHAR type parameter must be a single character")
        elif param_type == ParameterType.STRING and not isinstance(v, str):
            raise ValueError("STRING type parameter must be a string")
        elif param_type.value.startswith('array_') and not isinstance(v, list):
            raise ValueError("ARRAY type parameter must be an array")
        return v


class CompilerSettings(BaseModel):
    """Compiler configuration settings"""
    standard: Optional[Union[CStandard, CppStandard]] = Field(None, description="Language standard")
    flags: Optional[str] = Field("-Wall -Wextra -O2", description="Compiler flags")
    optimization_level: Optional[str] = Field("O2", description="Optimization level")


class ResourceLimits(BaseModel):
    """Resource constraints"""
    compile_timeout: Optional[int] = Field(30, description="Compilation time limit (seconds)", ge=1, le=300)
    execution_timeout: Optional[int] = Field(10, description="Execution time limit (seconds)", ge=1, le=60)
    memory_limit: Optional[str] = Field("128m", description="Memory limit")
    cpu_limit: Optional[float] = Field(1.0, description="CPU limit", ge=0.1, le=4.0)


class JudgeRequest(BaseModel):
    """Judge evaluation request"""
    language: LanguageType = Field(..., description="Programming language")
    user_code: str = Field(..., description="User code", min_length=1, max_length=50000)
    solve_params: List[SolveParameter] = Field(..., description="Solve function parameter list", min_length=1)
    expected: Dict[str, Any] = Field(..., description="Expected output result")
    function_type: FunctionType = Field(FunctionType.INT, description="Function return type")
    compiler_settings: Optional[CompilerSettings] = Field(None, description="Compiler configuration")
    resource_limits: Optional[ResourceLimits] = Field(None, description="Resource constraints")
    show_logs: Optional[bool] = Field(False, description="Whether to show detailed logs")
    
    @field_validator('user_code')
    @classmethod
    def validate_user_code(cls, v):
        """Validate user code"""
        if not v.strip():
            raise ValueError("User code cannot be empty")
        
        # Basic security check
        dangerous_keywords = ['system', 'exec', 'fork', 'eval']
        for keyword in dangerous_keywords:
            if keyword in v.lower():
                raise ValueError(f"Code contains unsafe keyword: {keyword}")
        
        return v

    @field_validator('expected')
    @classmethod
    def validate_expected(cls, v):
        """Validate expected results"""
        if not v:
            raise ValueError("Expected result cannot be empty")
        return v


class ExecutionMetrics(BaseModel):
    """Execution metrics"""
    total_execution_time: Optional[float] = Field(None, description="Total execution time (seconds)")
    compile_execution_time: Optional[float] = Field(None, description="Compilation time (seconds)")
    test_execution_time: Optional[float] = Field(None, description="Test execution time (seconds)")
    time_ms: Optional[float] = Field(None, description="Program execution time (milliseconds)")
    compile_time_ms: Optional[float] = Field(None, description="Compilation time (milliseconds)")
    cpu_utime: Optional[float] = Field(None, description="User mode CPU time")
    cpu_stime: Optional[float] = Field(None, description="Kernel mode CPU time")
    maxrss_mb: Optional[float] = Field(None, description="Maximum memory usage (MB)")


class JudgeResponse(BaseModel):
    """Judge evaluation response"""
    status: JudgeStatus = Field(..., description="Judge evaluation status")
    message: Optional[str] = Field(None, description="Status message")
    match: Optional[bool] = Field(None, description="Whether result matches expected")
    
    # Execution output
    stdout: Optional[str] = Field(None, description="Standard output")
    stderr: Optional[str] = Field(None, description="Standard error output")
    compile_output: Optional[str] = Field(None, description="Compilation output")
    
    # Result comparison
    expected: Optional[Dict[str, Any]] = Field(None, description="Expected result")
    actual: Optional[Dict[str, Any]] = Field(None, description="Actual result")
    
    # Execution metrics
    metrics: Optional[ExecutionMetrics] = Field(None, description="Execution metrics")
    
    # Error information
    exit_code: Optional[int] = Field(None, description="Program exit code")
    error_details: Optional[str] = Field(None, description="Error details")


class BatchJudgeRequest(BaseModel):
    """Batch judge evaluation request"""
    tests: List[JudgeRequest] = Field(..., description="Test list", min_length=1, max_length=100)
    show_progress: Optional[bool] = Field(True, description="Whether to show progress")


class OptimizedBatchJudgeRequest(BaseModel):
    """Optimized batch judge evaluation request for same language and user code with different test configurations"""
    language: LanguageType = Field(..., description="Programming language")
    user_code: str = Field(..., description="User source code", min_length=1, max_length=50000)
    configs: List[Dict[str, Any]] = Field(..., description="List of test configurations", min_length=1, max_length=100)
    compiler_settings: Optional[CompilerSettings] = Field(None, description="Compiler settings")
    resource_limits: Optional[ResourceLimits] = Field(None, description="Resource limits")
    show_progress: Optional[bool] = Field(True, description="Whether to show progress")

    @field_validator('user_code')
    @classmethod
    def validate_user_code(cls, v):
        """Validate user code for safety"""
        dangerous_patterns = [
            'system(', 'exec(', 'popen(', 'fork()', 'exit(',
            '#include <sys/', 'unistd.h', 'signal.h',
            'remove(', 'rename(', 'rmdir(', 'unlink(',
            'chmod(', 'chown(', 'kill(', 'abort()',
            '/dev/', '/proc/', '/sys/', '/etc/',
            'sudo', 'su ', 'passwd'
        ]
        
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError(f"Dangerous code pattern detected: {pattern}")
        
        return v


class BatchJudgeResponse(BaseModel):
    """Batch judge evaluation response"""
    results: List[JudgeResponse] = Field(..., description="Judge evaluation result list")
    summary: Dict[str, Any] = Field(..., description="Judge evaluation summary")


# Example data
class JudgeExamples:
    """API usage examples"""
    
    @staticmethod
    def get_c_example() -> Dict[str, Any]:
        """C language judge evaluation example"""
        return {
            "language": "c",
            "user_code": '''#include <stdio.h>

int solve(int *a, int *b) {
    *a = *a * 2;      // 3 * 2 = 6
    *b = *b * 2 + 1;  // 4 * 2 + 1 = 9
    printf("Hello from C user code!\\n");
    return 0;
}''',
            "solve_params": [
                {"name": "a", "type": "int", "input_value": 3},
                {"name": "b", "type": "int", "input_value": 4}
            ],
            "expected": {"a": 6, "b": 9},
            "function_type": "int",
            "compiler_settings": {
                "standard": "c11",
                "flags": "-Wall -Wextra -O2"
            },
            "resource_limits": {
                "compile_timeout": 30,
                "execution_timeout": 10
            }
        }
    
    @staticmethod
    def get_cpp_example() -> Dict[str, Any]:
        """C++ language judge evaluation example"""
        return {
            "language": "cpp",
            "user_code": '''#include <iostream>

int solve(int &a, int &b) {
    a = a * 2;      // 3 * 2 = 6
    b = b * 2 + 1;  // 4 * 2 + 1 = 9
    std::cout << "Hello from C++ user code!" << std::endl;
    return 0;
}''',
            "solve_params": [
                {"name": "a", "type": "int", "input_value": 3},
                {"name": "b", "type": "int", "input_value": 4}
            ],
            "expected": {"a": 6, "b": 9},
            "function_type": "int",
            "compiler_settings": {
                "standard": "cpp20",
                "flags": "-Wall -Wextra -O2 -std=c++20"
            },
            "resource_limits": {
                "compile_timeout": 30,
                "execution_timeout": 10
            }
        }

    @staticmethod
    def get_advanced_cpp_example() -> Dict[str, Any]:
        """C++ advanced example (using vectors and complex data structures)"""
        return {
            "language": "cpp",
            "user_code": '''#include <vector>
#include <iostream>

int solve(std::vector<int> &nums, int &target) {
    int sum = 0;
    for (int i = 0; i < nums.size(); i++) {
        if (nums[i] < target) {
            sum += nums[i];
            nums[i] *= 2;  // Modify original array
        }
    }
    target = sum;
    return sum > 10 ? 1 : 0;
}''',
            "solve_params": [
                {"name": "nums", "type": "array_int", "input_value": [1, 5, 3, 8, 2]},
                {"name": "target", "type": "int", "input_value": 6}
            ],
            "expected": {
                "nums": [2, 5, 6, 8, 4],
                "target": 11,
                "return_value": 1
            },
            "function_type": "int",
            "compiler_settings": {
                "standard": "cpp17",
                "flags": "-Wall -Wextra -O2 -std=c++17"
            }
        }

    @staticmethod
    def get_response_example() -> Dict[str, Any]:
        """Successful response example"""
        return {
            "status": "SUCCESS",
            "message": "Judge evaluation completed",
            "match": True,
            "stdout": "Hello from C++ user code!\nInput: a=3, b=4\nOutput: a=6, b=9\nRESULT_START\na:6\nb:9\nreturn_value:0\nRESULT_END\n",
            "stderr": "",
            "expected": {"a": 6, "b": 9},
            "actual": {"a": 6, "b": 9, "return_value": 0},
            "metrics": {
                "total_execution_time": 0.523,
                "compile_execution_time": 0.160,
                "test_execution_time": 0.004,
                "time_ms": 3.91,
                "compile_time_ms": 159.85,
                "cpu_utime": 0.000088,
                "cpu_stime": 0.000176,
                "maxrss_mb": 2.56
            }
        }

    @staticmethod
    def get_error_example() -> Dict[str, Any]:
        """Compilation error example"""
        return {
            "status": "COMPILE_ERROR",
            "message": "Compilation failed",
            "match": False,
            "compile_output": "error: expected ';' before '}' token",
            "metrics": {
                "total_execution_time": 0.234,
                "compile_execution_time": 0.234
            },
            "error_details": "Syntax error: missing semicolon"
        }

    @staticmethod
    def get_optimized_batch_example() -> Dict[str, Any]:
        """Optimized batch evaluation example"""
        return {
            "language": "c",
            "user_code": '''#include <stdio.h>
int solve(int *a, int *b) {
    *a = *a * 2;
    *b = *b * 2 + 1;
    printf("Test case: a=%d, b=%d\\n", *a, *b);
    return 0;
}''',
            "configs": [
                {
                    "solve_params": [
                        {"name": "a", "type": "int", "input_value": 3},
                        {"name": "b", "type": "int", "input_value": 4}
                    ],
                    "expected": {"a": 6, "b": 9},
                    "function_type": "int"
                },
                {
                    "solve_params": [
                        {"name": "a", "type": "int", "input_value": 5},
                        {"name": "b", "type": "int", "input_value": 10}
                    ],
                    "expected": {"a": 10, "b": 21},
                    "function_type": "int"
                },
                {
                    "solve_params": [
                        {"name": "a", "type": "int", "input_value": 1},
                        {"name": "b", "type": "int", "input_value": 2}
                    ],
                    "expected": {"a": 2, "b": 5},
                    "function_type": "int"
                }
            ],
            "compiler_settings": {
                "standard": "c11",
                "flags": "-Wall -Wextra -O2"
            },
            "resource_limits": {
                "compile_timeout": 30,
                "execution_timeout": 10
            },
            "show_progress": True
        }
