# Judge Microservice API Usage Guide

## Quick Start

### 1. Start API Service

```bash
# Navigate to project directory
cd /home/tsukisama9292/workspace/judge_micro

# Start API server
uvicorn judge_micro.api.main:get_app --host 0.0.0.0 --port 8000 --factory --reload
```

### 2. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

### 3. Test API

```bash
# Run automated tests
python scripts/test_api.py

# Or use pytest
pytest tests/test_judge_api.py -v
```

## API Endpoints Overview

### Core Evaluation Endpoints

- `POST /judge/submit` - Submit single code evaluation
- `POST /judge/batch` - Batch code evaluation
- `POST /judge/batch/optimized` - Optimized batch evaluation for same code with different test configurations

### Information Query Endpoints

- `GET /judge/status` - Service status
- `GET /judge/languages` - Supported languages
- `GET /judge/limits` - Resource limits
- `GET /judge/examples/{type}` - Usage examples

## Usage Examples

### 1. C Language Evaluation

```bash
curl -X POST "http://localhost:8000/judge/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "c",
    "user_code": "#include <stdio.h>\n\nint solve(int *a, int *b) {\n    *a = *a * 2;\n    *b = *b * 2 + 1;\n    printf(\"Hello from C!\\n\");\n    return 0;\n}",
    "solve_params": [
      {"name": "a", "type": "int", "input_value": 3},
      {"name": "b", "type": "int", "input_value": 4}
    ],
    "expected": {"a": 6, "b": 9},
    "function_type": "int"
  }'
```

### 2. C++ Language Evaluation

```bash
curl -X POST "http://localhost:8000/judge/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "cpp",
    "user_code": "#include <iostream>\n\nint solve(int &a, int &b) {\n    a = a * 2;\n    b = b * 2 + 1;\n    std::cout << \"Hello from C++!\" << std::endl;\n    return 0;\n}",
    "solve_params": [
      {"name": "a", "type": "int", "input_value": 3},
      {"name": "b", "type": "int", "input_value": 4}
    ],
    "expected": {"a": 6, "b": 9},
    "function_type": "int",
    "compiler_settings": {
      "standard": "cpp17",
      "flags": "-Wall -Wextra -O2 -std=c++17"
    }
  }'
```

### 3. Python Language Evaluation

```bash
curl -X POST "http://localhost:8000/judge/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "python",
    "user_code": "def solve(a: int, b: int) -> tuple:\n    \"\"\"Test function that modifies parameters via tuple return\"\"\"\n    a = a * 2\n    b = b * 2 + 1\n    print(\"Hello from Python!\")\n    return (a, b, 0)",
    "solve_params": [
      {"name": "a", "type": "int", "input_value": 3},
      {"name": "b", "type": "int", "input_value": 4}
    ],
    "expected": {"a": 6, "b": 9},
    "function_type": "int",
    "compiler_settings": {
      "standard": "python3.12"
    }
  }'
```

### 4. Using Python SDK

```python
from judge_micro.sdk.client import JudgeSDK, JudgeSDKHelper

# Initialize SDK
sdk = JudgeSDK(base_url="http://localhost:8000")

# Create C language request
request = JudgeSDKHelper.create_c_request(
    user_code='''#include <stdio.h>
int solve(int *a, int *b) {
    *a = *a * 2;
    *b = *b * 2 + 1;
    return 0;
}''',
    params=[
        {"name": "a", "type": "int", "value": 3},
        {"name": "b", "type": "int", "value": 4}
    ],
    expected={"a": 6, "b": 9}
)

# Submit evaluation
result = sdk.submit_code(request)
print(f"Evaluation result: {result['status']}")
print(f"Result match: {result['match']}")

# Create Python language request
python_request = JudgeSDKHelper.create_python_request(
    user_code='''def solve(a: int, b: int) -> tuple:
    """Test function that modifies parameters via tuple return"""
    a = a * 2
    b = b * 2 + 1
    return (a, b, 0)''',
    params=[
        {"name": "a", "type": "int", "value": 3},
        {"name": "b", "type": "int", "value": 4}
    ],
    expected={"a": 6, "b": 9}
)

# Submit Python evaluation
python_result = sdk.submit_code(python_request)
print(f"Python evaluation result: {python_result['status']}")
```

### 5. Optimized Batch Evaluation

For testing the same code with multiple test configurations efficiently:

```bash
curl -X POST "http://localhost:8000/judge/batch/optimized" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "c",
    "user_code": "#include <stdio.h>\nint solve(int *a, int *b) {\n    *a = *a * 2;\n    *b = *b * 2 + 1;\n    printf(\"Test: a=%d, b=%d\\n\", *a, *b);\n    return 0;\n}",
    "configs": [
      {
        "solve_params": [
          {"name": "a", "type": "int", "input_value": 3},
          {"name": "b", "type": "int", "input_value": 4}
        ],
        "expected": {"a": 6, "b": 9},
        "function_type": "int"
      },
      {
        "solve_params": [
          {"name": "a", "type": "int", "input_value": 5},
          {"name": "b", "type": "int", "input_value": 10}
        ],
        "expected": {"a": 10, "b": 21},
        "function_type": "int"
      },
      {
        "solve_params": [
          {"name": "a", "type": "int", "input_value": 1},
          {"name": "b", "type": "int", "input_value": 2}
        ],
        "expected": {"a": 2, "b": 5},
        "function_type": "int"
      }
    ],
    "compiler_settings": {
      "standard": "c11",
      "flags": "-Wall -Wextra -O2"
    },
    "show_progress": true
  }'
```

