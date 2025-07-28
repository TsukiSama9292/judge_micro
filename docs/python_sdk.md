# Python SDK Guide

## Overview

The Judge MicroService Python SDK provides a high-level interface for code evaluation, supporting both C and C++ programming languages with flexible configuration options and comprehensive result reporting.

## Installation and Setup

### Package Installation

```bash
# Install from PyPI (when available)
pip install judge_micro

# Install from source
git clone https://github.com/TsukiSama9292/judge_micro.git
cd judge_micro
pip install -e .
```

### Dependencies

The SDK automatically installs the following dependencies:

- `docker` - Docker Python API client
- `paramiko` - SSH connection support for remote Docker
- `pydantic` - Configuration validation
- `python-dotenv` - Environment variable management

### Environment Setup

1. **Create environment file:**

```bash
# Create .env.local file
touch .env.local
```

2. **Configure basic settings:**

```bash
# .env.local
CONTAINER_CPU=1.0
CONTAINER_MEM=512m
DOCKER_SSH_REMOTE=false
```

3. **Verify Docker installation:**

```python
import docker
client = docker.from_env()
print(client.info())
```

## Basic Usage

### Simple Code Evaluation

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
    "expected": {"a": 5, "b": 3},
    "function_type": "int"
}

# Execute evaluation
result = judge.run_microservice('c', user_code, config)

# Check results
if result['status'] == 'SUCCESS':
    print(f"✅ Test passed! Execution time: {result['time_ms']:.3f}ms")
    if result.get('match', True):
        print("✅ Output matches expected values")
    else:
        print("❌ Output doesn't match expected values")
else:
    print(f"❌ Test failed ({result['status']}): {result.get('stderr', 'Unknown error')}")
```

### C++ Vector Processing

```python
from judge_micro.services.efficient import JudgeMicroservice

judge = JudgeMicroservice()

# C++ code that processes vectors
cpp_code = '''
#include <vector>
#include <algorithm>

bool solve(std::vector<int>& numbers, int& sum) {
    // Sort the vector
    std::sort(numbers.begin(), numbers.end());
    
    // Calculate sum
    sum = 0;
    for (int num : numbers) {
        sum += num;
    }
    
    return true;
}
'''

config = {
    "solve_params": [
        {"name": "numbers", "type": "vector<int>", "input_value": [3, 1, 4, 1, 5]},
        {"name": "sum", "type": "int", "input_value": 0}
    ],
    "expected": {
        "numbers": [1, 1, 3, 4, 5],  # Sorted
        "sum": 14                     # Sum of elements
    },
    "function_type": "bool"
}

result = judge.run_microservice('cpp', cpp_code, config)
print(f"Status: {result['status']}")
```

## Advanced Features

### Remote Docker Execution

```python
from judge_micro.sdk.docker_ssh import RemoteDockerManager
from judge_micro.services.efficient import JudgeMicroservice

# Configure remote Docker connection
remote_manager = RemoteDockerManager(
    host="192.168.1.100",
    username="docker_user",
    key_path="~/.ssh/id_rsa"
)

# Use remote Docker client
judge = JudgeMicroservice(docker_client=remote_manager)

# Execute code on remote server
result = judge.run_microservice('c', user_code, config)
```

### Batch Processing

```python
from judge_micro.services.efficient import JudgeMicroservice
import concurrent.futures
from typing import List, Dict

class BatchProcessor:
    def __init__(self, max_workers: int = 4):
        self.judge = JudgeMicroservice()
        self.max_workers = max_workers
    
    def process_submissions(self, submissions: List[Dict]) -> List[Dict]:
        """Process multiple submissions concurrently"""
        
        def evaluate_single(submission):
            return {
                'id': submission['id'],
                'result': self.judge.run_microservice(
                    submission['language'],
                    submission['code'],
                    submission['config']
                )
            }
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(evaluate_single, sub) for sub in submissions]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        return results

# Usage example
processor = BatchProcessor(max_workers=2)

submissions = [
    {
        'id': 'user_001',
        'language': 'c',
        'code': 'int solve(int a) { return a * 2; }',
        'config': {
            "solve_params": [{"name": "a", "type": "int", "input_value": 5}],
            "expected": {"a": 10},
            "function_type": "int"
        }
    },
    {
        'id': 'user_002', 
        'language': 'cpp',
        'code': 'bool solve(int& x) { x *= 3; return true; }',
        'config': {
            "solve_params": [{"name": "x", "type": "int", "input_value": 4}],
            "expected": {"x": 12},
            "function_type": "bool"
        }
    }
]

