import pytest
from fastapi.testclient import TestClient
from judge_micro.api.main import get_app

client = TestClient(get_app(debug=True))


class TestCLanguage:
    """C language tests - both API and service level"""

    def test_c_service_basic(self):
        """Test C language using service directly"""
        from judge_micro.services.micro import judge_micro
        efficient_c_code = '''#include <stdio.h>

int solve(int *a, int *b) {
    *a = *a * 2;      // 3 * 2 = 6
    *b = *b * 2 + 1;  // 4 * 2 + 1 = 9
    printf("Hello from C user code!\\n");
    return 0;
}'''

        solve_params_test = [
            {"name": "a", "type": "int", "input_value": 3},
            {"name": "b", "type": "int", "input_value": 4}
        ]

        expected_test = {"a": 6, "b": 9}

        config = {
            "solve_params": solve_params_test,
            "expected": expected_test,
            "function_type": "int"
        }

        result_c_efficient = judge_micro.run_microservice(
            language='c',
            user_code=efficient_c_code,
            config=config,
            show_logs=True
        )
        print("C result:\n", result_c_efficient)
        assert result_c_efficient.get('status').lower() == 'success'
        assert result_c_efficient.get('match') == True

    def test_c_api_basic_success(self):
        """Test C language basic success case via API"""
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

    def test_c_compile_error(self):
        """Test C compilation error"""
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

    def test_c_with_resource_limits(self):
        """Test C with resource limits"""
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

    def test_c_dangerous_code(self):
        """Test C dangerous code detection"""
        request_data = {
            "language": "c",
            "user_code": '''#include <stdio.h>
int solve(int *a) {
    system("rm -rf /");  // Dangerous command
    return 0;
}''',
            "solve_params": [
                {"name": "a", "type": "int", "input_value": 1}
            ],
            "expected": {"a": 1},
            "function_type": "int"
        }
        
        response = client.post("/judge/submit", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_c_invalid_user_code(self):
        """Test C invalid user code"""
        request_data = {
            "language": "c",
            "user_code": "",  # Empty code
            "solve_params": [
                {"name": "a", "type": "int", "input_value": 1}
            ],
            "expected": {"a": 1},
            "function_type": "int"
        }
        
        response = client.post("/judge/submit", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_c_batch_submit(self):
        """Test C batch submission"""
        tests = [
            {
                "language": "c",
                "user_code": '''int solve(int *a) { *a = 10; return 0; }''',
                "solve_params": [{"name": "a", "type": "int", "input_value": 1}],
                "expected": {"a": 10},
                "function_type": "int"
            },
            {
                "language": "c",
                "user_code": '''int solve(int *a) { *a = 20; return 0; }''',
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

    def test_c_optimized_batch_submit(self):
        """Test C optimized batch submission for same code with different configurations"""
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

    def test_c_optimized_batch_compilation_error(self):
        """Test C optimized batch with compilation error - should affect all tests"""
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])