**Key Benefits of Optimized Batch:**
- **Single Compilation**: Code is compiled only once for all test configurations
- **Faster Execution**: Significantly faster for multiple test cases
- **Resource Efficient**: Reuses compiled binary for all tests
- **Error Propagation**: Compilation errors affect all tests (as expected)
- **Individual Test Results**: Each configuration gets its own result

## 支援的語言和特性

### C 語言
- 標準: c89, c99, c11, c17, c23
- 預設標準: c11
- 編譯器: GCC
- 特性: 指針操作、記憶體管理

### C++ 語言  
- 標準: cpp98, cpp03, cpp11, cpp14, cpp17, cpp20, cpp23
- 預設標準: cpp17
- 編譯器: G++
- 特性: STL、模板、現代 C++ 特性

### Python 語言
- 版本: 3.9, 3.10, 3.11, 3.12, 3.13
- 預設版本: 3.12
- 解釋器: CPython
- 特性: 類型提示、動態語言特性、豐富的標準庫

### 支援的數據類型
- 基本類型: int, float, double, char, string
- 陣列類型: array_int, array_float, array_char
- 返回類型: int, float, double, char, string, void

## 配置選項

### 編譯器設定
```json
{
  "compiler_settings": {
    "standard": "c11|cpp17",
    "flags": "-Wall -Wextra -O2",
    "optimization_level": "O2"
  }
}
```

### 資源限制
```json
{
  "resource_limits": {
    "compile_timeout": 30,
    "execution_timeout": 10,
    "memory_limit": "128m",
    "cpu_limit": 1.0
  }
}
```

## 錯誤處理

### 狀態代碼
- `SUCCESS` - 執行成功
- `COMPILE_ERROR` - 編譯錯誤
- `COMPILE_TIMEOUT` - 編譯超時
- `RUNTIME_ERROR` - 運行時錯誤
- `TIMEOUT` - 執行超時
- `ERROR` - 一般錯誤

### 錯誤回應範例
```json
{
  "status": "COMPILE_ERROR",
  "message": "編譯失敗",
  "compile_output": "error: expected ';' before '}' token",
  "metrics": {
    "compile_execution_time": 0.234
  }
}
```

## 性能指標

每次評測都會返回詳細的性能指標：

```json
{
  "metrics": {
    "total_execution_time": 0.523,
    "compile_execution_time": 0.160,
    "test_execution_time": 0.004,
    "time_ms": 3.91,
    "compile_time_ms": 159.85,
    "cpu_utime": 0.000088,
    "cpu_stime": 0.000176,
    "maxrss_mb": 2.56
  }
}
```

## 安全特性

1. **代碼安全檢查**: 自動檢測危險函數
2. **容器隔離**: 使用 Docker 隔離執行環境
3. **網絡隔離**: 執行環境無網絡訪問
4. **資源限制**: 嚴格的時間和記憶體限制
5. **輸入驗證**: 完整的請求數據驗證

## 開發和測試

### 運行測試
```bash
# 單元測試
pytest tests/ -v

# API 功能測試
python scripts/test_api.py

# 特定語言測試
pytest tests/test_c.py -v
pytest tests/test_cpp.py -v
```

### 開發模式
```bash
# 啟動開發服務器
uvicorn judge_micro.api.main:get_app --host 0.0.0.0 --port 8000 --factory --reload --debug

# 查看日誌
tail -f logs/judge_micro.log
```

### 使用 Docker
```bash
# 構建鏡像
docker build -t judge-micro-api .

# 運行容器
docker run -p 8000:8000 -v /var/run/docker.sock:/var/run/docker.sock judge-micro-api
```

## 限制和注意事項

### 代碼限制
- 最大代碼長度: 50,000 字符
- 批量測試最大數量: 100
- 禁止使用危險函數: system, exec, fork 等

### 資源限制
- 預設編譯超時: 30 秒
- 預設執行超時: 10 秒
- 預設記憶體限制: 128MB
- 最大 CPU 使用: 1.0 核心

### 環境要求
- Docker Engine 已安裝並運行
- 支援的鏡像已下載
- 足夠的系統資源

## 故障排除

### 常見問題

1. **Docker 連接失敗**
   ```bash
   # 檢查 Docker 服務
   sudo systemctl status docker
   
   # 啟動 Docker 服務
   sudo systemctl start docker
   ```

2. **鏡像缺失**
   ```bash
   # 拉取所需鏡像
   docker pull judge-microservice-c
   docker pull judge-microservice-cpp
   ```

3. **編譯超時**
   - 增加 compile_timeout 參數
   - 檢查代碼複雜度
   - 確認系統資源充足

4. **API 無回應**
   - 檢查服務器狀態: `GET /judge/status`
   - 查看日誌文件
   - 檢查網絡連接

## 文檔和支援

- API 設計文檔: `docs/api_design.md`
- Python SDK 文檔: `docs/python_sdk.md`
- 使用範例: `examples/`
- 測試文件: `tests/`

## 版本信息

- API 版本: 0.0.2.dev2
- 支援的語言: C, C++
- 相容的 Docker API: v1.40+
