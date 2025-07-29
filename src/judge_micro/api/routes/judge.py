from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

from judge_micro.api.models.judge import (
    JudgeRequest, 
    JudgeResponse, 
    BatchJudgeRequest, 
    BatchJudgeResponse,
    JudgeExamples,
    ExecutionMetrics,
    JudgeStatus
)
from judge_micro.services.micro import judge_micro

router = APIRouter(prefix="/judge", tags=["judge"])

# Create thread pool for asynchronous judge execution
executor = ThreadPoolExecutor(max_workers=4)


def _convert_legacy_result_to_response(result: Dict[str, Any]) -> JudgeResponse:
    """Convert legacy result format to new response format"""
    
    # Extract execution metrics
    metrics = ExecutionMetrics(
        total_execution_time=result.get('total_execution_time'),
        compile_execution_time=result.get('compile_execution_time'),
        test_execution_time=result.get('test_execution_time'),
        time_ms=result.get('time_ms'),
        compile_time_ms=result.get('compile_time_ms'),
        cpu_utime=result.get('cpu_utime'),
        cpu_stime=result.get('cpu_stime'),
        maxrss_mb=result.get('maxrss_mb')
    )
    
    # Create response object
    response = JudgeResponse(
        status=JudgeStatus(result.get('status', 'ERROR')),
        message=result.get('message'),
        match=result.get('match'),
        stdout=result.get('stdout'),
        stderr=result.get('stderr'),
        compile_output=result.get('compile_output'),
        expected=result.get('expected'),
        actual=result.get('actual'),
        metrics=metrics,
        exit_code=result.get('exit_code'),
        error_details=result.get('error_details')
    )
    
    return response


def _execute_judge_sync(request: JudgeRequest) -> JudgeResponse:
    """Execute judge evaluation synchronously"""
    try:
        # Build configuration
        config = {
            "solve_params": [param.model_dump() for param in request.solve_params],
            "expected": request.expected,
            "function_type": request.function_type.value
        }
        
        # Add compiler settings
        if request.compiler_settings:
            if request.compiler_settings.standard:
                if request.language.value == 'c':
                    config["c_standard"] = request.compiler_settings.standard.value
                elif request.language.value == 'cpp':
                    config["cpp_standard"] = request.compiler_settings.standard.value
            
            if request.compiler_settings.flags:
                config["compiler_flags"] = request.compiler_settings.flags
        
        # Set resource limits
        compile_timeout = None
        execution_timeout = None
        
        if request.resource_limits:
            compile_timeout = request.resource_limits.compile_timeout
            execution_timeout = request.resource_limits.execution_timeout
        
        # Execute judge evaluation
        result = judge_micro.run_microservice(
            language=request.language.value,
            user_code=request.user_code,
            config=config,
            show_logs=request.show_logs or False,
            compile_timeout=compile_timeout,
            execution_timeout=execution_timeout
        )
        
        # Convert to new format
        return _convert_legacy_result_to_response(result)
        
    except Exception as e:
        return JudgeResponse(
            status=JudgeStatus.ERROR,
            message=f"Error occurred during judge evaluation: {str(e)}",
            error_details=str(e)
        )


@router.post("/submit", response_model=JudgeResponse)
async def submit_code(request: JudgeRequest) -> JudgeResponse:
    """
    Submit code for judge evaluation
    
    Supports C and C++ language code evaluation, including:
    - Code compilation check
    - Function execution testing
    - Result verification
    - Resource usage statistics
    """
    try:
        # Use thread pool to execute judge evaluation asynchronously
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(executor, _execute_judge_sync, request)
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Judge service internal error: {str(e)}"
        )


