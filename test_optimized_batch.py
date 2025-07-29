#!/usr/bin/env python3
"""
Test script for the optimized batch API functionality.
This script tests the new /judge/batch/optimized endpoint that allows running
the same code with different test configurations without recompilation.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_optimized_batch_c():
    """Test optimized batch execution for C language"""
    print("🧪 Testing optimized batch execution for C language...")
    
    # Test data - same C code with different test configurations
    test_data = {
        "language": "c",
        "user_code": '''#include <stdio.h>
int solve(int *a, int *b) {
    *a = *a * 2;
    *b = *b * 2 + 1;
    printf("Processing: a=%d, b=%d\\n", *a, *b);
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
    
    try:
        print("📤 Sending optimized batch request...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/judge/batch/optimized",
            json=test_data,
            timeout=120
        )
        
        end_time = time.time()
        total_request_time = end_time - start_time
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        
        # Display results
        print(f"📊 Request completed in {total_request_time:.3f} seconds")
        print(f"✅ Total tests: {result['summary']['total_tests']}")
        print(f"✅ Successful: {result['summary']['success_count']}")
        print(f"❌ Failed: {result['summary']['error_count']}")
        print(f"📈 Success rate: {result['summary']['success_rate']:.2%}")
        print(f"⚡ Total execution time: {result['summary']['total_execution_time']:.3f}s")
        print(f"⚡ Average time per test: {result['summary']['average_time_per_test']:.3f}s")
        
        if 'optimization_note' in result['summary']:
            print(f"🚀 {result['summary']['optimization_note']}")
        
        # Check individual test results
        print("\n📋 Individual test results:")
        for i, test_result in enumerate(result['results']):
            status_icon = "✅" if test_result['status'] == 'SUCCESS' else "❌"
            print(f"  {status_icon} Test {i+1}: {test_result['status']}")
            if test_result['status'] == 'SUCCESS':
                print(f"    Expected: {test_result['expected']}")
                print(f"    Actual: {test_result['actual']}")
                print(f"    Match: {test_result['match']}")
                if 'metrics' in test_result:
                    metrics = test_result['metrics']
                    print(f"    Execution time: {metrics.get('test_execution_time', 'N/A')}s")
            else:
                print(f"    Error: {test_result['message']}")
        
        return result['summary']['success_count'] == result['summary']['total_tests']
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_optimized_batch_cpp():
    """Test optimized batch execution for C++ language"""
    print("\n🧪 Testing optimized batch execution for C++ language...")
    
    # Test data - same C++ code with different test configurations
    test_data = {
        "language": "cpp",
        "user_code": '''#include <iostream>
int solve(int &a, int &b) {
    a = a * 3;
    b = b * 3 + 2;
    std::cout << "C++ Processing: a=" << a << ", b=" << b << std::endl;
    return 0;
}''',
        "configs": [
            {
                "solve_params": [
                    {"name": "a", "type": "int", "input_value": 2},
                    {"name": "b", "type": "int", "input_value": 3}
                ],
                "expected": {"a": 6, "b": 11},
                "function_type": "int"
            },
            {
                "solve_params": [
                    {"name": "a", "type": "int", "input_value": 4},
                    {"name": "b", "type": "int", "input_value": 5}
                ],
                "expected": {"a": 12, "b": 17},
                "function_type": "int"
            }
        ],
        "compiler_settings": {
            "standard": "cpp17",
            "flags": "-Wall -Wextra -O2"
        },
        "show_progress": True
    }
    
    try:
        print("📤 Sending C++ optimized batch request...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/judge/batch/optimized",
            json=test_data,
            timeout=120
        )
        
        end_time = time.time()
        total_request_time = end_time - start_time
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        
        # Display results
        print(f"📊 C++ Request completed in {total_request_time:.3f} seconds")
        print(f"✅ Total tests: {result['summary']['total_tests']}")
        print(f"✅ Successful: {result['summary']['success_count']}")
        print(f"❌ Failed: {result['summary']['error_count']}")
        print(f"📈 Success rate: {result['summary']['success_rate']:.2%}")
        
        return result['summary']['success_count'] == result['summary']['total_tests']
        
    except Exception as e:
        print(f"❌ C++ Test failed with exception: {e}")
        return False

def test_compilation_error():
    """Test handling of compilation errors in optimized batch"""
    print("\n🧪 Testing compilation error handling in optimized batch...")
    
    # Test data with invalid C code
    test_data = {
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
        "show_progress": True
    }
    
    try:
        print("📤 Sending request with compilation error...")
        
        response = requests.post(
            f"{BASE_URL}/judge/batch/optimized",
            json=test_data,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
        
        result = response.json()
        
        # Should get compilation error for all tests
        print(f"📊 Error handling test results:")
        print(f"✅ Total tests: {result['summary']['total_tests']}")
        print(f"❌ Failed (expected): {result['summary']['error_count']}")
        
        # Check that all tests failed with compilation error
        all_compile_errors = all(
            test_result['status'] in ['COMPILE_ERROR', 'COMPILE_TIMEOUT'] 
            for test_result in result['results']
        )
        
        if all_compile_errors:
            print("✅ Compilation error correctly propagated to all tests")
            return True
        else:
            print("❌ Expected compilation error for all tests")
            return False
        
    except Exception as e:
        print(f"❌ Error test failed with exception: {e}")
        return False

def get_optimized_batch_example():
    """Get the optimized batch example from the API"""
    print("\n📖 Getting optimized batch example...")
    
    try:
        response = requests.get(f"{BASE_URL}/judge/examples/optimized-batch")
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
        
        result = response.json()
        print("✅ Successfully retrieved optimized batch example")
        print(f"📄 Description: {result['description']}")
        print(f"📝 Note: {result.get('note', 'N/A')}")
        
        # Pretty print the example
        print("\n📋 Example request structure:")
        example = result['example']
        print(f"Language: {example['language']}")
        print(f"Code length: {len(example['user_code'])} characters")
        print(f"Number of test configurations: {len(example['configs'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to get example: {e}")
        return False

def main():
    """Run all optimized batch tests"""
    print("🚀 Judge Microservice - Optimized Batch API Test Suite")
    print("=" * 60)
    
    tests = [
        ("Get Optimized Batch Example", get_optimized_batch_example),
        ("C Language Optimized Batch", test_optimized_batch_c),
        ("C++ Language Optimized Batch", test_optimized_batch_cpp),
        ("Compilation Error Handling", test_compilation_error)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                print(f"✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All optimized batch tests passed!")
        return True
    else:
        print("❌ Some tests failed. Check the API server and try again.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
