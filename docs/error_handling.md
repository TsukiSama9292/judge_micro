# Error Handling & Status Codes Reference

## Overview

The Judge MicroService harness (`harness.c` and `harness.cpp`) provides comprehensive error detection and reporting capabilities. Both harnesses automatically detect compilation errors, runtime errors, and wrong answers without any manual configuration.

## Supported Status Codes

| Status Code | Description | Exit Condition | JSON Fields |
|-------------|-------------|----------------|-------------|
| `SUCCESS` | Code compiled and executed successfully | Normal execution, output matches expected (if provided) | All standard fields |
| `COMPILE_ERROR` | Compilation failed | GCC/G++ returns non-zero exit code | `error`, `stderr`, `exit_code`, `compile_time_ms` |
| `RUNTIME_ERROR` | Runtime execution failed | Program crashes, segfault, or non-zero exit | `error`, `stderr`, `exit_code`, `time_ms`, resource stats |
| `WRONG_ANSWER` | Execution succeeded but output incorrect | `expected` values don't match `actual` values | `expected`, `actual`, `match: false` |

## Error Detection Mechanisms

### 1. Compilation Error Detection

**C Harness (`harness.c`):**
```c
// Automatic compilation with error capture
char compile_cmd[512];
snprintf(compile_cmd, sizeof(compile_cmd), 
         "gcc -std=%s %s test_main.c user.c -o test_runner -lcjson 2>&1", 
         std_flag, extra_flags);

FILE *compile_output = popen(compile_cmd, "r");
char compile_errors[4096] = {0};
fread(compile_errors, 1, sizeof(compile_errors)-1, compile_output);
int compile_rc = pclose(compile_output);

if (compile_rc != 0) {
    save_error_result(argv[2], "COMPILE_ERROR", "Compilation failed", 
                     compile_errors, compile_rc, compile_time, 0, NULL);
    return 1;
}
```

**C++ Harness (`harness.cpp`):**
```cpp
// Automatic compilation with error capture
std::string cpp_std = config.value("cpp_standard", "c++17");
std::string flags = config.value("compiler_flags", "-Wall -Wextra");
std::string compile_cmd = "g++ -std=" + cpp_std + " " + flags + 
                         " test_main.cpp user.cpp -o test_runner 2>&1";

auto compile_result = run_command(compile_cmd);
if (!compile_result.success) {
    save_error_result(result_file, "COMPILE_ERROR", 
                     "Compilation failed", compile_result.error, 
                     compile_result.exit_code, compile_time);
    return 1;
}
```

**Common Compilation Errors Detected:**
- Syntax errors (missing semicolons, brackets)
- Type mismatches
- Undefined functions or variables
- Missing header files
- Language standard violations
- Linker errors

### 2. Runtime Error Detection

**Automatic Runtime Monitoring:**
```c
// Execute with monitoring
int exec_rc = system(run_cmd);
if (exec_rc != 0) {
    save_error_result(argv[2], "RUNTIME_ERROR", "Execution failed", 
                     test_stderr, exec_rc, compile_time, exec_time, &stats);
    return 2;
}
```

**Common Runtime Errors Detected:**
- Segmentation faults (exit code 139)
- Stack overflow
- Divide by zero
- Array out of bounds
- Null pointer dereference
- Infinite loops (with timeout)
- Exception throwing (C++)
- Assert failures

### 3. Wrong Answer Detection

**Automatic Output Validation:**
```c
// C Version - Compare expected vs actual
if (expected) {
    cJSON* actual = parse_output_results(test_output, expected);
    int match = compare_results(expected, actual);
    if (!match) {
        cJSON_SetValuestring(cJSON_GetObjectItem(result, "status"), "WRONG_ANSWER");
    }
}
```

```cpp
// C++ Version - Compare expected vs actual  
if (config.contains("expected")) {
    const auto& expected = config["expected"];
    auto actual = ResultAnalyzer::parse_output(exec_result.output, expected);
    result["match"] = ResultAnalyzer::compare_results(expected, actual);
    
    if (!result["match"].get<bool>()) {
        result["status"] = "WRONG_ANSWER";
    }
}
```

## JSON Result Format