results = processor.process_submissions(submissions)
for result in results:
    print(f"User {result['id']}: {result['result']['status']}")
```

### Error Handling and Validation

```python
from judge_micro.services.efficient import JudgeMicroservice
from docker.errors import DockerException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafeJudgeService:
    def __init__(self):
        try:
            self.judge = JudgeMicroservice()
            logger.info("Judge service initialized successfully")
        except DockerException as e:
            logger.error(f"Docker connection failed: {e}")
            raise
    
    def validate_config(self, config: dict) -> bool:
        """Validate configuration structure"""
        required_fields = ['solve_params', 'expected', 'function_type']
        
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field: {field}")
                return False
        
        if not isinstance(config['solve_params'], list):
            logger.error("solve_params must be a list")
            return False
        
        for param in config['solve_params']:
            if not all(key in param for key in ['name', 'type', 'input_value']):
                logger.error(f"Invalid parameter structure: {param}")
                return False
        
        return True
    
    def safe_evaluate(self, language: str, code: str, config: dict) -> dict:
        """Safely evaluate code with comprehensive error handling"""
        
        # Validate inputs
        if language not in ['c', 'cpp']:
            return {'status': 'COMPILE_ERROR', 'error': f'Unsupported language: {language}', 'stderr': ''}
        
        if not self.validate_config(config):
            return {'status': 'COMPILE_ERROR', 'error': 'Invalid configuration', 'stderr': ''}
        
        try:
            # Execute evaluation
            result = self.judge.run_microservice(
                language, code, config, show_logs=True
            )
            
            logger.info(f"Evaluation completed: {result['status']}")
            return result
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {
                'status': 'RUNTIME_ERROR',
                'error': str(e),
                'stderr': str(e),
                'time_ms': 0
            }

# Usage
safe_judge = SafeJudgeService()
result = safe_judge.safe_evaluate('c', user_code, config)
```

### Performance Monitoring

```python
from judge_micro.services.efficient import JudgeMicroservice
import time
import statistics
from typing import List

class PerformanceMonitor:
    def __init__(self):
        self.judge = JudgeMicroservice()
        self.execution_times: List[float] = []
        self.memory_usage: List[str] = []
    
    def benchmark_evaluation(self, language: str, code: str, config: dict, runs: int = 5):
        """Run multiple evaluations and collect performance metrics"""
        
        results = []
        
        for i in range(runs):
            start_time = time.time()
            
            result = self.judge.run_microservice(language, code, config)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            self.execution_times.append(total_time)
            
            results.append({
                'run': i + 1,
                'status': result['status'],
                'execution_time': result.get('execution_time', 0),
                'total_time': total_time,
                'memory_usage': result.get('memory_usage', 'unknown')
            })
        
        # Calculate statistics
        stats = {
            'total_runs': runs,
            'successful_runs': sum(1 for r in results if r['status'] == 'SUCCESS'),
            'average_time': statistics.mean(self.execution_times),
            'median_time': statistics.median(self.execution_times),
            'min_time': min(self.execution_times),
            'max_time': max(self.execution_times),
            'std_deviation': statistics.stdev(self.execution_times) if runs > 1 else 0
        }
        
        return {
            'results': results,
            'statistics': stats
        }
    
    def get_performance_report(self) -> dict:
        """Generate comprehensive performance report"""
        if not self.execution_times:
            return {'error': 'No performance data available'}
        
        return {
            'total_evaluations': len(self.execution_times),
            'average_execution_time': statistics.mean(self.execution_times),
            'fastest_execution': min(self.execution_times),
            'slowest_execution': max(self.execution_times),
            'performance_consistency': 1 - (statistics.stdev(self.execution_times) / statistics.mean(self.execution_times))
        }

# Benchmark example
monitor = PerformanceMonitor()

benchmark_code = '''
int solve(int n) {
    int result = 0;
    for (int i = 1; i <= n; i++) {
        result += i;
    }
    return result;
}
'''

benchmark_config = {
    "solve_params": [{"name": "n", "type": "int", "input_value": 1000}],
    "expected": {"n": 1000},
    "function_type": "int"
}

benchmark_results = monitor.benchmark_evaluation('c', benchmark_code, benchmark_config, runs=10)

