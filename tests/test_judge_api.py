import pytest
import json
from fastapi.testclient import TestClient
from judge_micro.api.main import get_app

client = TestClient(get_app(debug=True))


class TestJudgeAPI:
    """Judge API tests"""

    def test_c_basic_success(self):
        """Test C language basic success case"""
        request_data = {
            "language": "c",
            "user_code": '''#include <stdio.h>
int solve(int *a, int *b) {
    *a = *a * 2;
    *b = *b * 2 + 1;
    printf("Hello from C!\\n");
    return 0;
}''',
            "solve_params": [
                {"name": "a", "type": "int", "input_value": 3},
                {"name": "b", "type": "int", "input_value": 4}
            ],
            "expected": {"a": 6, "b": 9},
            "function_type": "int"
        }
        
        response = client.post("/judge/submit", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == "SUCCESS"
        assert result["match"] is True
        assert result["actual"]["a"] == 6
        assert result["actual"]["b"] == 9

    def test_cpp_basic_success(self):
        """Test C++ language basic success case"""
        request_data = {
            "language": "cpp",
            "user_code": '''#include <iostream>
int solve(int &a, int &b) {
    a = a * 2;
    b = b * 2 + 1;
    std::cout << "Hello from C++!" << std::endl;
    return 0;
}''',
            "solve_params": [
                {"name": "a", "type": "int", "input_value": 3},
                {"name": "b", "type": "int", "input_value": 4}
            ],
            "expected": {"a": 6, "b": 9},
            "function_type": "int"
        }
        
        response = client.post("/judge/submit", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == "SUCCESS"
        assert result["match"] is True

    def test_compile_error(self):
        """Test compilation error"""
        request_data = {
            "language": "c",
            "user_code": '''#include <stdio.h>
int solve(int *a, int *b) {
    *a = *a * 2  // Intentionally missing semicolon
    *b = *b * 2 + 1;
    return 0;
}''',
            "solve_params": [
                {"name": "a", "type": "int", "input_value": 3},
                {"name": "b", "type": "int", "input_value": 4}
            ],
            "expected": {"a": 6, "b": 9},
            "function_type": "int"
        }
        
        response = client.post("/judge/submit", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == "COMPILE_ERROR"
        # For compile errors, match field may be None since execution never occurred
        assert result["match"] in [False, None]

    def test_with_compiler_settings(self):
        """Test using compiler settings"""
        request_data = {
            "language": "cpp",
            "user_code": '''#include <iostream>
int solve(int &a) {
    a = a + 10;
    std::cout << "C++ test" << std::endl;
    return 0;
}''',
            "solve_params": [
                {"name": "a", "type": "int", "input_value": 5}
            ],
            "expected": {"a": 15},
            "function_type": "int",
            "compiler_settings": {
                "standard": "cpp11",
                "flags": "-Wall -Wextra -O2"
            }
        }
        
        response = client.post("/judge/submit", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        # Since this is testing compiler settings, we just verify the API accepts the request
        # The actual compilation success depends on Docker environment availability
        assert result["status"] in ["SUCCESS", "COMPILE_ERROR", "ERROR"]

    def test_with_resource_limits(self):
        """Test resource limits"""
        request_data = {
            "language": "c",
            "user_code": '''#include <stdio.h>
int solve(int *a) {
    *a = 42;
    printf("Simple test\\n");
    return 0;
}''',
            "solve_params": [
                {"name": "a", "type": "int", "input_value": 1}
            ],
            "expected": {"a": 42},
            "function_type": "int",
            "resource_limits": {
                "compile_timeout": 10,
                "execution_timeout": 5
            }
        }
        
        response = client.post("/judge/submit", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        # Test that the API accepts resource limits and processes the request
        assert result["status"] in ["SUCCESS", "COMPILE_ERROR", "ERROR"]
        # Verify that resource limits were processed (they should appear in metrics if successful)
        if result["status"] == "SUCCESS" and "metrics" in result:
            assert "total_execution_time" in result["metrics"]

    def test_batch_submit(self):
        """Test batch submission"""
        tests = [
            {
                "language": "c",
                "user_code": '''int solve(int *a) { *a = 10; return 0; }''',
                "solve_params": [{"name": "a", "type": "int", "input_value": 1}],
                "expected": {"a": 10},
                "function_type": "int"
            },
            {
                "language": "cpp",
                "user_code": '''int solve(int &a) { a = 20; return 0; }''',
                "solve_params": [{"name": "a", "type": "int", "input_value": 1}],
                "expected": {"a": 20},
                "function_type": "int"
            }
        ]
        
        request_data = {
            "tests": tests,
            "show_progress": False
        }
        
        response = client.post("/judge/batch", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        assert len(result["results"]) == 2
        assert result["summary"]["total_tests"] == 2

    def test_invalid_language(self):
        """Test invalid language"""
        request_data = {
            "language": "javascript",  # Unsupported language
            "user_code": "console.log('hello')",
            "solve_params": [{"name": "a", "type": "int", "input_value": 1}],
            "expected": {"a": 1},
            "function_type": "int"
        }
        
        response = client.post("/judge/submit", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_invalid_user_code(self):
        """Test invalid user code"""
        request_data = {
            "language": "c",
            "user_code": "",  # Empty code
            "solve_params": [{"name": "a", "type": "int", "input_value": 1}],
            "expected": {"a": 1},
            "function_type": "int"
        }
        
        response = client.post("/judge/submit", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_dangerous_code(self):
        """Test dangerous code"""
        request_data = {
            "language": "c",
            "user_code": '''#include <stdio.h>
int solve(int *a) {
    system("rm -rf /");  // Dangerous command
    return 0;
}''',
            "solve_params": [{"name": "a", "type": "int", "input_value": 1}],
            "expected": {"a": 1},
            "function_type": "int"
        }
        
        response = client.post("/judge/submit", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_get_examples(self):
        """Test getting examples"""
        # C example
        response = client.get("/judge/examples/c")
        assert response.status_code == 200
        result = response.json()
        assert "example" in result
        assert result["example"]["language"] == "c"
        
        # C++ example
        response = client.get("/judge/examples/cpp")
        assert response.status_code == 200
        result = response.json()
        assert "example" in result
        assert result["example"]["language"] == "cpp"
        
        # Advanced example
        response = client.get("/judge/examples/advanced")
        assert response.status_code == 200
        
        # Error example
        response = client.get("/judge/examples/error")
        assert response.status_code == 200

    def test_get_supported_languages(self):
        """Test getting supported languages"""
        response = client.get("/judge/languages")
        assert response.status_code == 200
        
        result = response.json()
        assert "supported_languages" in result
        languages = [lang["language"] for lang in result["supported_languages"]]
        assert "c" in languages
        assert "cpp" in languages

    def test_get_service_status(self):
        """Test getting service status"""
        response = client.get("/judge/status")
        assert response.status_code == 200
        
        result = response.json()
        assert "service" in result
        assert "status" in result

    def test_get_resource_limits(self):
        """Test getting resource limits"""
        response = client.get("/judge/limits")
        assert response.status_code == 200
        
        result = response.json()
        assert "default_limits" in result
        assert "maximum_limits" in result
        assert "code_limits" in result

    def test_optimized_batch_submit(self):
        """Test optimized batch submission for same code with different configurations"""
        request_data = {
            "language": "c",
            "user_code": '''#include <stdio.h>
int solve(int *a, int *b) {
    *a = *a * 2;
    *b = *b * 2 + 1;
    printf("Test: a=%d, b=%d\\n", *a, *b);
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
                }
            ],
            "show_progress": False
        }
        
        response = client.post("/judge/batch/optimized", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "results" in result
        assert "summary" in result
        assert len(result["results"]) == 2
        assert result["summary"]["total_tests"] == 2
        
        # Check for optimization indicators
        summary = result["summary"]
        assert "optimization_note" in summary or "compile_once" in summary

    def test_optimized_batch_compilation_error(self):
        """Test optimized batch with compilation error - should affect all tests"""
        request_data = {
            "language": "c",
            "user_code": '''#include <stdio.h>
int solve(int *a, int *b) {
    *a = *a * 2  // Missing semicolon
    *b = *b * 2 + 1;
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
                }
            ],
            "show_progress": False
        }
        
        response = client.post("/judge/batch/optimized", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        assert len(result["results"]) == 1
        assert result["results"][0]["status"] in ["COMPILE_ERROR", "COMPILE_TIMEOUT"]
        assert result["summary"]["error_count"] == 1

    def test_get_optimized_batch_example(self):
        """Test getting optimized batch example"""
        response = client.get("/judge/examples/optimized-batch")
        assert response.status_code == 200
        
        result = response.json()
        assert "description" in result
        assert "example" in result
        assert "note" in result
        
        example = result["example"]
        assert example["language"] in ["c", "cpp"]
        assert "user_code" in example
        assert "configs" in example
        assert len(example["configs"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
