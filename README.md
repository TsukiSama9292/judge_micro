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
- 🔌 **Python SDK**: Easy-to-use Python API for seamless integration
- 🌐 **Remote Support**: Execute on remote Docker hosts via SSH
- 📊 **Detailed Reporting**: Comprehensive performance metrics and error analysis
- 💻 **Multi-Language Support**: C and C++ with modern standards (C++11 to C++23)
- 🛠️ **RESTful API**: Complete HTTP API with OpenAPI documentation

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Judge Micro System                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌───────────────────┐ │
│  │  Client Code    │    │   Python SDK    │    │  Docker Manager   │ │
│  │  - Submit Code  │───▶│  - JudgeMicro   │───▶│  - Local/Remote   │ │
│  │  - Get Results  │    │  - Validation   │    │  - SSH Support    │ │
│  └─────────────────┘    └─────────────────┘    └───────────────────┘ │
│                                   │                       │          │
│                                   ▼                       ▼          │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    Execution Containers                         │ │
│  │                                                                 │ │
│  │  ┌─────────────────┐              ┌─────────────────┐           │ │
│  │  │   C Container   │              │  C++ Container  │           │ │
│  │  │  - GCC Compiler │              │ - G++ Compiler  │           │ │
│  │  │  - cJSON Library│              │ - JSON Library  │           │ │
│  │  │  - Test Harness │              │ - Test Harness  │           │ │
│  │  └─────────────────┘              └─────────────────┘           │ │
│  │           │                                 │                   │ │
│  │           ▼                                 ▼                   │ │
│  │  ┌─────────────────┐              ┌─────────────────┐           │ │
│  │  │  Config.json    │              │  Config.json    │           │ │
│  │  │  User Code      │              │  User Code      │           │ │
│  │  │  Test Cases     │              │  Test Cases     │           │ │
│  │  └─────────────────┘              └─────────────────┘           │ │
│  │           │                                 │                   │ │
│  │           ▼                                 ▼                   │ │
│  │  ┌─────────────────┐              ┌─────────────────┐           │ │
│  │  │  Result.json    │              │  Result.json    │           │ │
│  │  │  - Status       │              │  - Status       │           │ │
│  │  │  - Performance  │              │  - Performance  │           │ │
│  │  │  - Errors       │              │  - Errors       │           │ │
│  │  └─────────────────┘              └─────────────────┘           │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

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
- **Template Support**: Generic functions and type deduction
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

# Or install from source
git clone https://github.com/TsukiSama9292/judge_micro.git
cd judge_micro
pip install -e .
```

### Method 3: API Service

```bash
# Start the REST API server
uvicorn judge_micro.api.main:get_app --host 0.0.0.0 --port 8000 --factory --reload

# Access API documentation
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

## 💡 Usage Examples

### Python SDK

```python
from judge_micro.services.efficient import JudgeMicroservice

# Initialize the service
judge = JudgeMicroservice()

# Define user code
user_code = '''
int solve(int a, int b) {
    return a + b;
}
'''

# Define test configuration
config = {
    "solve_params": [
        {"name": "a", "type": "int", "input_value": 5},
        {"name": "b", "type": "int", "input_value": 3}
    ],
    "expected": {"result": 8},
    "function_type": "int"
}

# Execute evaluation
result = judge.run_microservice('c', user_code, config)

if result['status'] == 'SUCCESS':
    print(f"✅ Test passed! Result: {result['actual']}")
    print(f"⏱️ Execution time: {result['metrics']['test_execution_time']:.3f}s")
```

### REST API

```bash
curl -X POST "http://localhost:8000/judge/submit" \
-H "Content-Type: application/json" \
-d '{
  "language": "c",
  "user_code": "int solve(int a, int b) { return a + b; }",
  "solve_params": [
    {"name": "a", "type": "int", "input_value": 5},
    {"name": "b", "type": "int", "input_value": 3}
  ],
  "expected": {"result": 8},
  "function_type": "int"
}'
```

## 🌍 Use Cases

- **Online Judge Platforms**: Competitive programming websites like Codeforces, AtCoder
- **Educational Systems**: Automated assignment grading and student assessment
- **Coding Interviews**: Technical assessment platforms for recruitment
- **Code Quality Tools**: Automated testing and validation systems
- **Research Projects**: Algorithm performance evaluation and benchmarking

## 📚 Documentation

- **[API Design](docs/api_design.md)**: Complete API specification and data models
- **[API Usage Guide](docs/api_usage.md)**: HTTP API usage examples and best practices
- **[Python SDK Guide](docs/python_sdk.md)**: Comprehensive Python SDK documentation
- **[C Language Examples](docker/c/README.md)**: C language evaluation examples and configurations
- **[C++ Language Examples](docker/c++/README.md)**: C++ language evaluation examples and configurations
- **[Jupyter Notebook Examples](examples/Judge_MicroService.ipynb)**: Interactive examples and tutorials

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
```

## 🧪 Testing

```bash
# Run Python SDK tests
pytest tests/ -v

# Run API tests
python scripts/test_api.py

# Run language-specific tests
pytest tests/test_c.py -v
pytest tests/test_cpp.py -v
```

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/TsukiSama9292/judge_micro/blob/main/LICENSE) file for details.