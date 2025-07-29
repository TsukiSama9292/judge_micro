"""
Judge Microservice Python SDK

This SDK provides a simple and easy-to-use interface for interacting with the Judge Microservice API.
"""

import requests
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
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


@dataclass
class SolveParameter:
    """Solve function parameter"""
    name: str
    type: ParameterType
    input_value: Union[int, float, str, List[Union[int, float, str]]]


@dataclass
class CompilerSettings:
    """Compiler configuration"""
    standard: Optional[str] = None
    flags: Optional[str] = "-Wall -Wextra -O2"
    optimization_level: Optional[str] = "O2"


@dataclass
class ResourceLimits:
    """Resource constraints"""
    compile_timeout: Optional[int] = 30
    execution_timeout: Optional[int] = 10
    memory_limit: Optional[str] = "128m"
    cpu_limit: Optional[float] = 1.0


@dataclass
class JudgeRequest:
    """Judge evaluation request"""
    language: LanguageType
    user_code: str
    solve_params: List[SolveParameter]
    expected: Dict[str, Any]
    function_type: str = "int"
    compiler_settings: Optional[CompilerSettings] = None
    resource_limits: Optional[ResourceLimits] = None
    show_logs: bool = False


class JudgeSDK:
    """Judge Microservice SDK client"""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 300):
        """
        Initialize SDK client
        
        Args:
            base_url: API server base URL
            timeout: Request timeout (seconds)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
    def submit_code(self, request: JudgeRequest) -> Dict[str, Any]:
        """
        Submit code for judge evaluation
        
        Args:
            request: Judge evaluation request object
            
        Returns:
            Judge evaluation result dictionary
            
        Raises:
            requests.RequestException: Network request error
            ValueError: API response error
        """
        url = f"{self.base_url}/judge/submit"
        
        # Convert to dictionary format
        data = asdict(request)
        
        # Handle nested objects
        data['solve_params'] = [asdict(param) for param in request.solve_params]
        if request.compiler_settings:
            data['compiler_settings'] = asdict(request.compiler_settings)
        if request.resource_limits:
            data['resource_limits'] = asdict(request.resource_limits)
        
        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Unable to parse API response: {e}")
    
    def batch_submit(self, requests_list: List[JudgeRequest], show_progress: bool = True) -> Dict[str, Any]:
        """
        Submit batch code evaluation
        
        Args:
            requests_list: Judge evaluation request list
            show_progress: Whether to show progress
            
        Returns:
            Batch judge evaluation result dictionary
        """
        url = f"{self.base_url}/judge/batch"
        
        tests = []
        for req in requests_list:
            data = asdict(req)
            data['solve_params'] = [asdict(param) for param in req.solve_params]
            if req.compiler_settings:
                data['compiler_settings'] = asdict(req.compiler_settings)
            if req.resource_limits:
                data['resource_limits'] = asdict(req.resource_limits)
            tests.append(data)
        
        batch_data = {
            "tests": tests,
            "show_progress": show_progress
        }
        
        try:
            response = self.session.post(url, json=batch_data, timeout=self.timeout * len(requests_list))
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"Batch judge evaluation request failed: {e}")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        url = f"{self.base_url}/judge/status"
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Get supported languages list"""
        url = f"{self.base_url}/judge/languages"
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def get_resource_limits(self) -> Dict[str, Any]:
        """Get resource limits information"""
        url = f"{self.base_url}/judge/limits"
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def get_examples(self, language: str = None) -> Dict[str, Any]:
        """
        Get usage examples
        
        Args:
            language: Language type ('c', 'cpp', 'advanced', 'error')
        """
        if language is None:
            language = 'c'
        
        url = f"{self.base_url}/judge/examples/{language}"
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return response.json()


