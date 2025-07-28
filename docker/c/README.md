# 配置驅動 OJ 微服務

一個現代化的線上評測系統，基於純 C 語言實現，支援純函數式介面，完全基於配置文件驅動，無需修改任何核心代碼。

## ✨ 特色

- 🚀 **零代碼修改**：harness.c 永遠不需要修改
- 🎯 **純函數式**：用戶函數無需處理全局變數
- 📝 **配置驅動**：只需修改 config.json 即可定義新題目
- ⚡ **自動編譯**：自動生成測試代碼並編譯執行
- 📊 **詳細報告**：包含性能測量、錯誤檢測、結果驗證
- 🔧 **靈活參數**：支援任意數量的函數參數
- 💻 **純 C 實現**：無額外依賴，高性能評測
- �️ **錯誤處理**：完善的錯誤檢測和報告機制

## 🏗️ 系統架構

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用戶代碼      │    │   配置文件      │    │   評測引擎      │
│   user.c        │    │   config.json   │    │   harness.c     │
│   solve()函數   │ -> │   solve_params  │ -> │   動態生成      │
│   純函數接口    │    │   expected      │    │   編譯執行      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       v
                                              ┌─────────────────┐
                                              │   結果報告      │
                                              │   result.json   │
                                              │   性能統計      │
                                              │   錯誤檢測      │
                                              └─────────────────┘
```

## 🛠️ 環境需求

- **編譯器**: GCC (支援 C99 標準)
- **函式庫**: cJSON 函式庫
- **系統**: Linux/Unix 環境
- **工具**: Make (可選，用於自動化)

### 安裝依賴

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install gcc libcjson-dev make

# CentOS/RHEL  
sudo yum install gcc cjson-devel make

# 驗證安裝
gcc --version
pkg-config --cflags --libs libcjson
```

## 🚀 快速開始

### 方法一：使用演示腳本（推薦新手）

```bash
# 運行完整演示
./demo.sh
```

### 方法二：手動步驟

#### 步驟 1：編譯 harness

```bash
# 基本編譯
gcc harness.c -o harness -lcjson

# 或使用 Makefile（推薦）
make build
```

#### 步驟 2：創建配置文件

創建 `config.json`（支援語言版本參數）：

```json
{
  "solve_params": [
    {"name": "a", "input_value": 3},
    {"name": "b", "input_value": 4}
  ],
  "expected": {"a": 6, "b": 9},
  "c_standard": "c11",
  "compiler_flags": "-Wall -Wextra -O2"
}
```

**新增支援的語言版本參數：**
- `c_standard`：指定 C 標準 (c89, c99, c11, c17, c23)
- `compiler_flags`：自定義編譯器標誌

創建 `config.json`：

```json
{
  "solve_params": [
    {"name": "a", "input_value": 3},
    {"name": "b", "input_value": 4}
  ],
  "expected": {"a": 6, "b": 9}
}
```

#### 步驟 3：實現用戶函數

創建 `user.c`：

```c
int solve(int *a, int *b) {
    *a = *a * 2;    // a: 3 -> 6
    *b = *b + 5;    // b: 4 -> 9
    return 0;       // 返回 0 表示成功
}
```

#### 步驟 4：運行評測

```bash
# 直接運行
./harness config.json result.json

# 查看結果
cat result.json

# 或使用 Makefile 自動化
make test
make show-result
```

### 方法三：使用 Makefile 自動化

```bash
make help          # 顯示所有可用命令
make build         # 編譯 harness
make test          # 運行基本測試
make show-result   # 顯示測試結果
make examples      # 使用範例
make clean         # 清理生成文件
```

## 📋 配置文件格式

### config.json 結構

```json
{
  "solve_params": [
    {"name": "參數名", "input_value": 輸入值},
    {"name": "參數名", "input_value": 輸入值}
  ],
  "expected": {
    "參數名": 期望值,
    "參數名": 期望值
  }
}
```

### 參數說明

- **solve_params**: 函數參數定義陣列
  - **name**: 參數名稱（必須是有效的 C 變數名）
  - **input_value**: 參數的初始值（整數）
