![repo_logo](https://raw.githubusercontent.com/TsukiSama9292/judge_micro/refs/heads/main/assets/repo_logo.png)

# Judge Microservice

A modern, configuration-driven online judge microservice system for automated code evaluation. Built with Docker and designed for high-performance competitive programming assessment and educational purposes.

## ✨ Features

- 🚀 **Zero Code Modification**: The evaluation harness never requires changes
- 🎯 **Pure Function Interface**: User functions operate on parameters without global state
- 📝 **Configuration-Driven**: Define test cases through JSON configuration files
- 🐳 **Docker Native**: Full containerization with local and remote Docker support
- 🔧 **Microservice Architecture**: Stateless, containerized evaluation engines
- 🛡️ **Resource Isolation**: Secure sandboxed execution environment with resource limits
- ⚡ **High Performance**: Efficient container lifecycle management
- 🚀 **Optimized Batch Execution**: Test same code with multiple configurations without recompilation
- 🐍 **Python Support**: Full Python language support with multiple versions (3.9-3.13)
- 🔌 **Python SDK**: Easy-to-use Python API for seamless integration
- 🌐 **Remote Support**: Execute on remote Docker hosts via SSH
- 📊 **Detailed Reporting**: Comprehensive performance metrics and error analysis
- 💻 **Multi-Language Support**: C, C++, and Python with modern standards
- 🛠️ **RESTful API**: Complete HTTP API with OpenAPI documentation

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Judge Micro System                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌───────────────────┐ │
│  │  Client Code    │    │  API / SDK      │    │  Docker Manager   │ │
│  │  - Submit Code  │───▶│  - JudgeMicro   │───▶│  - Local/Remote   │ │
│  │  - Get Results  │    │  - Validation   │    │  - SSH Support    │ │
│  └─────────────────┘    └─────────────────┘    └───────────────────┘ │
│                                   │                       │          │
│                                   ▼                       ▼          │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    Execution Containers                         │ │
│  │                                                                 │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────────────┐  │ │
│  │  │  C Container  │  │ C++ Container │  │  Python Container   │  │ │
│  │  │- GCC Compiler │  │- G++ Compiler │  │ - Python 3.9-3.13   │  │ │
│  │  │- cJSON Library│  │- JSON Library │  │ - JSON Library      │  │ │
│  │  │- Test Harness │  │- Test Harness │  │ - Test Harness      │  │ │
│  │  └───────────────┘  └───────────────┘  └─────────────────────┘  │ │
│  │        │                    │                    │              │ │
│  │        ▼                    ▼                    ▼              │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────────────┐  │ │
│  │  │ Config.json   │  │ Config.json   │  │    Config.json      │  │ │
│  │  │ User Code     │  │ User Code     │  │    User Code        │  │ │
│  │  │ Test Cases    │  │ Test Cases    │  │    Test Cases       │  │ │
│  │  └───────────────┘  └───────────────┘  └─────────────────────┘  │ │
│  │        │                    │                    │              │ │
│  │        ▼                    ▼                    ▼              │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────────────┐  │ │
│  │  │ Result.json   │  │ Result.json   │  │    Result.json      │  │ │
│  │  │ - Status      │  │ - Status      │  │    - Status         │  │ │
│  │  │ - Performance │  │ - Performance │  │    - Performance    │  │ │
│  │  │ - Errors      │  │ - Errors      │  │    - Errors         │  │ │
│  │  └───────────────┘  └───────────────┘  └─────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

## 🧠 AI Usage

I checked the code, wrote parts of it, and worked on logic, flow, and documentation. AI tools helped speed things up and gave useful suggestions along the way.

### Vibe Coding

- Tools: VSCode - Github Copilot  
- Models: Claude Sonnet 4  
- Helped with code completion, logic refinement, and some quick snippets.

### Brainstorm

- Tools: ChatGPT (Website)  
- Models: GPT-4o  
- Used for exploring ideas, clarifying concepts, and writing draft docs.

## 🎯 Core Design Principles

### 1. Configuration-Driven Evaluation 📝
- **Zero Code Modification**: The evaluation harness never needs changes
- **Pure Function Interface**: User functions operate on parameters without global state
- **JSON Configuration**: Test cases defined through structured configuration files
- **Flexible Parameters**: Support for arbitrary function signatures and types

### 2. Microservice Architecture 🔧
- **Stateless Execution**: Each evaluation runs in isolation
- **Container Lifecycle**: Create → Execute → Destroy pattern
- **Resource Management**: CPU, memory, and time limits enforced
- **Scalable Design**: Horizontal scaling through container orchestration

### 3. Multi-Language Support 💻
- **C Language**: GCC with cJSON library support (C99, C11, C23)
- **C++ Language**: G++ with modern standards (C++11, C++17, C++20, C++23)
- **Python Language**: Multiple Python versions (3.9, 3.10, 3.11, 3.12, 3.13)
- **Template Support**: Generic functions and type deduction
- **No Compilation for Python**: Direct execution for interpreted languages
- **Extensible Framework**: Easy addition of new language containers

### 4. Comprehensive Error Detection 🛡️
- **Compilation Errors**: Automatic detection of syntax and type errors
- **Runtime Errors**: Segmentation faults, exceptions, and crashes
- **Logic Errors**: Output validation against expected results
- **Resource Monitoring**: CPU time, memory usage, and execution metrics

## 🛠️ System Requirements

- **Operating System**: Linux (Ubuntu/Debian recommended)
- **Container Runtime**: Docker Engine 20.10+
- **Python**: 3.8+ for SDK usage
- **Network**: Internet access for Docker image pulls

## 🚀 Quick Start

### Method 1: Docker Compose (Recommended)

```bash
git clone https://github.com/TsukiSama9292/judge_micro.git
cd judge_micro
docker compose up -d
```

### Method 2: Python SDK Installation

```bash
# Install from PyPI
pip install judge_micro
# (Optional) Start API Server
uvicorn judge_micro.api.main:get_app --host 0.0.0.0 --port 8000 --factory --reload
```

### Method 3: Python SDK Installation (From Github)

```bash
git clone https://github.com/TsukiSama9292/judge_micro.git
cd judge_micro
pip install -e .
# (Optional) Start API Server
python3 main.py dev
```

## 💡 Usage Examples

### Python SDK - Basic Example

```python
from judge_micro.services.efficient import JudgeMicroservice

# Initialize the service
judge = JudgeMicroservice()

# C/C++ example
user_code = '''
int solve(int *a, int *b) {
    *a = *a + *b;
    return 0;
}
'''

config = {
    "solve_params": [
        {"name": "a", "type": "int", "input_value": 5},
        {"name": "b", "type": "int", "input_value": 3}
    ],
    "expected": {"a": 8, "b": 3},
    "function_type": "int"
}

result = judge.run_microservice('c', user_code, config)

if result['status'] == 'SUCCESS':
    print(f"✅ Test passed! Result: {result['actual']}")
    print(f"⏱️ Execution time: {result['metrics']['test_execution_time']:.3f}s")
```

### Python SDK - Python Language Example

```python
# Python code example
python_code = '''
def solve(numbers: list, multiplier: int) -> tuple:
    result = [x * multiplier for x in numbers]
    return (result, multiplier, result)
'''

python_config = {
    "solve_params": [
        {"name": "numbers", "type": "list", "input_value": [1, 2, 3, 4]},
        {"name": "multiplier", "type": "int", "input_value": 2}
    ],
    "expected": {"numbers": [2, 4, 6, 8], "multiplier": 2, "return_value": [2, 4, 6, 8]},
    "function_type": "list"
}

# Test with Python 3.12 (default)
result = judge.run_microservice('python', python_code, python_config)

# Test with specific Python version
result = judge.run_microservice('python-3.11', python_code, python_config)
```

### Python SDK - Optimized Batch Testing

```python
# Test same code with multiple configurations efficiently
user_code = '''
int solve(int *n, int *result) {
    if (*n <= 1) {
        *result = 1;
    } else {
        *result = 1;
        for (int i = 2; i <= *n; i++) {
            *result *= i;
        }
    }
    return 0;
}
'''

# Multiple test configurations
configs = [
    {
        "solve_params": [
            {"name": "n", "type": "int", "input_value": 5},
            {"name": "result", "type": "int", "input_value": 0}
        ],
        "expected": {"n": 5, "result": 120},
        "function_type": "int"
    },
    {
        "solve_params": [
            {"name": "n", "type": "int", "input_value": 0},
            {"name": "result", "type": "int", "input_value": 0}
        ],
        "expected": {"n": 0, "result": 1},
        "function_type": "int"
    },
    {
        "solve_params": [
            {"name": "n", "type": "int", "input_value": 7},
            {"name": "result", "type": "int", "input_value": 0}
        ],
        "expected": {"n": 7, "result": 5040},
        "function_type": "int"
    }
]

# Single compilation, multiple tests
results = judge.optimized_batch_test('c', user_code, configs)
print(f"Executed {len(results)} tests with single compilation")
```

### REST API - Basic Usage

```bash
# C/C++ submission
curl -X POST "http://localhost:8000/judge/submit" \
-H "Content-Type: application/json" \
-d '{
  "language": "c",
  "user_code": "int solve(int *a, int *b) { *a = *a + *b; return 0; }",
  "solve_params": [
    {"name": "a", "type": "int", "input_value": 5},
    {"name": "b", "type": "int", "input_value": 3}
  ],
  "expected": {"a": 8, "b": 3},
  "function_type": "int"
}'
```

### REST API - Python Submission

```bash
# Python submission with specific version
curl -X POST "http://localhost:8000/judge/submit" \
-H "Content-Type: application/json" \
-d '{
  "language": "python-3.12",
  "user_code": "def solve(numbers: list, target: int) -> tuple:\n    found = target in numbers\n    return (numbers, target, found)",
  "solve_params": [
    {"name": "numbers", "type": "list", "input_value": [1, 2, 3, 4, 5]},
    {"name": "target", "type": "int", "input_value": 3}
  ],
  "expected": {"numbers": [1, 2, 3, 4, 5], "target": 3, "return_value": true},
  "function_type": "bool"
}'
```

### REST API - Optimized Batch Processing

```bash
# Submit multiple test configurations for batch processing
curl -X POST "http://localhost:8000/judge/batch/optimized" \
-H "Content-Type: application/json" \
-d '{
  "language": "c",
  "user_code": "int solve(int *x, int *result) { *result = (*x) * (*x); return 0; }",
  "configs": [
    {
      "solve_params": [
        {"name": "x", "type": "int", "input_value": 2},
        {"name": "result", "type": "int", "input_value": 0}
      ],
      "expected": {"x": 2, "result": 4},
      "function_type": "int"
    },
    {
      "solve_params": [
        {"name": "x", "type": "int", "input_value": 5},
        {"name": "result", "type": "int", "input_value": 0}
      ],
      "expected": {"x": 5, "result": 25},
      "function_type": "int"
    }
  ]
}'
```

## 🌍 Use Cases

- **Online Judge Platforms**: Competitive programming websites like Codeforces, AtCoder
- **Educational Systems**: Automated assignment grading and student assessment
- **Coding Interviews**: Technical assessment platforms for recruitment
- **Code Quality Tools**: Automated testing and validation systems
- **Research Projects**: Algorithm performance evaluation and benchmarking
- **Multi-Language Learning**: Support for learning C, C++, and Python programming

## 🚀 Supported Languages

| Language | Versions | Container Image | Features |
|----------|----------|-----------------|----------|
| **C** | C99, C11, C23 | `tsukisama9292/judge_micro:c` | GCC compiler, cJSON library |
| **C++** | C++11, C++17, C++20, C++23 | `tsukisama9292/judge_micro:c_plus_plus` | G++ compiler, STL, templates |
| **Python** | 3.9, 3.10, 3.11, 3.12, 3.13 | `tsukisama9292/judge_micro:python-X.Y` | No compilation, direct execution |

### Python Language Support

- **Default Version**: Python 3.12 (`python` language code)
- **Specific Versions**: Use `python-3.9` through `python-3.13`
- **Built-in Types**: Support for `int`, `float`, `str`, `bool`, `list`, `dict`
- **No Compilation**: Direct execution for faster testing
- **Version-Specific Testing**: Test code compatibility across Python versions

## 🔀 Language-Specific Patterns

### C/C++ Pattern
```c
// C functions use pointers to modify parameters
int solve(int *input, int *result) {
    *result = (*input) * (*input);
    return 0;
}
```
**Expected format**: `{"input": 5, "result": 25}`

### Python Pattern
```python
# Python functions return tuple with all values
def solve(input_val: int, result: int) -> tuple:
    calculated = input_val * input_val
    return (input_val, calculated, calculated)
```
**Expected format**: `{"input_val": 5, "result": 25, "return_value": 25}`

## 📚 Documentation

- **[API Design](https://github.com/TsukiSama9292/judge_micro/blob/main/docs/api_design.md)**: Complete API specification and data models
- **[API Usage Guide](https://github.com/TsukiSama9292/judge_micro/blob/main/docs/api_usage.md)**: HTTP API usage examples and best practices
- **[Python SDK Guide](https://github.com/TsukiSama9292/judge_micro/blob/main/docs/python_sdk.md)**: Comprehensive Python SDK documentation
- **[C Language Examples](https://github.com/TsukiSama9292/judge_micro/blob/main/docker/c/README.md)**: C language evaluation examples and configurations
- **[C++ Language Examples](https://github.com/TsukiSama9292/judge_micro/blob/main/docker/c++/README.md)**: C++ language evaluation examples and configurations
- **[Python Language Examples](https://github.com/TsukiSama9292/judge_micro/blob/main/docker/python/README.md)**: Python language evaluation examples and configurations

## 🔧 Advanced Configuration

### Remote Docker Support

```python
# Configure remote Docker host via SSH
import os
os.environ['DOCKER_SSH_REMOTE'] = 'true'
os.environ['DOCKER_SSH_HOST'] = '192.168.1.100'
os.environ['DOCKER_SSH_USER'] = 'docker'
os.environ['DOCKER_SSH_KEY_PATH'] = '/path/to/ssh/key'
```

### Resource Limits

```python
# Set container resource limits
os.environ['CONTAINER_CPU'] = '1.0'      # CPU limit (cores)
os.environ['CONTAINER_MEM'] = '512m'     # Memory limit
os.environ['CONTAINER_TIMEOUT'] = '30'   # Execution timeout (seconds)
os.environ['COMPILE_TIMEOUT'] = '20'     # Compilation timeout (seconds)
```

### Language-Specific Configuration

```python
# C++ with specific standard
config = {
    "compiler_settings": {
        "standard": "cpp20",
        "flags": "-Wall -Wextra",
        "optimization_level": "-O2"
    }
}

# C with specific standard
config = {
    "compiler_settings": {
        "standard": "c11",
        "flags": "-Wall -Wextra -pedantic"
    }
}

# Python with specific version
result = judge.run_microservice('python-3.11', user_code, config)
```

### Batch Processing Configuration

```python
# Optimize batch execution for multiple test cases
from judge_micro.services.efficient import JudgeMicroservice

judge = JudgeMicroservice()

# Single code, multiple test configurations
results = judge.optimized_batch_test(
    language='python',
    user_code=user_code,
    configs=multiple_configs
)

# Performance benefits:
# - Single compilation/initialization
# - Reused container
# - Parallel test execution
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run language-specific tests
pytest tests/test_c.py -v        # C language tests
pytest tests/test_cpp.py -v      # C++ language tests  
pytest tests/test_python.py -v   # Python language tests

# Run API tests
python scripts/test_api.py

# Run optimized batch tests
pytest test_optimized_batch.py -v

# Run Python API tests
pytest test_python_api.py -v
```

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/TsukiSama9292/judge_micro/blob/main/LICENSE) file for details.