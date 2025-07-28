# API Documentation

## Overview

The Judge MicroService provides a Python SDK for evaluating C and C++ code submissions through containerized execution environments. The SDK offers both local and remote Docker execution capabilities with comprehensive configuration options.

## Installation

```bash
# Install from PyPI
pip install judge_micro

# Install from source
git clone https://github.com/TsukiSama9292/judge_micro.git
cd judge_micro
pip install -e .
```

## Core Classes and Methods

### `JudgeMicroservice`

The main class for code evaluation operations.

#### Constructor

```python
from judge_micro.services.efficient import JudgeMicroservice

# Using default Docker client
judge = JudgeMicroservice()

# Using custom Docker client
judge = JudgeMicroservice(docker_client=custom_client)
```

#### Methods

##### `run_microservice(language, user_code, config, show_logs=False)`

Executes user code in a sandboxed container environment.

**Parameters:**
- `language` (str): Programming language - `'c'` or `'cpp'`
- `user_code` (str): User's source code to evaluate
- `config` (dict): Test configuration (see [Configuration Guide](configuration.md))
- `show_logs` (bool, optional): Enable detailed execution logs

**Returns:**
- `dict`: Execution result containing:
  - `status`: Execution status (`"SUCCESS"`, `"COMPILE_ERROR"`, `"RUNTIME_ERROR"`, `"WRONG_ANSWER"`)
  - `stdout`: Standard output from user code
  - `stderr`: Error messages (compilation or runtime)
  - `exit_code`: Process exit code (compilation or execution)
  - `time_ms`: Execution time in milliseconds
  - `cpu_utime`: User CPU time in seconds
  - `cpu_stime`: System CPU time in seconds
  - `maxrss_mb`: Maximum memory usage in MB
  - `compile_time_ms`: Compilation time in milliseconds
  - `expected`: Expected parameter values (if provided)
  - `actual`: Actual parameter values after execution
  - `match`: Boolean indicating if actual matches expected

**Example:**

```python
from judge_micro.services.efficient import JudgeMicroservice

# Initialize the service
judge = JudgeMicroservice()

# Define user code
user_code = '''
int solve(int a, int b) {
    return a * a + b * b;
}
'''

# Define test configuration
config = {
    "solve_params": [
        {"name": "a", "type": "int", "input_value": 3},
        {"name": "b", "type": "int", "input_value": 4}
    ],
    "expected": {"a": 9, "b": 16},
    "function_type": "int"
}

# Execute the code
result = judge.run_microservice('c', user_code, config, show_logs=True)

print(f"Status: {result['status']}")
if result['status'] == 'SUCCESS':
    print(f"✅ Execution time: {result['time_ms']:.3f}ms")
    if result.get('match', True):
        print("✅ Output matches expected values")
    else:
        print("❌ Output doesn't match expected values")
elif result['status'] == 'COMPILE_ERROR':
    print(f"❌ Compilation failed: {result['stderr']}")
elif result['status'] == 'RUNTIME_ERROR':
    print(f"❌ Runtime error: {result['stderr']}")
elif result['status'] == 'WRONG_ANSWER':
    print(f"❌ Wrong answer - Expected: {result['expected']}, Got: {result['actual']}")
```

### `DockerEngine`

Manages Docker client connections for both local and remote execution.

#### Constructor

```python
from judge_micro.docker.client import DockerEngine

# Auto-detection based on settings
engine = DockerEngine()

# Custom Docker client
engine = DockerEngine(docker_client=custom_client)
```

#### Methods

##### `get_client()`

Returns the configured Docker client instance.

**Returns:**
- `docker.DockerClient` or `RemoteDockerManager`: Docker client instance

### `RemoteDockerManager`

Enables remote Docker execution via SSH connections.

#### Constructor

```python
from judge_micro.sdk.docker_ssh import RemoteDockerManager

manager = RemoteDockerManager(
    host="192.168.1.100",
    username="docker_user",
    key_path="~/.ssh/id_rsa",  # Optional: SSH key path
    password="password",        # Optional: SSH password
    port=22                     # Optional: SSH port
)
```

**Parameters:**
- `host` (str): Remote server IP address or hostname
- `username` (str): SSH username
- `key_path` (str, optional): Path to SSH private key (preferred method)
- `password` (str, optional): SSH password (fallback method)
- `port` (int, optional): SSH port (default: 22)

#### Methods

##### `execute_command(command)`

Executes shell commands on the remote server.

**Parameters:**
- `command` (str): Shell command to execute