print("Benchmark Results:")
print(f"Successful runs: {benchmark_results['statistics']['successful_runs']}/10")
print(f"Average time: {benchmark_results['statistics']['average_time']:.3f}s")
print(f"Standard deviation: {benchmark_results['statistics']['std_deviation']:.3f}s")
```

## Web Framework Integration

### Flask Application

```python
from flask import Flask, request, jsonify, render_template
from judge_micro.services.efficient import JudgeMicroservice
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize judge service once
judge_service = JudgeMicroservice()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/evaluate', methods=['POST'])
def evaluate_code():
    try:
        data = request.json
        
        # Validate input
        required_fields = ['language', 'code', 'config']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Execute evaluation
        result = judge_service.run_microservice(
            data['language'],
            data['code'],
            data['config'],
            show_logs=False
        )
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Evaluation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    try:
        # Simple test to verify service is working
        test_result = judge_service.run_microservice(
            'c',
            'int solve() { return 42; }',
            {
                "solve_params": [],
                "expected": {},
                "function_type": "int"
            }
        )
        
        return jsonify({
            'status': 'healthy',
            'service_available': test_result['status'] == 'SUCCESS'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### FastAPI Application

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from judge_micro.services.efficient import JudgeMicroservice
import asyncio
import uuid

app = FastAPI(title="Judge MicroService API", version="1.0.0")

# Initialize service
judge_service = JudgeMicroservice()

# In-memory storage for async results (use Redis in production)
results_store: Dict[str, dict] = {}

class EvaluationRequest(BaseModel):
    language: str = Field(..., regex="^(c|cpp)$")
    code: str = Field(..., min_length=1)
    config: dict
    
class EvaluationResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[dict] = None

@app.post("/evaluate", response_model=dict)
async def evaluate_code(request: EvaluationRequest):
    """Synchronous code evaluation"""
    try:
        result = judge_service.run_microservice(
            request.language,
            request.code,
            request.config
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate/async", response_model=EvaluationResponse)
async def evaluate_code_async(request: EvaluationRequest, background_tasks: BackgroundTasks):
    """Asynchronous code evaluation"""
    job_id = str(uuid.uuid4())
    
    def run_evaluation():
        try:
            result = judge_service.run_microservice(
                request.language,
                request.code,
                request.config
            )
            results_store[job_id] = {
                'status': 'completed',
                'result': result
            }
        except Exception as e:
            results_store[job_id] = {
                'status': 'failed',
                'error': str(e)
            }
    
    # Store initial status
    results_store[job_id] = {'status': 'processing'}
    
    # Run evaluation in background
    background_tasks.add_task(run_evaluation)
    
    return EvaluationResponse(
        job_id=job_id,
        status='processing'
    )

@app.get("/evaluate/async/{job_id}", response_model=EvaluationResponse)
async def get_evaluation_result(job_id: str):
    """Get asynchronous evaluation result"""
    if job_id not in results_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = results_store[job_id]
    
    response = EvaluationResponse(
        job_id=job_id,
        status=job_data['status']
    )
    
    if job_data['status'] == 'completed':
        response.result = job_data['result']
    elif job_data['status'] == 'failed':
        response.result = {'error': job_data['error']}
    
    return response

@app.get("/health")
async def health_check():
    """Service health check"""
    return {
        'status': 'healthy',
        'service': 'Judge MicroService',
        'version': '1.0.0'
    }

# Run with: uvicorn main:app --host 0.0.0.0 --port 8000
```

## Configuration Patterns

### Environment-Based Configuration

```python
import os
from judge_micro.services.efficient import JudgeMicroservice
from judge_micro.config.settings import Settings

class ConfigurableJudgeService:
    def __init__(self):
        # Load configuration based on environment
        env = os.getenv('ENVIRONMENT', 'development')
        
        if env == 'production':
            self.load_production_config()
        elif env == 'testing':
            self.load_test_config()
        else:
            self.load_development_config()
        
        self.judge = JudgeMicroservice()
    
    def load_development_config(self):
        os.environ['CONTAINER_CPU'] = '0.5'
        os.environ['CONTAINER_MEM'] = '256m'
        os.environ['DOCKER_SSH_REMOTE'] = 'false'
    
    def load_production_config(self):
        os.environ['CONTAINER_CPU'] = '2.0'
        os.environ['CONTAINER_MEM'] = '1g'
        os.environ['DOCKER_SSH_REMOTE'] = 'true'
        os.environ['DOCKER_SSH_HOST'] = 'prod-docker-server'
    
    def load_test_config(self):
        os.environ['CONTAINER_CPU'] = '0.25'
        os.environ['CONTAINER_MEM'] = '128m'
        os.environ['DOCKER_SSH_REMOTE'] = 'false'
```

### Dynamic Resource Allocation

```python
from judge_micro.services.efficient import JudgeMicroservice
import os

class AdaptiveJudgeService:
    def __init__(self):
        self.judge = JudgeMicroservice()
        self.base_cpu = float(os.getenv('CONTAINER_CPU', 1.0))
        self.base_memory = os.getenv('CONTAINER_MEM', '512m')
    
    def evaluate_with_complexity(self, language: str, code: str, config: dict, complexity: str = 'normal'):
        """Adjust resources based on code complexity"""
        
        # Adjust resource limits based on complexity
        if complexity == 'high':
            os.environ['CONTAINER_CPU'] = str(self.base_cpu * 2)
            os.environ['CONTAINER_MEM'] = self._scale_memory(self.base_memory, 2)
        elif complexity == 'low':
            os.environ['CONTAINER_CPU'] = str(self.base_cpu * 0.5)
            os.environ['CONTAINER_MEM'] = self._scale_memory(self.base_memory, 0.5)
        else:
            os.environ['CONTAINER_CPU'] = str(self.base_cpu)
            os.environ['CONTAINER_MEM'] = self.base_memory
        
        # Create new judge instance with updated settings
        adaptive_judge = JudgeMicroservice()
        
        try:
            result = adaptive_judge.evaluate_code(language, code, config)
            return result
        finally:
            # Reset to base configuration
            os.environ['CONTAINER_CPU'] = str(self.base_cpu)
            os.environ['CONTAINER_MEM'] = self.base_memory
    
    def _scale_memory(self, memory_str: str, factor: float) -> str:
        """Scale memory limit by factor"""
        if memory_str.endswith('m'):
            value = int(memory_str[:-1])
            return f"{int(value * factor)}m"
        elif memory_str.endswith('g'):
            value = int(memory_str[:-1])
            return f"{int(value * factor)}g"
        return memory_str
```

## Testing and Debugging

### Unit Testing

```python
import unittest
from judge_micro.services.efficient import JudgeMicroservice

class TestJudgeService(unittest.TestCase):
    def setUp(self):
        self.judge = JudgeMicroservice()
        
        self.simple_c_code = '''
        int solve(int x) {
            return x * 2;
        }
        '''
        
        self.simple_config = {
            "solve_params": [{"name": "x", "type": "int", "input_value": 5}],
            "expected": {"x": 10},
            "function_type": "int"
        }
    
    def test_successful_evaluation(self):
        result = self.judge.run_microservice('c', self.simple_c_code, self.simple_config)
        
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertGreater(result.get('time_ms', 0), 0)
    
    def test_compilation_error(self):
        bad_code = '''
        int solve(int x) {
            return x * ; // Syntax error
        }
        '''
        
        result = self.judge.run_microservice('c', bad_code, self.simple_config)
        
        self.assertEqual(result['status'], 'COMPILE_ERROR')
        self.assertIn('error', result.get('stderr', '').lower())
    
    def test_invalid_language(self):
        with self.assertRaises(ValueError):
            self.judge.run_microservice('python', self.simple_c_code, self.simple_config)

if __name__ == '__main__':
    unittest.main()
```

### Debug Mode

```python
from judge_micro.services.efficient import JudgeMicroservice
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Create debug judge instance
judge = JudgeMicroservice()

# Test with detailed logs
result = judge.run_microservice(
    'c',
    '''
    int solve(int a, int b) {
        printf("Debug: a=%d, b=%d\\n", a, b);
        return a + b;
    }
    ''',
    {
        "solve_params": [
            {"name": "a", "type": "int", "input_value": 3},
            {"name": "b", "type": "int", "input_value": 4}
        ],
        "expected": {"a": 3, "b": 4},
        "function_type": "int"
    },
    show_logs=True  # Enable detailed output
)

print("Debug output:", result.get('debug_output', ''))
```

For complete configuration options, see the [Configuration Guide](configuration.md).  
For deployment instructions, see the [Deployment Guide](deployment.md).  
For detailed API reference, see the [API Documentation](api.md).