@router.post("/batch", response_model=BatchJudgeResponse)
async def batch_submit(request: BatchJudgeRequest) -> BatchJudgeResponse:
    """
    Submit batch code evaluation
    
    Submit multiple judge evaluation requests at once, supporting:
    - Concurrent execution of multiple tests
    - Overall result statistics
    - Error handling and reporting
    """
    try:
        results = []
        start_time = time.time()
        
        # Execute all tests concurrently
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, _execute_judge_sync, test_request)
            for test_request in request.tests
        ]
        
        if request.show_progress:
            # If need to show progress, wait one by one
            for i, task in enumerate(tasks, 1):
                result = await task
                results.append(result)
                print(f"✅ Test {i}/{len(tasks)} completed")
        else:
            # Wait for all tasks to complete at once
            results = await asyncio.gather(*tasks)
        
        # Calculate statistics
        total_time = time.time() - start_time
        success_count = sum(1 for r in results if r.status == JudgeStatus.SUCCESS)
        error_count = len(results) - success_count
        
        summary = {
            "total_tests": len(results),
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": success_count / len(results) if results else 0,
            "total_execution_time": total_time,
            "average_time_per_test": total_time / len(results) if results else 0
        }
        
        return BatchJudgeResponse(
            results=results,
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch judge service internal error: {str(e)}"
        )


@router.get("/examples/c")
async def get_c_example() -> Dict[str, Any]:
    """Get C language judge evaluation example"""
    return {
        "description": "C language judge evaluation request example",
        "example": JudgeExamples.get_c_example(),
        "response_example": JudgeExamples.get_response_example()
    }


@router.get("/examples/cpp")
async def get_cpp_example() -> Dict[str, Any]:
    """Get C++ language judge evaluation example"""
    return {
        "description": "C++ language judge evaluation request example",
        "example": JudgeExamples.get_cpp_example(),
        "response_example": JudgeExamples.get_response_example()
    }


@router.get("/examples/advanced")
async def get_advanced_example() -> Dict[str, Any]:
    """Get advanced judge evaluation example"""
    return {
        "description": "C++ advanced judge evaluation example (including vectors and complex data structures)",
        "example": JudgeExamples.get_advanced_cpp_example(),
        "response_example": JudgeExamples.get_response_example()
    }


@router.get("/examples/error")
async def get_error_example() -> Dict[str, Any]:
    """Get error response example"""
    return {
        "description": "Compilation error response example",
        "example": JudgeExamples.get_error_example()
    }


@router.get("/languages")
async def get_supported_languages() -> Dict[str, Any]:
    """Get supported programming languages list"""
    return {
        "supported_languages": [
            {
                "language": "c",
                "description": "C Language",
                "standards": ["c89", "c99", "c11", "c17", "c23"],
                "default_standard": "c11"
            },
            {
                "language": "cpp", 
                "description": "C++ Language",
                "standards": ["cpp98", "cpp03", "cpp11", "cpp14", "cpp17", "cpp20", "cpp23"],
                "default_standard": "cpp17"
            }
        ],
        "parameter_types": [
            "int", "float", "double", "char", "string", 
            "array_int", "array_float", "array_char"
        ],
        "function_types": [
            "int", "float", "double", "char", "string", "void"
        ]
    }


@router.get("/status")
async def get_service_status() -> Dict[str, Any]:
    """Get judge service status"""
    try:
        # Perform simple health check
        test_request = JudgeRequest(
            language="c",
            user_code='''int solve(int *a) { *a = 42; return 0; }''',
            solve_params=[{"name": "a", "type": "int", "input_value": 1}],
            expected={"a": 42},
            function_type="int"
        )
        
        start_time = time.time()
        result = _execute_judge_sync(test_request)
        health_check_time = time.time() - start_time
        
        is_healthy = result.status == JudgeStatus.SUCCESS
        
        return {
            "service": "Judge Microservice",
            "status": "healthy" if is_healthy else "unhealthy",
            "docker_available": True,  # If we can get here, Docker is available
            "health_check_time": health_check_time,
            "supported_languages": ["c", "cpp"],
            "last_check": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        return {
            "service": "Judge Microservice",
            "status": "unhealthy",
            "error": str(e),
            "last_check": time.strftime("%Y-%m-%d %H:%M:%S")
        }


@router.get("/limits")
async def get_resource_limits() -> Dict[str, Any]:
    """Get resource limits information"""
    return {
        "default_limits": {
            "compile_timeout": 30,  # seconds
            "execution_timeout": 10,  # seconds
            "memory_limit": "128m",
            "cpu_limit": 1.0
        },
        "maximum_limits": {
            "compile_timeout": 300,  # seconds
            "execution_timeout": 60,  # seconds
            "memory_limit": "1g",
            "cpu_limit": 4.0
        },
        "code_limits": {
            "max_code_length": 50000,  # characters
            "max_batch_size": 100  # maximum number of batch tests
        }
    }