**Returns:**
- `dict`: Command execution result:
  - `command`: Original command
  - `exit_code`: Command exit code
  - `output`: Command stdout
  - `error`: Command stderr
  - `success`: Boolean success indicator

## Error Handling

The SDK provides comprehensive error handling for various failure scenarios:

### Docker Connection Errors

```python
try:
    judge = JudgeMicroservice()
except DockerException as e:
    print(f"Docker connection failed: {e}")
```

### Remote SSH Connection Errors

```python
try:
    remote_manager = RemoteDockerManager(
        host="invalid-host",
        username="user",
        password="wrong-password"
    )
except Exception as e:
    print(f"SSH connection failed: {e}")
```

### Code Execution Errors

```python
result = judge.run_microservice('c', user_code, config)

if result['status'] == 'SUCCESS':
    print("Code executed successfully")
    if 'match' in result:
        if result['match']:
            print("✅ Output matches expected values")
        else:
            print("❌ Output doesn't match expected values")
            print(f"Expected: {result['expected']}")
            print(f"Actual: {result['actual']}")
elif result['status'] == 'COMPILE_ERROR':
    print(f"❌ Compilation failed: {result['stderr']}")
elif result['status'] == 'RUNTIME_ERROR':
    print(f"❌ Runtime error: {result['stderr']}")
elif result['status'] == 'WRONG_ANSWER':
    print(f"❌ Wrong answer:")
    print(f"Expected: {result['expected']}")
    print(f"Actual: {result['actual']}")
```

## Performance Considerations

### Resource Limits

The service automatically applies resource constraints:

- **CPU Limit**: Configurable via `CONTAINER_CPU` environment variable
- **Memory Limit**: Configurable via `CONTAINER_MEM` environment variable
- **Network**: Disabled for security
- **Execution Time**: Monitored and reported

### Container Lifecycle

The service follows an efficient "Create → Execute → Destroy" pattern:

1. **Container Creation**: Fast container instantiation
2. **Code Injection**: Efficient file upload via tar archives
3. **Execution**: Sandboxed code execution
4. **Result Extraction**: JSON result retrieval
5. **Cleanup**: Immediate container removal

### Best Practices

1. **Reuse JudgeMicroservice instances**: Avoid creating new instances for each request
2. **Configure resource limits**: Set appropriate CPU and memory limits for your use case
3. **Use remote execution**: Offload execution to dedicated servers for better isolation
4. **Monitor execution times**: Track performance metrics for optimization
5. **Handle errors gracefully**: Implement proper error handling for production use

## Advanced Usage

### Custom Docker Images

You can extend the system with custom Docker images:

```python
# Custom image mapping
CUSTOM_IMAGES = {
    'python': 'my-registry/judge-python:latest',
    'java': 'my-registry/judge-java:latest'
}

judge = JudgeMicroservice()
judge.DOCKER_IMAGES.update(CUSTOM_IMAGES)
```

### Batch Processing

For multiple submissions:

```python
def process_submissions(submissions):
    judge = JudgeMicroservice()
    results = []
    
    for submission in submissions:
        result = judge.run_microservice(
            submission['language'],
            submission['code'],
            submission['config']
        )
        results.append(result)
    
    return results
```

### Integration with Web Frameworks

#### Flask Example

```python
from flask import Flask, request, jsonify
from judge_micro.services.efficient import JudgeMicroservice

app = Flask(__name__)
judge = JudgeMicroservice()

@app.route('/evaluate', methods=['POST'])
def evaluate_code():
    data = request.json
    
    try:
        result = judge.run_microservice(
            data['language'],
            data['code'],
            data['config']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### FastAPI Example

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from judge_micro.services.efficient import JudgeMicroservice

app = FastAPI()
judge = JudgeMicroservice()

class SubmissionRequest(BaseModel):
    language: str
    code: str
    config: dict

@app.post("/evaluate")
async def evaluate_code(request: SubmissionRequest):
    try:
        result = judge.run_microservice(
            request.language,
            request.code,
            request.config
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## API Reference Summary

| Class | Method | Purpose |
|-------|--------|---------|
| `JudgeMicroservice` | `__init__(docker_client=None)` | Initialize service |
| `JudgeMicroservice` | `run_microservice(language, user_code, config, show_logs=False)` | Execute code evaluation |
| `DockerEngine` | `__init__(docker_client=None)` | Initialize Docker client |
| `DockerEngine` | `get_client()` | Get Docker client instance |
| `RemoteDockerManager` | `__init__(host, username, **kwargs)` | Initialize remote connection |
| `RemoteDockerManager` | `execute_command(command)` | Execute remote commands |

For configuration details, see the [Configuration Guide](configuration.md).
