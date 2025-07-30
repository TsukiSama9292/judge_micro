# Python OJ Runner

This is a config-driven Online Judge runner for Python, designed to be universal and compatible with the C and C++ versions.

## Features

- **Universal harness**: `harness.py` never changes, all configuration is driven by JSON
- **Auto-generated result files**: Automatically generates result filenames like `result_user.json` based on the user file
- **Type-safe**: Supports Python type hints and various data types
- **Resource monitoring**: Tracks CPU time, memory usage, and execution time
- **Error handling**: Comprehensive error reporting for syntax errors, runtime errors, and timeouts
- **Result comparison**: Automatic comparison of expected vs actual results

## Usage

```bash
# Auto-generate result filename (recommended)
python3 harness.py config.json

# Explicit result filename
python3 harness.py config.json result.json
```

The harness automatically detects the user file and generates an appropriate result filename:
- `user.py` → `result_user.json`
- `solution.py` → `result_solution.json`
- `solve.py` → `result_solve.json`
- etc.

## Configuration Format

The configuration is identical to the C/C++ versions:

```json
{
  "solve_params": [
    {"name": "a", "type": "int", "input_value": 3},
    {"name": "b", "type": "int", "input_value": 4}
  ],
  "expected": {"a": 6, "b": 9},
  "function_type": "int",
  "python_interpreter": "python3",
  "timeout": 30
}
```

### Configuration Fields

- `solve_params`: Array of parameters for the solve function
  - `name`: Parameter name
  - `type`: Parameter type (int, float, str, list, dict, bool, etc.)
  - `input_value`: Initial value for the parameter
- `expected`: Expected output values after function execution
- `function_type`: Return type of the solve function (int, str, bool, None, etc.)
- `python_interpreter`: Python interpreter to use (default: "python3")
- `timeout`: Execution timeout in seconds (default: 30)

### Supported Types

- **Basic types**: `int`, `float`, `str`, `bool`
- **Collections**: `list`, `dict`
- **Aliases**: `string` (→ `str`), `vector<int>` (→ `list`), `double` (→ `float`)

## User Code Format

Users only need to implement the `solve` function in `user.py`:

```python
def solve(a: int, b: int) -> int:
    """
    Your solution here.
    Modify parameters in-place if needed.
    """
    a = a * 2
    b = b + 5
    return 0
```

## Examples

### Basic Integer Manipulation

**config.json:**
```json
{
  "solve_params": [
    {"name": "a", "type": "int", "input_value": 3},
    {"name": "b", "type": "int", "input_value": 4}
  ],
  "expected": {"a": 6, "b": 9},
  "function_type": "int"
}
```

**user.py:**
```python
def solve(a: int, b: int) -> int:
    a = a * 2
    b = b + 5
    return 0
```

### List Processing

**config_list.json:**
```json
{
  "solve_params": [
    {"name": "numbers", "type": "list", "input_value": [1, 2, 3, 4, 5]},
    {"name": "sum_result", "type": "int", "input_value": 0}
  ],
  "expected": {"numbers": [2, 4, 6, 8, 10], "sum_result": 30},
  "function_type": "bool"
}
```

**user_list.py:**
```python
def solve(numbers: list, sum_result: int) -> bool:
    for i in range(len(numbers)):
        numbers[i] = numbers[i] * 2
    sum_result = sum(numbers)
    return True
```

### Factorial Calculation

**config_factorial.json:**
```json
{
  "solve_params": [
    {"name": "n", "type": "int", "input_value": 5},
    {"name": "factorial", "type": "int", "input_value": 0}
  ],
  "expected": {
    "n": 5,
    "factorial": 120
  },
  "function_type": "int"
}
```

**user_factorial.py:**
```python
def solve(n: int, factorial: int) -> int:
    result = 1
    for i in range(1, n + 1):
        result *= i
    factorial = result
    return 0
```

## Output Format

The runner produces a JSON result file with the following structure:

### Success Case
```json
{
  "status": "SUCCESS",
  "stdout": "...",
  "stderr": "...",
  "time_ms": 15.2,
  "cpu_utime": 0.01,
  "cpu_stime": 0.002,
  "maxrss_mb": 8.5,
  "compile_time_ms": 5.1,
  "expected": {"a": 6, "b": 9},
  "actual": {"a": 6, "b": 9},
  "match": true
}
```

### Error Cases
```json
{
  "status": "COMPILE_ERROR",
  "error": "Syntax error",
  "stderr": "SyntaxError: invalid syntax...",
  "exit_code": 1,
  "compile_time_ms": 3.2
}
```

```json
{
  "status": "RUNTIME_ERROR",
  "error": "Execution failed",
  "stderr": "ZeroDivisionError: division by zero",
  "exit_code": 1,
  "compile_time_ms": 5.1,
  "time_ms": 8.3,
  "cpu_utime": 0.005,
  "cpu_stime": 0.001,
  "maxrss_mb": 7.2
}
```

```json
{
  "status": "WRONG_ANSWER",
  "stdout": "...",
  "stderr": "...",
  "time_ms": 12.5,
  "cpu_utime": 0.008,
  "cpu_stime": 0.002,
  "maxrss_mb": 8.1,
  "compile_time_ms": 4.8,
  "expected": {"a": 6, "b": 9},
  "actual": {"a": 5, "b": 8},
  "match": false
}
```

## Testing

Run the examples:

```bash
# Basic test
python3 harness.py config.json result.json

# List processing test
cp user_list.py user.py
python3 harness.py config_list.json result_list.json

# Factorial test
cp user_factorial.py user.py
python3 harness.py config_factorial.json result_factorial.json
```

## Implementation Notes

1. **Parameter passing**: Python parameters are passed by reference for mutable objects and by value for immutable objects. The harness handles this automatically.

2. **Type conversion**: The harness automatically converts input values to the appropriate Python types based on the configuration.

3. **Result extraction**: Results are extracted from a `function_result.txt` file rather than stdout, allowing user code to print to stdout without interfering with result checking.

4. **Error handling**: The harness catches and reports syntax errors, runtime errors, and timeouts with detailed information.

5. **Resource monitoring**: CPU time and memory usage are monitored using the `resource` module.

6. **Compatibility**: The output format matches the C and C++ versions for consistency across language runners.
