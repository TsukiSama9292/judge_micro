# Judge Microservice API Design Documentation

## Overview

The Judge Microservice API provides a complete code evaluation service that supports C and C++ language code compilation, execution, and result verification.

## API Endpoints

### Basic Endpoints

- `GET /` - Health check
- `GET /judge/status` - Service status
- `GET /judge/languages` - Supported languages list
- `GET /judge/limits` - Resource limits information

### Evaluation Endpoints

- `POST /judge/submit` - Submit single evaluation
- `POST /judge/batch` - Batch evaluation
- `POST /judge/batch/optimized` - Optimized batch evaluation for same code with different test configurations

### Example Endpoints

- `GET /judge/examples/c` - C language examples
- `GET /judge/examples/cpp` - C++ language examples
- `GET /judge/examples/advanced` - Advanced examples
- `GET /judge/examples/error` - Error examples
- `GET /judge/examples/optimized-batch` - Optimized batch evaluation examples

## Data Models

### Request Format (JudgeRequest)

```json
{
  "language": "c|cpp",
  "user_code": "string",
  "solve_params": [
    {
      "name": "string",
      "type": "int|float|double|char|string|array_int|array_float|array_char",
      "input_value": "any"
    }
  ],
  "expected": {
    "key": "value"
  },
  "function_type": "int|float|double|char|string|void",
  "compiler_settings": {
    "standard": "c11|cpp20|...",
    "flags": "string",
    "optimization_level": "string"
  },
  "resource_limits": {
    "compile_timeout": 30,
    "execution_timeout": 10,
    "memory_limit": "128m",
    "cpu_limit": 1.0
  },
  "show_logs": false
}
```

### Response Format (JudgeResponse)

```json
{
  "status": "SUCCESS|COMPILE_ERROR|TIMEOUT|ERROR",
  "message": "string",
  "match": true,
  "stdout": "string",
  "stderr": "string",
  "compile_output": "string",
  "expected": {
    "key": "value"
  },
  "actual": {
    "key": "value"
  },
  "metrics": {
    "total_execution_time": 0.523,
    "compile_execution_time": 0.160,
    "test_execution_time": 0.004,
    "time_ms": 3.91,
    "compile_time_ms": 159.85,
    "cpu_utime": 0.000088,
    "cpu_stime": 0.000176,
    "maxrss_mb": 2.56
  },
  "exit_code": 0,
  "error_details": "string"
}
```

## Usage Examples

### 1. Basic C Language Example

**Request:**
```json
{
  "language": "c",
  "user_code": "#include <stdio.h>\n\nint solve(int *a, int *b) {\n    *a = *a * 2;\n    *b = *b * 2 + 1;\n    printf(\"Hello from C!\\n\");\n    return 0;\n}",
  "solve_params": [
    {"name": "a", "type": "int", "input_value": 3},
    {"name": "b", "type": "int", "input_value": 4}
  ],
  "expected": {"a": 6, "b": 9},
  "function_type": "int"
}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "match": true,
  "stdout": "Hello from C!\nInput: a=3, b=4\nOutput: a=6, b=9\n...",
  "expected": {"a": 6, "b": 9},
  "actual": {"a": 6, "b": 9, "return_value": 0},
  "metrics": {
    "total_execution_time": 0.523,
    "compile_execution_time": 0.160,
    "test_execution_time": 0.004
  }
}
```

### 2. C++ Language Example

**Request:**
```json
{
  "language": "cpp",
  "user_code": "#include <iostream>\n\nint solve(int &a, int &b) {\n    a = a * 2;\n    b = b * 2 + 1;\n    std::cout << \"Hello from C++!\" << std::endl;\n    return 0;\n}",
  "solve_params": [
    {"name": "a", "type": "int", "input_value": 3},
    {"name": "b", "type": "int", "input_value": 4}
  ],
  "expected": {"a": 6, "b": 9},
  "function_type": "int",
  "compiler_settings": {
    "standard": "cpp20",
    "flags": "-Wall -Wextra -O2 -std=c++20"
  }
}
```

### 3. Advanced C++ Example (Vector Operations)

**Request:**
```json
{
  "language": "cpp",
  "user_code": "#include <vector>\n#include <iostream>\n\nint solve(std::vector<int> &nums, int &target) {\n    int sum = 0;\n    for (int i = 0; i < nums.size(); i++) {\n        if (nums[i] < target) {\n            sum += nums[i];\n            nums[i] *= 2;\n        }\n    }\n    target = sum;\n    return sum > 10 ? 1 : 0;\n}",
  "solve_params": [
    {"name": "nums", "type": "array_int", "input_value": [1, 5, 3, 8, 2]},
    {"name": "target", "type": "int", "input_value": 6}
  ],
  "expected": {
    "nums": [2, 5, 6, 8, 4],
    "target": 11,
    "return_value": 1
  },
  "function_type": "int"
}
```

### 4. Batch Evaluation Example

**Request:**
```json
{
  "tests": [
    {
      "language": "c",
      "user_code": "int solve(int *a) { *a = 10; return 0; }",
      "solve_params": [{"name": "a", "type": "int", "input_value": 1}],
      "expected": {"a": 10},
      "function_type": "int"
    },
    {
      "language": "cpp",
      "user_code": "int solve(int &a) { a = 20; return 0; }",
      "solve_params": [{"name": "a", "type": "int", "input_value": 1}],
      "expected": {"a": 20},
      "function_type": "int"
    }
  ],
  "show_progress": true
}
```