- **expected**: 期望的輸出值（鍵為參數名，值為期望的整數）

### 配置範例

#### 單參數配置
```json
{
  "solve_params": [
    {"name": "result", "input_value": 5}
  ],
  "expected": {"result": 25}
}
```

#### 多參數配置
```json
{
  "solve_params": [
    {"name": "x", "input_value": 10},
    {"name": "y", "input_value": 20},
    {"name": "sum", "input_value": 0}
  ],
  "expected": {"x": 10, "y": 20, "sum": 30}
}
```

## 💻 用戶函數規範

### 函數簽名要求

```c
int solve(int *param1, int *param2, ..., int *paramN);
```

### 規則說明

1. **函數名必須是 `solve`**
2. **所有參數都是 `int*` 指標**
3. **返回值為 `int`**（0 表示成功，非 0 表示錯誤）
4. **輸入值通過指標傳遞，修改後作為輸出**
5. **參數數量必須與 config.json 中的 solve_params 數量一致**
6. **參數順序必須與 config.json 中的 solve_params 順序一致**

### 實現範例

#### 基本數學運算
```c
// 對應配置：{"name": "x", "input_value": 5}
int solve(int *x) {
    *x = *x * *x;  // 計算平方：5 -> 25
    return 0;      // 成功
}
```

#### 多參數處理
```c
// 對應配置：[{"name": "a", "input_value": 3}, {"name": "b", "input_value": 4}]
int solve(int *a, int *b) {
    *a = *a * 2;   // a: 3 -> 6
    *b = *b + 5;   // b: 4 -> 9
    return 0;
}
```

#### 錯誤處理
```c
int solve(int *a, int *b) {
    // 輸入驗證
    if (*a < 0 || *b < 0) {
        return -1;  // 錯誤：負數輸入
    }
    
    // 主要邏輯
    *a = *a + *b;
    *b = *a - *b;
    return 0;  // 成功
}
```

## 📊 結果報告格式

運行完成後，`result.json` 包含以下信息：

```json
{
  "return_code": 0,
  "outputs": [6, 9],
  "expected": [6, 9],
  "status": "PASS",
  "stdout": "{\"return_code\":0,\"outputs\":[6,9]}\n",
  "time_sec": 0.0034,
  "cpu_utime": 0.000385,
  "cpu_stime": 0,
  "maxrss_mb": 1.54
}
```

### 欄位說明

- **return_code**: 用戶函數的返回值（0=成功）
- **outputs**: 實際輸出值陣列
- **expected**: 期望輸出值陣列
- **status**: 測試狀態（PASS/FAIL/ERROR）
- **stdout**: 程式標準輸出（JSON 格式）
- **time_sec**: 總執行時間（秒）
- **cpu_utime**: 用戶模式 CPU 時間
- **cpu_stime**: 系統模式 CPU 時間
- **maxrss_mb**: 最大記憶體使用量（MB）

### 狀態判定

- **PASS**: 所有輸出值與期望值匹配
- **FAIL**: 輸出值與期望值不匹配
- **ERROR**: 程式執行錯誤或返回非零值

## 📚 完整範例

### 範例 1：基本數學運算

**config.json**
```json
{
  "solve_params": [
    {"name": "result", "input_value": 5}
  ],
  "expected": {"result": 25}
}
```

**user.c**
```c
int solve(int *result) {
    *result = *result * *result;  // 計算平方
    return 0;
}
```

**執行與結果**
```bash
$ ./harness config.json result.json
$ cat result.json
{
  "return_code": 0,
  "outputs": [25],
  "expected": [25],
  "status": "PASS",
  "time_sec": 0.001234
}
```

### 範例 2：多參數計算

**config.json**
```json
{
  "solve_params": [
    {"name": "sum", "input_value": 0},
    {"name": "product", "input_value": 1}
  ],
  "expected": {"sum": 15, "product": 120}
}
```