class JudgeSDKHelper:
    """SDK helper utility class"""
    
    @staticmethod
    def create_c_request(
        user_code: str,
        params: List[Dict[str, Any]],
        expected: Dict[str, Any],
        standard: str = "c11"
    ) -> JudgeRequest:
        """
        Create C language judge evaluation request
        
        Args:
            user_code: User code
            params: Parameter list, format: [{"name": "a", "type": "int", "value": 3}]
            expected: Expected result
            standard: C language standard
        """
        solve_params = [
            SolveParameter(
                name=p["name"],
                type=ParameterType(p["type"]),
                input_value=p["value"]
            )
            for p in params
        ]
        
        compiler_settings = CompilerSettings(
            standard=standard,
            flags=f"-Wall -Wextra -O2 -std={standard}"
        )
        
        return JudgeRequest(
            language=LanguageType.C,
            user_code=user_code,
            solve_params=solve_params,
            expected=expected,
            compiler_settings=compiler_settings
        )
    
    @staticmethod
    def create_cpp_request(
        user_code: str,
        params: List[Dict[str, Any]],
        expected: Dict[str, Any],
        standard: str = "cpp17"
    ) -> JudgeRequest:
        """
        Create C++ language judge evaluation request
        
        Args:
            user_code: User code
            params: Parameter list
            expected: Expected result
            standard: C++ language standard
        """
        solve_params = [
            SolveParameter(
                name=p["name"],
                type=ParameterType(p["type"]),
                input_value=p["value"]
            )
            for p in params
        ]
        
        compiler_settings = CompilerSettings(
            standard=standard,
            flags=f"-Wall -Wextra -O2 -std={standard}"
        )
        
        return JudgeRequest(
            language=LanguageType.CPP,
            user_code=user_code,
            solve_params=solve_params,
            expected=expected,
            compiler_settings=compiler_settings
        )


# Usage examples
def example_usage():
    """SDK usage examples"""
    
    # Initialize SDK
    sdk = JudgeSDK(base_url="http://localhost:8000")
    
    # Check service status
    print("Checking service status...")
    status = sdk.get_service_status()
    print(f"Service status: {status['status']}")
    
    # C language example
    print("\n=== C Language Judge Evaluation Example ===")
    c_request = JudgeSDKHelper.create_c_request(
        user_code='''#include <stdio.h>
int solve(int *a, int *b) {
    *a = *a * 2;
    *b = *b * 2 + 1;
    printf("Hello from C!\\n");
    return 0;
}''',
        params=[
            {"name": "a", "type": "int", "value": 3},
            {"name": "b", "type": "int", "value": 4}
        ],
        expected={"a": 6, "b": 9}
    )
    
    c_result = sdk.submit_code(c_request)
    print(f"C judge evaluation result: {c_result['status']}")
    print(f"Result match: {c_result['match']}")
    
    # C++ language example
    print("\n=== C++ Language Judge Evaluation Example ===")
    cpp_request = JudgeSDKHelper.create_cpp_request(
        user_code='''#include <iostream>
int solve(int &a, int &b) {
    a = a * 2;
    b = b * 2 + 1;
    std::cout << "Hello from C++!" << std::endl;
    return 0;
}''',
        params=[
            {"name": "a", "type": "int", "value": 3},
            {"name": "b", "type": "int", "value": 4}
        ],
        expected={"a": 6, "b": 9},
        standard="cpp20"
    )
    
    cpp_result = sdk.submit_code(cpp_request)
    print(f"C++ judge evaluation result: {cpp_result['status']}")
    print(f"Result match: {cpp_result['match']}")
    
    # Batch judge evaluation example
    print("\n=== Batch Judge Evaluation Example ===")
    batch_requests = [c_request, cpp_request]
    batch_result = sdk.batch_submit(batch_requests)
    
    print(f"Batch judge evaluation completed: {batch_result['summary']['total_tests']} tests")
    print(f"Success rate: {batch_result['summary']['success_rate']:.2%}")
    
    # Get examples
    print("\n=== Get API Examples ===")
    examples = sdk.get_examples('c')
    print("C language examples retrieved")


if __name__ == "__main__":
    example_usage()