**Response:**
```json
{
  "results": [
    {
      "status": "SUCCESS",
      "match": true,
      "actual": {"a": 10, "return_value": 0}
    },
    {
      "status": "SUCCESS", 
      "match": true,
      "actual": {"a": 20, "return_value": 0}
    }
  ],
  "summary": {
    "total_tests": 2,
    "success_count": 2,
    "error_count": 0,
    "success_rate": 1.0,
    "total_execution_time": 1.234,
    "average_time_per_test": 0.617
  }
}
```

## Optimized Batch Evaluation

### Overview

The optimized batch evaluation endpoint (`POST /judge/batch/optimized`) is designed for scenarios where you need to test the same user code against multiple test configurations without recompiling. This is significantly more efficient than regular batch evaluation when testing the same code with different input data.

### Key Features

- **Single Compilation**: Compiles the user code only once
- **Multiple Test Configurations**: Runs the compiled binary against different test data
- **Efficient Resource Usage**: Reuses the same container and compiled binary
- **Error Propagation**: Compilation errors affect all test configurations
- **Individual Test Handling**: Runtime errors are handled per test configuration

### Use Cases

- **Algorithm Testing**: Test the same algorithm implementation with multiple test cases
- **Performance Benchmarking**: Run the same code with different input sizes
- **Edge Case Testing**: Test corner cases without recompilation overhead
- **Contest Judging**: Efficiently evaluate submissions against multiple test datasets

### Request Format (OptimizedBatchJudgeRequest)

```json
{
  "language": "c|cpp",
  "user_code": "string",
  "configs": [
    {
      "solve_params": [
        {
          "name": "string",
          "type": "int|float|double|char|string|array_int|array_float|array_char",
          "input_value": "any"
        }
      ],
      "expected": {
        "key": "value"
      },
      "function_type": "int|float|double|char|string|void"
    }
  ],
  "compiler_settings": {
    "standard": "c11|cpp20|...",
    "flags": "string"
  },
  "resource_limits": {
    "compile_timeout": 30,
    "execution_timeout": 10
  },
  "show_progress": true
}
```

### Response Format

The response follows the same format as regular batch evaluation but includes additional metadata about the optimization:

```json
{
  "results": [
    {
      "status": "SUCCESS|COMPILE_ERROR|TIMEOUT|ERROR",
      "message": "string",
      "match": true,
      "config_index": 0,
      "metrics": {
        "compile_execution_time": 0.160,
        "test_execution_time": 0.004
      }
    }
  ],
  "summary": {
    "total_tests": 3,
    "success_count": 3,
    "error_count": 0,
    "success_rate": 1.0,
    "total_execution_time": 0.523,
    "average_time_per_test": 0.174,
    "optimization_note": "Used optimized batch execution with single compilation",
    "compile_once": true
  }
}
```

### Performance Benefits

Compared to regular batch evaluation:
- **Compilation Time**: Saved for all tests after the first one
- **Container Overhead**: Reduced by reusing the same container
- **Memory Usage**: More efficient memory utilization
- **Total Time**: Significantly faster for multiple test scenarios

### Error Handling

- **Compilation Errors**: If compilation fails, all test configurations will receive the same compilation error
- **Runtime Errors**: Each test configuration is handled individually
- **Timeouts**: Compilation timeout affects all tests; execution timeout is per test configuration

## Supported Language Standards

### C Language Standards
- `c89` - C89/C90 standard
- `c99` - C99 standard
- `c11` - C11 standard
- `c17` - C17 standard
- `c23` - C23 standard

### C++ Language Standards
- `cpp98` - C++98 standard
- `cpp03` - C++03 standard
- `cpp11` - C++11 standard
- `cpp14` - C++14 standard
- `cpp17` - C++17 standard
- `cpp20` - C++20 standard
- `cpp23` - C++23 standard

## Supported Parameter Types

- `int` - Integer
- `float` - Single precision floating point
- `double` - Double precision floating point
- `char` - Character
- `string` - String
- `array_int` - Integer array
- `array_float` - Floating point array
- `array_char` - Character array

## Status Codes

- `SUCCESS` - Execution successful
- `COMPILE_ERROR` - Compilation error
- `COMPILE_TIMEOUT` - Compilation timeout
- `RUNTIME_ERROR` - Runtime error
- `TIMEOUT` - Execution timeout
- `TIMEOUT_ERROR` - Timeout handling error
- `ERROR` - General error

## Resource Limits

### Default Limits
- Compilation time: 30 seconds
- Execution time: 10 seconds
- Memory limit: 128MB
- CPU limit: 1.0 core

### Maximum Limits
- Compilation time: 300 seconds
- Execution time: 60 seconds
- Memory limit: 1GB
- CPU limit: 4.0 cores

### Code Limits
- Maximum code length: 50,000 characters
- Maximum batch test count: 100

## Security Features

1. **Code Safety Check**: Automatic detection of dangerous function calls
2. **Resource Isolation**: Docker container isolation for execution environment
3. **Network Isolation**: No network access in execution environment
4. **Time Limits**: Strict compilation and execution time limits
5. **Memory Limits**: Prevent memory leaks and excessive usage

## Error Handling

The API provides detailed error information, including:
- Specific location and reason for compilation errors
- Stack traces for runtime errors
- Detailed timeout error descriptions
- Resource usage statistics

## Performance Metrics

Each evaluation returns detailed performance metrics:
- Total execution time
- Compilation time
- Test execution time
- CPU usage time
- Peak memory usage

## API Usage Limits

1. Request rate limits (configurable)
2. Concurrent request count limits
3. Code length limits
4. Batch evaluation count limits

## Development and Testing

Using FastAPI's automatic documentation features:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI Schema: `/openapi.json`