### Successful Execution
```json
{
  "status": "SUCCESS",
  "stdout": "User program output",
  "stderr": "",
  "time_ms": 12.34,
  "cpu_utime": 0.01,
  "cpu_stime": 0.005,
  "maxrss_mb": 2.1,
  "compile_time_ms": 145.6,
  "expected": {"a": 6, "b": 9},
  "actual": {"a": 6, "b": 9},
  "match": true
}
```

### Compilation Error
```json
{
  "status": "COMPILE_ERROR",
  "error": "Compilation failed",
  "stderr": "user.c:5:12: error: expected ';' before '}' token",
  "exit_code": 1,
  "compile_time_ms": 89.2
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
  "cpu_utime": 0.015,
  "cpu_stime": 0.008,
  "maxrss_mb": 1.8,
  "compile_time_ms": 156.7
}
```

### Wrong Answer
```json
{
  "status": "WRONG_ANSWER",
  "stdout": "Debug: calculated values",
  "stderr": "",
  "time_ms": 8.7,
  "cpu_utime": 0.008,
  "cpu_stime": 0.002,
  "maxrss_mb": 1.5,
  "compile_time_ms": 134.2,
  "expected": {"a": 6, "b": 9},
  "actual": {"a": 6, "b": 8},
  "match": false
}
```

## Resource Monitoring

Both harnesses automatically monitor and report:

### Performance Metrics
- **Execution Time**: Wall-clock time in milliseconds
- **CPU Time**: User and system CPU time in seconds
- **Memory Usage**: Peak memory usage in MB
- **Compilation Time**: Time taken to compile in milliseconds

### Resource Monitoring Implementation
```c
// Resource monitoring in C
struct rusage ru_start, ru_end;
getrusage(RUSAGE_SELF, &ru_start);
double exec_start = now_ms();

// ... execute program ...

double exec_time = now_ms() - exec_start;
getrusage(RUSAGE_SELF, &ru_end);
resource_stats_t stats = get_resource_stats(&ru_start, &ru_end);
```

```cpp
// Resource monitoring in C++
ResourceMonitor monitor;
Timer timer;

monitor.start();
timer.start();

// ... execute program ...

auto stats = monitor.get_stats();
double exec_time = timer.elapsed_ms();
```

## Error Handling Best Practices

### 1. Configuration Validation
- Check required fields in config.json
- Validate parameter types and values
- Ensure function signature matches

### 2. Safe Execution
- Automatic resource limits
- Isolated execution environment
- Comprehensive error capture

### 3. Detailed Reporting
- Complete error messages
- Exit codes for debugging
- Performance metrics
- Resource usage statistics

### 4. User Debugging Support
- Standard output preservation
- Error context in stderr
- Compilation command details
- Runtime environment info

## Integration with Python SDK

The Python SDK automatically handles all these status codes:

```python
result = judge.run_microservice('c', user_code, config)

if result['status'] == 'SUCCESS':
    print("✅ Execution successful")
    if result.get('match', True):
        print("✅ Output matches expected")
    else:
        print("❌ Output mismatch")
        
elif result['status'] == 'COMPILE_ERROR':
    print(f"❌ Compilation failed: {result['stderr']}")
    
elif result['status'] == 'RUNTIME_ERROR':
    print(f"❌ Runtime error: {result['stderr']}")
    print(f"Exit code: {result['exit_code']}")
    
elif result['status'] == 'WRONG_ANSWER':
    print(f"❌ Wrong answer")
    print(f"Expected: {result['expected']}")
    print(f"Actual: {result['actual']}")
```

## Summary

The Judge MicroService harness provides enterprise-grade error detection and reporting:

✅ **Automatic Error Detection** - No manual configuration needed  
✅ **Comprehensive Status Codes** - Four distinct error categories  
✅ **Detailed Error Messages** - Full compilation and runtime error capture  
✅ **Resource Monitoring** - CPU, memory, and time tracking  
✅ **Output Validation** - Automatic expected vs actual comparison  
✅ **Cross-Language Support** - Consistent behavior in C and C++  
✅ **Production Ready** - Battle-tested error handling patterns  

This ensures reliable, consistent evaluation results for competitive programming and educational platforms.