**user.c**
```c
int solve(int *sum, int *product) {
    // 計算 1+2+3+4+5 和 1*2*3*4*5
    for (int i = 1; i <= 5; i++) {
        *sum += i;
        *product *= i;
    }
    return 0;
}
```

### 範例 3：錯誤處理

**config_error.json**
```json
{
  "solve_params": [
    {"name": "a", "input_value": -5},
    {"name": "b", "input_value": 3}
  ],
  "expected": {"a": -2, "b": -5}
}
```

**user.c**
```c
int solve(int *a, int *b) {
    if (*a < 0 || *b < 0) {
        return -1;  // 錯誤：負數輸入
    }
    
    *a = *a + *b;
    *b = *a - *b;
    return 0;
}
```

**結果**
```json
{
  "return_code": -1,
  "outputs": [-5, 3],
  "expected": [-2, -5],
  "status": "ERROR"
}
```

## 🔧 進階使用

### 自動化腳本

**創建 auto_judge.sh**
```bash
#!/bin/bash
# 自動化評測腳本

CONFIG="${1:-config.json}"
USER_CODE="${2:-user.c}"
RESULT_FILE="${3:-result.json}"

echo "🚀 自動化 OJ 評測系統"
echo "配置文件: $CONFIG"
echo "用戶代碼: $USER_CODE"
echo "=========================="

# 編譯 harness（如果不存在）
if [ ! -f harness ]; then
    echo "🔧 編譯 harness..."
    gcc harness.c -o harness -lcjson || exit 1
fi

# 運行評測
echo "⚡ 運行評測..."
./harness "$CONFIG" "$RESULT_FILE"

# 顯示結果
if [ -f "$RESULT_FILE" ]; then
    echo "📊 評測結果:"
    cat "$RESULT_FILE"
    
    # 提取狀態
    STATUS=$(cat "$RESULT_FILE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    case "$STATUS" in
        "PASS") echo "✅ 測試通過!" ;;
        "FAIL") echo "❌ 測試失敗!" ;;
        *) echo "⚠️  執行錯誤!" ;;
    esac
else
    echo "❌ 結果文件未生成"
    exit 1
fi
```

**使用方法**
```bash
chmod +x auto_judge.sh
./auto_judge.sh                           # 使用默認文件
./auto_judge.sh config_advanced.json user_advanced.c
```

### 批量測試

**創建 batch_test.sh**
```bash
#!/bin/bash
# 批量測試腳本

echo "🔄 批量測試開始"
TOTAL=0
PASSED=0

for config in config_*.json; do
    if [ -f "$config" ]; then
        test_name=$(basename "$config" .json)
        user_file="user_${test_name#config_}.c"
        result_file="result_${test_name#config_}.json"
        
        echo "📝 測試: $test_name"
        
        if [ -f "$user_file" ]; then
            ./harness "$config" "$result_file" 2>/dev/null
            
            if [ -f "$result_file" ]; then
                status=$(grep -o '"status":"[^"]*"' "$result_file" | cut -d'"' -f4)
                if [ "$status" = "PASS" ]; then
                    echo "   結果: ✅ PASS"
                    PASSED=$((PASSED + 1))
                else
                    echo "   結果: ❌ $status"
                fi
            else
                echo "   結果: ❌ NO_RESULT"
            fi
        else
            echo "   結果: ⚠️  NO_CODE"
        fi
        
        TOTAL=$((TOTAL + 1))
    fi
done

echo "📊 批量測試結果:"
echo "   總計: $TOTAL"
echo "   通過: $PASSED"
echo "   失敗: $((TOTAL - PASSED))"
if [ $TOTAL -gt 0 ]; then
    echo "   成功率: $((PASSED * 100 / TOTAL))%"
fi
```

### 性能基準測試

