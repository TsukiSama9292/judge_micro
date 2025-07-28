# Judge Micro 🚀

> A modern, configuration-driven online judge microservice system built for competitive programming evaluation.

## ✨ Features

- 🎯 **Configuration-Driven**: Define test cases through JSON config files
- 🔧 **Microservice Architecture**: Stateless, containerized evaluation engines
- 🐳 **Docker Native**: Full containerization with remote Docker support
- 🛡️ **Resource Isolation**: Secure sandboxed execution environment
- ⚡ **High Performance**: Efficient container lifecycle management
- 🔌 **Python SDK**: Easy-to-use Python API for integration
- 🌐 **Remote Support**: Execute on remote Docker hosts via SSH
- 📊 **Detailed Reporting**: Comprehensive performance metrics and error analysis

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
- **C Language**: GCC with cJSON library support
- **C++ Language**: G++ with modern standards (C++11 to C++23)
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

### Docker Compose

```bash
git clone https://github.com/TsukiSama9292/judge_micro.git
docker compose up -d
```

### Installation

```bash
# Install from PyPI
pip install judge_micro

# Or install from source
git clone https://github.com/TsukiSama9292/judge_micro.git
cd judge_micro
pip install -e .
```

### Basic Usage

```python
from judge_micro.services.efficient import judge_micro

# C language example
c_code = '''
#include <stdio.h>

int solve(int *a, int *b) {
    *a = *a * 2;      // 3 * 2 = 6
    *b = *b * 2 + 1;  // 4 * 2 + 1 = 9
    return 0;
}
'''

# Configuration
config = {
    "solve_params": [
        {"name": "a", "type": "int", "input_value": 3},
        {"name": "b", "type": "int", "input_value": 4}
    ],
    "expected": {"a": 6, "b": 9},
    "function_type": "int"
}

# Execute
result = judge_micro.run_microservice(
    language='c',
    user_code=c_code,
    config=config
)

print(f"Status: {result['status']}")
if result['status'] == 'SUCCESS':
    print(f"✅ Match: {result.get('match', True)}")
    print(f"⏱️ Execution time: {result['time_ms']:.3f}ms")
elif result['status'] == 'COMPILE_ERROR':
    print(f"❌ Compilation failed: {result['stderr']}")
elif result['status'] == 'RUNTIME_ERROR':
    print(f"❌ Runtime error: {result['stderr']}")
elif result['status'] == 'WRONG_ANSWER':
    print(f"❌ Wrong answer - Expected: {result['expected']}, Got: {result['actual']}")
```

## 📊 Example Output

### Successful Execution
```json
{
  "status": "SUCCESS",
  "match": true,
  "time_ms": 1.234,
  "cpu_utime": 0.0012,
  "cpu_stime": 0.0008,
  "maxrss_mb": 2.1,
  "compile_time_ms": 145.6,
  "expected": {"a": 6, "b": 9},
  "actual": {"a": 6, "b": 9},
  "stdout": "Debug output from user code",
  "stderr": ""
}
```

### Compilation Error
```json
{
  "status": "COMPILE_ERROR",
  "error": "Compilation failed",
  "stderr": "error: expected ';' before '}' token",
  "exit_code": 1,
  "compile_time_ms": 89.3
}
```

### Runtime Error
```json
{
  "status": "RUNTIME_ERROR",
  "error": "Execution failed", 
  "stderr": "Segmentation fault (core dumped)",
  "exit_code": 139,
  "time_ms": 23.1,
  "compile_time_ms": 156.7
}
```

### Wrong Answer
```json
{
  "status": "WRONG_ANSWER",
  "match": false,
  "expected": {"a": 6, "b": 9},
  "actual": {"a": 6, "b": 8},
  "time_ms": 2.1,
  "cpu_utime": 0.002,
  "cpu_stime": 0.001,
  "maxrss_mb": 1.3,
  "compile_time_ms": 128.5,
  "stdout": "Debug: Processing values...",
  "stderr": ""
}
```

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
os.environ['CONTAINER_CPU'] = '1.0'      # CPU limit
os.environ['CONTAINER_MEM'] = '256m'     # Memory limit
os.environ['CONTAINER_COUNT'] = '5'      # Max containers
```

## 🌍 Use Cases

- **Online Judge Platforms**: Competitive programming websites
- **Educational Systems**: Automated assignment grading
- **Coding Interviews**: Technical assessment platforms
- **Code Quality Tools**: Automated testing and validation
- **Research Projects**: Algorithm performance evaluation

## 📚 Documentation

- [C/C++ Usage Examples](https://github.com/TsukiSama9292/judge_micro/blob/main/examples/Judge_MicroService.ipynb)
- [API Reference](https://github.com/TsukiSama9292/judge_micro/blob/main/docs/api.md)
- [Configuration Guide](https://github.com/TsukiSama9292/judge_micro/blob/main/docs/configuration.md)
- [Error Handling & Status Codes](https://github.com/TsukiSama9292/judge_micro/blob/main/docs/error_handling.md)
- [Python SDK Guide](https://github.com/TsukiSama9292/judge_micro/blob/main/docs/python_sdk.md)
- [Deployment Guide](https://github.com/TsukiSama9292/judge_micro/blob/main/docs/deployment.md)

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/TsukiSama9292/judge_micro/blob/main/LICENSE) file for details.