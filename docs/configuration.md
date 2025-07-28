# Configuration Guide

## Overview

Judge MicroService uses a combination of environment variables and JSON configuration files to control execution behavior, resource limits, and test case definitions.

## Environment Configuration

The service uses environment variables that can be defined in `.env` or `.env.local` files in the project root.

### Core Settings

Create a `.env.local` file in your project root:

```bash
# Container Resource Limits
CONTAINER_CPU=1.0
CONTAINER_MEM=512m

# Docker Connection Settings
DOCKER_SSH_REMOTE=false
DOCKER_SSH_HOST=127.0.0.1
DOCKER_SSH_PORT=22
DOCKER_SSH_KEY_PATH=
DOCKER_SSH_USER=
DOCKER_SSH_PASSWORD=
```

### Environment Variables Reference

#### Resource Control

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CONTAINER_CPU` | float | `0.5` | CPU limit per container (in CPU cores) |
| `CONTAINER_MEM` | string | `128m` | Memory limit per container (e.g., `512m`, `1g`) |

**CPU Limit Details:**
- `0.5` = 50% of one CPU core
- `1.0` = 100% of one CPU core  
- `2.0` = 200% of one CPU core (requires multi-core system)

**Memory Limit Formats:**
- `128m` = 128 MB
- `512m` = 512 MB
- `1g` = 1 GB
- `2g` = 2 GB

#### Docker Connection

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DOCKER_SSH_REMOTE` | boolean | `false` | Enable remote Docker execution via SSH |
| `DOCKER_SSH_HOST` | string | `127.0.0.1` | Remote Docker host IP/hostname |
| `DOCKER_SSH_PORT` | integer | `22` | SSH port for remote connection |
| `DOCKER_SSH_KEY_PATH` | string | `""` | Path to SSH private key (preferred) |
| `DOCKER_SSH_USER` | string | `""` | SSH username |
| `DOCKER_SSH_PASSWORD` | string | `""` | SSH password (fallback option) |

### Configuration Examples

#### Local Development

```bash
# .env.local - Local development settings
CONTAINER_CPU=0.5
CONTAINER_MEM=256m
DOCKER_SSH_REMOTE=false
```

#### Production with Remote Docker

```bash
# .env.local - Production with dedicated Docker server
CONTAINER_CPU=2.0
CONTAINER_MEM=1g
DOCKER_SSH_REMOTE=true
DOCKER_SSH_HOST=docker-server.example.com
DOCKER_SSH_PORT=22
DOCKER_SSH_KEY_PATH=/path/to/ssh/key
DOCKER_SSH_USER=docker_user
```

#### High-Resource Evaluation

```bash
# .env.local - High-performance evaluation
CONTAINER_CPU=4.0
CONTAINER_MEM=2g
DOCKER_SSH_REMOTE=true
DOCKER_SSH_HOST=gpu-server.example.com
DOCKER_SSH_USER=eval_user
DOCKER_SSH_KEY_PATH=~/.ssh/eval_key
```

## Test Configuration (JSON)

Test cases are defined using JSON configuration files that specify function parameters, expected outputs, and return types.

### Basic Configuration Structure

```json
{
  "solve_params": [
    {"name": "param_name", "type": "param_type", "input_value": value}
  ],
  "expected": {"param_name": expected_value},
  "function_type": "return_type"
}
```

### Configuration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `solve_params` | array | Yes | Function parameters definition |
| `expected` | object | Yes | Expected parameter values after execution |
| `function_type` | string | Yes | Function return type |

#### Parameter Definition

Each parameter in `solve_params` contains:

| Field | Type | Description | Examples |
|-------|------|-------------|----------|
| `name` | string | Parameter name in function | `"a"`, `"numbers"`, `"text"` |
| `type` | string | Parameter data type | `"int"`, `"string"`, `"vector<int>"` |
| `input_value` | any | Initial parameter value | `42`, `"hello"`, `[1,2,3]` |

#### Expected Results

The `expected` object defines the anticipated state of parameters after function execution:

```json
"expected": {
  "input_param": "expected_value_after_execution",
  "output_param": "expected_output_value"
}
```

### Supported Data Types

#### C Language Types

| Type | Description | JSON Example |
|------|-------------|--------------|
| `int` | Integer | `42` |
| `float` | Floating point | `3.14` |
| `double` | Double precision | `2.71828` |
| `char` | Single character | `"A"` |
| `char*` | String | `"hello world"` |
| `int*` | Integer array | `[1, 2, 3, 4, 5]` |
| `bool` | Boolean | `true` or `false` |

#### C++ Language Types

| Type | Description | JSON Example |
|------|-------------|--------------|
| `int` | Integer | `42` |
| `float` | Floating point | `3.14` |
| `double` | Double precision | `2.71828` |
| `string` | String object | `"hello world"` |
| `vector<int>` | Integer vector | `[1, 2, 3, 4, 5]` |
| `vector<string>` | String vector | `["a", "b", "c"]` |
| `vector<double>` | Double vector | `[1.1, 2.2, 3.3]` |
| `bool` | Boolean | `true` or `false` |

### Configuration Examples

#### Basic C Example

```json
{
  "solve_params": [
    {"name": "a", "type": "int", "input_value": 3},
    {"name": "b", "type": "int", "input_value": 4}
  ],
  "expected": {"a": 9, "b": 16},
  "function_type": "int"
}
```