**創建 benchmark.sh**
```bash
#!/bin/bash
# 性能基準測試

USER_CODE="${1:-user.c}"
CONFIG="${2:-config.json}"
RUNS="${3:-10}"

echo "🔬 性能測試: $USER_CODE (運行 $RUNS 次)"

for i in $(seq 1 $RUNS); do
    echo -n "  運行 $i/$RUNS... "
    
    start_time=$(date +%s.%N)
    ./harness "$CONFIG" "result_bench.json" 2>/dev/null
    end_time=$(date +%s.%N)
    
    wall_time=$(echo "$end_time - $start_time" | bc)
    
    if [ -f "result_bench.json" ]; then
        status=$(grep -o '"status":"[^"]*"' "result_bench.json" | cut -d'"' -f4)
        time_sec=$(grep -o '"time_sec":[0-9.]*' "result_bench.json" | cut -d':' -f2)
        echo "✅ $status (牆鐘: ${wall_time}s, CPU: ${time_sec}s)"
    else
        echo "❌ FAILED"
    fi
done

rm -f result_bench.json
```

## 🐛 故障排除

### 常見編譯錯誤

**錯誤：cJSON 庫未找到**
```bash
harness.c:1:10: fatal error: cjson/cJSON.h: No such file or directory
```

**解決方案：**
```bash
# Ubuntu/Debian
sudo apt-get install libcjson-dev

# 檢查安裝
pkg-config --cflags --libs libcjson

# 手動指定路徑
gcc harness.c -o harness -I/usr/include/cjson -lcjson
```

### 常見運行錯誤

**錯誤：配置文件不存在**
```bash
Error: Cannot open config file: config.json
```

**解決方案：**
```bash
# 檢查文件存在
ls -la config.json

# 檢查 JSON 格式
cat config.json | python3 -m json.tool
```

**錯誤：用戶函數未找到**
```bash
/tmp/test_main.c: undefined reference to `solve'
```

**解決方案：**
```bash
# 檢查函數定義
grep -n "solve" user.c

# 檢查函數簽名是否正確
# 確保參數數量與配置文件匹配
```

### 除錯工具

**創建 debug_helper.sh**
```bash
#!/bin/bash
echo "🔍 OJ 系統除錯助手"
echo "=================="

# 檢查環境
echo "📋 環境檢查:"
echo "GCC: $(gcc --version 2>/dev/null | head -1 || echo '未安裝')"
echo "cJSON: $(pkg-config --modversion libcjson 2>/dev/null || echo '未安裝')"

# 檢查文件
echo -e "\n📁 文件檢查:"
for file in harness.c harness config.json user.c; do
    echo "$file: $([ -f "$file" ] && echo '✅' || echo '❌')"
done

# 檢查配置文件
if [ -f config.json ]; then
    echo -e "\n⚙️  配置文件檢查:"
    if python3 -m json.tool config.json >/dev/null 2>&1; then
        echo "JSON 格式: ✅"
    else
        echo "JSON 格式: ❌"
    fi
fi

# 檢查用戶代碼
if [ -f user.c ]; then
    echo -e "\n💻 用戶代碼檢查:"
    if grep -q "int solve(" user.c; then
        echo "solve 函數: ✅"
    else
        echo "solve 函數: ❌"
    fi
fi
```

## 🎯 最佳實踐

### 1. 配置文件組織

```bash
# 按難度分類
config_easy_square.json
config_medium_factorial.json
config_hard_matrix.json

# 按主題分類
config_math_basic.json
config_algorithm_sort.json
config_datastructure_tree.json
```

### 2. 錯誤處理策略

```c
int solve(int *a, int *b) {
    // 1. 輸入驗證
    if (a == NULL || b == NULL) return -1;
    if (*a < 0 || *b < 0) return -2;
    
    // 2. 邊界檢查
    if (*a > 1000000 || *b > 1000000) return -3;
    
    // 3. 主要邏輯
    *a = *a + *b;
    *b = *a - *b;
    
    return 0;  // 成功
}
```

### 3. 性能優化建議

- 避免不必要的計算
- 使用適當的演算法時間複雜度
- 注意記憶體使用效率
- 利用編譯器優化：`gcc -O2 harness.c -o harness -lcjson`

## 📝 擴展功能

### 與 runner.py 集成

如果需要多語言支援，可以使用附帶的 `runner.py`：

```bash
# 使用 Python 介面調用 harness
python3 runner.py --filename user.c --use-harness --cleanup
```

詳細的 runner.py 使用方法請參考 `MICROSERVICE_GUIDE.md`。

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

### 開發環境設置

```bash
# 克隆項目
git clone <repository-url>
cd config-driven-oj

