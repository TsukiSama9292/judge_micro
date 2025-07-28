![repo_logo](https://raw.githubusercontent.com/TsukiSama9292/judge_micro/refs/heads/main/assets/repo_logo.png)

A modern, configuration-driven online judge microservice system built for competitive programming evaluation.

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
cd judge_micro
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

### MUST: Pull C, C++ Judge Micro Image

```bash
docker pull tsukisama9292/judge_micro:c
docker pull tsukisama9292/judge_micro:c_plus_plus
```

## 🌍 Use Cases

- **Online Judge Platforms**: Competitive programming websites
- **Educational Systems**: Automated assignment grading
- **Coding Interviews**: Technical assessment platforms
- **Code Quality Tools**: Automated testing and validation
- **Research Projects**: Algorithm performance evaluation

## 📚 Documentation

- [C/C++ Usage Examples](https://github.com/TsukiSama9292/judge_micro/blob/main/examples/Judge_MicroService.ipynb)
- [Python SDK Guide](https://github.com/TsukiSama9292/judge_micro/blob/main/docs/python_sdk.md)

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

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/TsukiSama9292/judge_micro/blob/main/LICENSE) file for details.