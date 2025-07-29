# Configuration-Driven C Language Online Judge

A modern online judge system implemented in pure C language, supporting pure functional interfaces and completely configuration-driven without requiring any core code modifications.

## ✨ Features

- 🚀 **Zero Code Modification**: The harness.c never need## 🎯 Complete Examples modification
- 🎯 **Pure Function Interface**: User functions operate without global variables
- 📝 **Configuration-Driven**: Define new problems by modifying config.json only
- ⚡ **Automatic Compilation**: Automatically generates test code and compiles for execution
- 📊 **Detailed Reporting**: Includes performance measurement, error detection, and result verification
- 🔧 **Flexible Parameters**: Supports arbitrary number of function parameters
- 💻 **Pure C Implementation**: No external dependencies, high-performance evaluation
- 🛡️ **Error Handling**: Comprehensive error detection and reporting mechanism

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Code     │    │ Configuration   │    │ Evaluation      │
│   user.c        │    │   config.json   │    │   Engine        │
│   solve() func  │ -> │   solve_params  │ -> │   harness.c     │
│   Pure function │    │   expected      │    │   Dynamic gen   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       v
                                              ┌─────────────────┐
                                              │   Result        │
                                              │   report        │
                                              │   result.json   │
                                              │   Performance   │
                                              │   Error detect  │
                                              └─────────────────┘
```

## 🛠️ Environment Requirements

- **Compiler**: GCC (C99 standard support)
- **Libraries**: cJSON library
- **System**: Linux/Unix environment
- **Tools**: Make (optional, for automation)

### Install Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install gcc libcjson-dev make

# CentOS/RHEL  
sudo yum install gcc cjson-devel make

# Verify installation
gcc --version
pkg-config --cflags --libs libcjson
```

## 🚀 Quick Start

### Method 1: Demo Script (Recommended for beginners)

```bash
# Run complete demo
./demo.sh
```

### Method 2: Manual Steps

#### Step 1: Compile harness

```bash
# Basic compilation
gcc harness.c -o harness -lcjson

# Or use Makefile (recommended)
make build
```

#### Step 2: Create configuration file

Create `config.json` (supports language version parameters):

```json
{
  "solve_params": [
    {"name": "a", "type": "int", "input_value": 3},
    {"name": "b", "type": "int", "input_value": 4}
  ],
  "expected": {"a": 6, "b": 9},
  "function_type": "int",
  "c_standard": "c11",
  "compiler_flags": "-Wall -Wextra -O2"
}
```

**Newly supported configuration parameters:**
- `c_standard`: Specify C standard (c89, c99, c11, c17, c23)
- `compiler_flags`: Custom compiler flags
- `function_type`: Return type of solve function (int, void, etc.)
- `type`: Parameter type in solve_params (int, float, etc.)

Create basic `config.json`:

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

#### Step 3: Implement user function

Create `user.c`:

```c
int solve(int *a, int *b) {
    *a = *a * 2;        // a: 3 -> 6
    *b = *b * 2 + 1;    // b: 4 -> 9
    return 0;           // Return 0 for success
}
```

#### Step 4: Run evaluation

```bash
# Direct execution
./harness config.json result.json

# View results
cat result.json

# Or use Makefile automation
make test
make show-result
```

### Method 3: Makefile Automation

```bash
make help          # Show all available commands
make build         # Compile harness
make test-config CONFIG_FILE=config.json  # Run test with specific config
make show-result   # Show test results
make examples      # Run examples
make clean         # Clean generated files
```

## 📋 Configuration File Format

### config.json Structure

```json
{
  "solve_params": [
    {"name": "parameter_name", "type": "parameter_type", "input_value": input_value},
    {"name": "parameter_name", "type": "parameter_type", "input_value": input_value}
  ],
  "expected": {
    "parameter_name": expected_value,
    "parameter_name": expected_value
  },
  "function_type": "return_type",
  "c_standard": "c_standard_version",
  "compiler_flags": "additional_flags"
}
```

### Parameter Description

- **solve_params**: Function parameter definition array
  - **name**: Parameter name (must be a valid C variable name)
  - **type**: Parameter data type (int, float, double, etc.)
  - **input_value**: Initial value of parameter (must match the type)
- **expected**: Expected output values (key as parameter name, value as expected result)
- **function_type**: Return type of the solve function (int, void, etc.)
- **c_standard**: C language standard version (c89, c99, c11, c17, c23)
- **compiler_flags**: Additional compiler flags for compilation