# 安裝依賴
sudo apt-get install gcc libcjson-dev

# 編譯測試
make build
make test
```

## 📄 授權

MIT License

---

## 📞 支援

如有問題，請查看故障排除章節或提交 Issue。

**主要文件說明：**
- `harness.c` - 核心評測引擎
- `config.json` - 題目配置文件
- `user.c` - 用戶實現文件
- `Makefile` - 編譯自動化
- `demo.sh` - 演示腳本
- `runner.py` - 多語言擴展（可選）

### runner.py 微服務接口

runner.py 提供了強大的多語言評測能力，支援以下語言：

- **C/C++**: 自動編譯並執行
- **Java**: 編譯 .java 並執行 class 文件
- **Python**: 直接執行 .py 文件
- **JavaScript**: 使用 Node.js 執行
- **Rust**: 編譯 .rs 文件
- **Go**: 編譯並執行 Go 程序
- **C#**: 使用 .NET Core 編譯執行
- **Ruby/PHP**: 直接執行腳本

### API 調用方式

#### 1. 命令行調用

```bash
# 基本用法
python3 runner.py --filename user.c

# 使用 harness 模式（推薦用於 OJ）
python3 runner.py --filename user.c --use-harness --cleanup

# 指定數據庫（用於 SQL 評測）
python3 runner.py --filename script.sql --db database.db

# 完整參數說明
python3 runner.py \
    --filename user.c \           # 源代碼文件
    --use-harness \              # 使用 harness 評測模式
    --cleanup \                  # 執行後清理編譯產物
    --db test.db                 # 數據庫文件（SQL 用）
```

#### 2. Python API 調用

```python
from runner import auto_compile_and_run, measure

# 評測 C 代碼（使用 harness）
result = auto_compile_and_run(
    src_path="user.c", 
    db="test.db", 
    use_harness=True,    # 使用配置驅動的 harness
    cleanup=True         # 自動清理
)

# 評測其他語言
python_result = auto_compile_and_run("solution.py", "test.db")
java_result = auto_compile_and_run("Solution.java", "test.db", cleanup=True)

# 直接執行命令並測量性能
cmd_result = measure("./my_program < input.txt")
```

#### 3. HTTP 微服務封裝（擴展用法）

```python
# 可以基於 runner.py 創建 Flask/FastAPI 微服務
from flask import Flask, request, jsonify
from runner import auto_compile_and_run
import tempfile
import os

app = Flask(__name__)

@app.route('/evaluate', methods=['POST'])
def evaluate_code():
    data = request.json
    code = data.get('code')
    language = data.get('language', 'c')
    
    # 創建臨時文件
    with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{language}', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        # 評測代碼
        result = auto_compile_and_run(
            src_path=temp_file,
            db="test.db",
            use_harness=(language == 'c'),
            cleanup=True
        )
        return jsonify(result)
    finally:
        # 清理臨時文件
        os.unlink(temp_file)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 返回結果格式

runner.py 的返回結果包含豐富的執行信息：

```json
{
  "stage": "run",                    // 執行階段：compile/run
  "stdout": "{\"return_code\":0,\"outputs\":[6,9]}\n", // 標準輸出（正確格式）
  "stderr": "",                      // 標準錯誤（應該為空）
  "returncode": 0,                   // 返回碼（0表示成功）
  "time_wall_sec": 0.0034,          // 牆鐘時間（秒）
  "cpu_utime": 0.000385,            // 用戶 CPU 時間
  "cpu_stime": 0,                   // 系統 CPU 時間
  "maxrss_mb": 1.54,                // 最大記憶體使用（MB）
  
  // 以下欄位僅在 use_harness=True 時出現
  "return_code": 0,                 // harness 返回碼
  "outputs": [6, 9],                // 實際輸出值
  "expected": [6, 9],               // 期望輸出值
  "status": "PASS"                  // 測試狀態（PASS/FAIL/ERROR）
}
```