**Expected C Function:**
```c
int solve(int a, int b) {
    // Should modify a and b to be their squares
    a = a * a;  // 3 -> 9
    b = b * b;  // 4 -> 16
    return 0;   // Return type is int
}
```

#### Advanced C Example

```json
{
  "solve_params": [
    {"name": "num1", "type": "int", "input_value": 12},
    {"name": "num2", "type": "int", "input_value": 18},
    {"name": "gcd_result", "type": "int", "input_value": 0},
    {"name": "lcm_result", "type": "int", "input_value": 0}
  ],
  "expected": {
    "num1": 12,
    "num2": 18,
    "gcd_result": 6,
    "lcm_result": 36
  },
  "function_type": "int"
}
```

**Expected C Function:**
```c
int solve(int num1, int num2, int gcd_result, int lcm_result) {
    gcd_result = gcd(num1, num2);      // Calculate GCD
    lcm_result = (num1 * num2) / gcd_result;  // Calculate LCM
    return 0;
}
```

#### C++ Vector Example

```json
{
  "solve_params": [
    {"name": "numbers", "type": "vector<int>", "input_value": [1, 2, 3, 4, 5]},
    {"name": "sum", "type": "int", "input_value": 0}
  ],
  "expected": {"numbers": [2, 4, 6, 8, 10], "sum": 30},
  "function_type": "bool"
}
```

**Expected C++ Function:**
```cpp
bool solve(vector<int>& numbers, int& sum) {
    // Double each number and calculate sum
    for (int& num : numbers) {
        num *= 2;  // [1,2,3,4,5] -> [2,4,6,8,10]
        sum += num;  // sum = 2+4+6+8+10 = 30
    }
    return true;  // Return type is bool
}
```

#### C++ String Example

```json
{
  "solve_params": [
    {"name": "text", "type": "string", "input_value": "hello"},
    {"name": "length", "type": "int", "input_value": 0}
  ],
  "expected": {"text": "HELLO", "length": 5},
  "function_type": "void"
}
```

**Expected C++ Function:**
```cpp
void solve(string& text, int& length) {
    // Convert to uppercase and get length
    for (char& c : text) {
        c = toupper(c);  // "hello" -> "HELLO"
    }
    length = text.length();  // 5
}
```

#### Complex Data Structure Example

```json
{
  "solve_params": [
    {"name": "matrix", "type": "vector<vector<int>>", "input_value": [[1, 2], [3, 4]]},
    {"name": "sum", "type": "int", "input_value": 0},
    {"name": "transpose", "type": "vector<vector<int>>", "input_value": []}
  ],
  "expected": {
    "matrix": [[1, 2], [3, 4]],
    "sum": 10,
    "transpose": [[1, 3], [2, 4]]
  },
  "function_type": "void"
}
```

### Function Return Types

| Return Type | Description | Usage |
|-------------|-------------|-------|
| `void` | No return value | Modify parameters by reference |
| `int` | Integer return | Return status or computed value |
| `bool` | Boolean return | Return success/failure status |
| `float`/`double` | Numeric return | Return computed numeric result |
| `string` | String return | Return computed string result |

### Error Handling and Status Codes

The Judge MicroService harness automatically detects and reports various types of errors with specific status codes:

#### Supported Status Codes

| Status Code | Description | When It Occurs |
|-------------|-------------|----------------|
| `SUCCESS` | Code executed successfully and output matches expected | Normal successful execution |
| `COMPILE_ERROR` | Compilation failed | Syntax errors, missing headers, type mismatches |
| `RUNTIME_ERROR` | Runtime execution failed | Segmentation faults, exceptions, non-zero exit codes |
| `WRONG_ANSWER` | Execution succeeded but output doesn't match expected | Logic errors, incorrect calculations |

#### Compilation Error Detection

The harness automatically captures compilation errors:

```json
{
  "status": "COMPILE_ERROR",
  "error": "Compilation failed",
  "stderr": "error: expected ';' before '}' token",
  "exit_code": 1,
  "compile_time_ms": 234.5
}
```

#### Runtime Error Detection

Runtime errors are automatically detected:

```json
{
  "status": "RUNTIME_ERROR", 
  "error": "Execution failed",
  "stderr": "Segmentation fault (core dumped)",
  "exit_code": 139,
  "time_ms": 45.2,
  "compile_time_ms": 189.3
}
```

#### Wrong Answer Detection

Output validation is automatic when `expected` values are provided:

```json
{
  "status": "WRONG_ANSWER",
  "expected": {"a": 6, "b": 9},
  "actual": {"a": 6, "b": 8},
  "match": false,
  "stdout": "Debug output from user code",
  "time_ms": 12.4
}
```

### Best Practices

#### 1. Parameter Naming
- Use descriptive parameter names
- Follow language conventions (camelCase vs snake_case)
- Avoid reserved keywords

#### 2. Type Consistency
- Ensure JSON types match declared types
- Use appropriate precision for floating-point values
- Consider integer overflow for large values

#### 3. Test Coverage
- Include edge cases (empty arrays, null values)
- Test boundary conditions
- Verify error handling

#### 4. Performance Considerations
- Limit array sizes for performance tests
- Consider memory usage for large data structures
- Set appropriate timeouts for complex algorithms

### Configuration Validation

The system automatically validates configurations:

1. **Type Checking**: Ensures parameter types are supported
2. **Value Validation**: Verifies JSON values match declared types
3. **Function Signature**: Checks function parameter consistency
4. **Expected Results**: Validates expected values are achievable

For API usage details, see the [API Documentation](api.md).