### Configuration Examples

#### Single Parameter Configuration
```json
{
  "solve_params": [
    {"name": "result", "type": "int", "input_value": 5}
  ],
  "expected": {"result": 25},
  "function_type": "int"
}
```

#### Multiple Parameter Configuration
```json
{
  "solve_params": [
    {"name": "x", "type": "int", "input_value": 10},
    {"name": "y", "type": "int", "input_value": 20},
    {"name": "sum", "type": "int", "input_value": 0}
  ],
  "expected": {"x": 10, "y": 20, "sum": 30},
  "function_type": "int"
}
```

## 💻 User Function Specification

### Function Signature Requirements

```c
return_type solve(type1 *param1, type2 *param2, ..., typeN *paramN);
```

### Rule Description

1. **Function name must be `solve`**
2. **All parameters are pointers to their respective types**
3. **Return value type is configurable** (int, void, etc., specified in config.json)
4. **Input values passed through pointers, modified as output**
5. **Parameter count must match solve_params count in config.json**
6. **Parameter order must match solve_params order in config.json**
7. **Parameter types must match those specified in config.json**

### Implementation Examples

#### Basic Mathematical Operations
```c
// Corresponding config: {"name": "x", "type": "int", "input_value": 5}
int solve(int *x) {
    *x = *x * *x;  // Calculate square: 5 -> 25
    return 0;      // Success
}
```

#### Multiple Parameter Processing
```c
// Corresponding config: [{"name": "a", "type": "int", "input_value": 3}, {"name": "b", "type": "int", "input_value": 4}]
int solve(int *a, int *b) {
    *a = *a * 2;   // a: 3 -> 6
    *b = *b + 5;   // b: 4 -> 9
    return 0;
}
```

#### Error Handling
```c
int solve(int *a, int *b) {
    // Input validation
    if (*a < 0 || *b < 0) {
        return -1;  // Error: negative input
    }
    
    // Main logic
    *a = *a + *b;
    *b = *a - *b;
    return 0;  // Success
}
```

## 📊 Result Report Format

After execution, `result.json` contains the following information:

```json
{
  "status": "SUCCESS",
  "stdout": "",
  "stderr": "",
  "time_ms": 3.4,
  "cpu_utime": 0.000385,
  "cpu_stime": 0,
  "maxrss_mb": 1.54,
  "compile_time_ms": 45.2,
  "expected": {"a": 6, "b": 9},
  "actual": {"a": 6, "b": 9},
  "match": true
}
```

### Field Description

- **status**: Execution status (SUCCESS/COMPILE_ERROR/RUNTIME_ERROR/WRONG_ANSWER)
- **stdout**: Program standard output
- **stderr**: Program standard error output
- **time_ms**: Total execution time (milliseconds)
- **cpu_utime**: User mode CPU time (seconds)
- **cpu_stime**: System mode CPU time (seconds) 
- **maxrss_mb**: Maximum memory usage (MB)
- **compile_time_ms**: Compilation time (milliseconds)
- **expected**: Expected output values (when available)
- **actual**: Actual output values (when available)
- **match**: Whether actual matches expected (boolean, when comparison available)

### Status Determination

- **SUCCESS**: Code compiled and executed successfully, all outputs match expected values
- **COMPILE_ERROR**: Compilation failed due to syntax errors or missing dependencies
- **RUNTIME_ERROR**: Program compiled but failed during execution (segfault, timeout, etc.)
- **WRONG_ANSWER**: Program executed successfully but outputs don't match expected values

---

## 📞 Support

If you have questions, please check the troubleshooting section or submit an Issue.

**Main File Description:**
- `harness.c` - Core evaluation engine (universal, never needs modification)
- `config.json` - Problem configuration file (defines parameters and expected results)
- `user.c` - User implementation file (contains the solve function)
- `solve.h` - Auto-generated header file (created by harness)
- `test_main.c` - Auto-generated test runner (created by harness)
- `Makefile` - Build automation and test management
- `demo.sh` - Demonstration script (shows basic usage)

This C language evaluation system provides a complete configuration-driven online judge solution that seamlessly integrates with the broader Judge Microservice ecosystem. The harness ensures consistent behavior and accurate status reporting for all evaluation scenarios.