**注意事項：**
- `returncode` 和 `status` 應該一致：returncode=0 對應 status="PASS"
- `stderr` 在正常情況下應該為空
- `stdout` 包含程序的標準輸出，格式正確無雙重轉義
```

### 錯誤處理

```python
result = auto_compile_and_run("user.c", "test.db", use_harness=True)

if result.get("stage") == "compile" and result.get("returncode") != 0:
    print("編譯錯誤:", result.get("stderr"))
elif result.get("stage") == "run":
    if result.get("status") == "PASS":
        print("測試通過!")
    elif result.get("status") == "FAIL":
        print("測試失敗:", result.get("outputs"), "vs", result.get("expected"))
    else:
        print("執行錯誤:", result.get("stderr"))
```

## 📋 配置文件格式

### config.json 結構

```json
{
  "solve_params": [
    {"name": "參數名", "input_value": 輸入值},
    ...
  ],
  "expected": {
    "參數名": 期望值,
    ...
  }
}
```

### 參數說明

- **solve_params**: 函數參數定義陣列
  - **name**: 參數名稱（必須是有效的 C 變數名）
  - **input_value**: 參數的初始值
- **expected**: 期望的輸出值（鍵為參數名）

## 💻 函數規範

### 函數簽名

```c
int solve(int *param1, int *param2, ..., int *paramN);
```

### 規則

1. **函數名必須是 `solve`**
2. **所有參數都是 `int*` 指標**
3. **返回值為 `int`**（0 表示成功）
4. **輸入值通過指標傳遞，修改後作為輸出**

### 範例

```c
// 2個參數的情況
int solve(int *a, int *b) {
    *a = *a * 2;
    *b = *b + 5;
    return 0;
}

// 3個參數的情況
int solve(int *x, int *y, int *z) {
    *x = *x * *x;  // 平方
    *y = *y * *y;
    *z = *z * *z;
    return 0;
}
```

## 📊 結果報告格式

運行完成後，`result.json` 包含以下信息：

```json
{
  "return_code": 0,
  "outputs": [6, 9],
  "expected": [6, 9],
  "status": "PASS",
  "stdout": "{\"return_code\":0,\"outputs\":[6,9]}\n",
  "time_sec": 0.0034,
  "cpu_utime": 0.000385,
  "cpu_stime": 0,
  "maxrss_mb": 1.54
}
```

### 欄位說明

- **return_code**: 用戶函數的返回值
- **outputs**: 實際輸出值陣列
- **expected**: 期望輸出值陣列
- **status**: 測試狀態（PASS/FAIL/ERROR）
- **stdout**: 程式標準輸出
- **time_sec**: 總執行時間（秒）
- **cpu_utime**: 用戶模式 CPU 時間
- **cpu_stime**: 系統模式 CPU 時間
- **maxrss_mb**: 最大記憶體使用量（MB）

## 📚 完整範例

### 範例 1：基本數學運算（直接 harness 模式）

**config.json**
```json
{
  "solve_params": [
    {"name": "result", "input_value": 5}
  ],
  "expected": {"result": 25}
}
```

**user.c**
```c
int solve(int *result) {
    *result = *result * *result;  // 計算平方
    return 0;
}
```

**執行命令**
```bash
gcc harness.c -o harness -lcjson
./harness config.json result.json
cat result.json
```

### 範例 2：多參數計算（runner.py 模式）

**config.json**
```json
{
  "solve_params": [
    {"name": "sum", "input_value": 0},
    {"name": "product", "input_value": 1}
  ],
  "expected": {"sum": 15, "product": 120}
}
```

**user.c**
```c
int solve(int *sum, int *product) {
    // 計算 1+2+3+4+5 和 1*2*3*4*5
    for (int i = 1; i <= 5; i++) {
        *sum += i;
        *product *= i;
    }
    return 0;
}
```

**執行命令**
```bash
python3 runner.py --filename user.c --use-harness --cleanup
```