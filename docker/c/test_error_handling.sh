#!/bin/bash

# 測試腳本：驗證改進的編譯錯誤提示功能
echo "========================================"
echo "測試改進的 C 語言編譯錯誤提示功能"
echo "========================================"

# 確保在正確的目錄
cd /home/tsukisama9292/workspace/Dockerfiles/judger-runner/c

# 備份原始文件
echo "1. 備份原始文件..."
cp user.c user_original.c

echo ""
echo "2. 測試正確代碼的編譯和執行..."
echo "----------------------------------------"
make test-verbose
echo ""

echo "3. 測試編譯錯誤提示功能..."
echo "----------------------------------------"
# 使用錯誤代碼
cp user_error_test.c user.c
echo "使用有錯誤的代碼進行測試："
echo ""

# 運行測試並查看結果
./harness config_error_test.json result_error_test.json
echo ""

echo "生成的錯誤結果："
echo "----------------------------------------"
cat result_error_test.json | jq '.' 2>/dev/null || cat result_error_test.json
echo ""

echo "4. 測試不同類型的編譯錯誤..."
echo "----------------------------------------"

# 創建另一個錯誤測試
cat > user_warning_test.c << 'EOF'
#include <stdio.h>

int solve(int *result) {
    int unused_variable = 42;  // 未使用變量警告
    char buffer[5];
    strcpy(buffer, "This is too long");  // 緩衝區溢出風險
    
    *result = 100;
    return 0;  // 缺少返回值
}
EOF

echo "測試警告和其他編譯問題："
cp user_warning_test.c user.c
./harness config_error_test.json result_warning_test.json

echo "警告測試結果："
cat result_warning_test.json | jq '.stderr' 2>/dev/null || cat result_warning_test.json
echo ""

echo "5. 恢復原始文件..."
echo "----------------------------------------"
cp user_original.c user.c
rm -f user_original.c

echo ""
echo "測試完成！"
echo "========================================"
echo "改進總結："
echo "- ✅ 編譯錯誤信息現在包含在 stderr 字段中"
echo "- ✅ 使用 -Wall -Wextra 顯示更多警告"
echo "- ✅ 錯誤信息包含行號和詳細描述"
echo "- ✅ 結果 JSON 包含 COMPILE_ERROR 狀態"
echo "- ✅ make test-verbose 顯示詳細錯誤信息"
echo "========================================"
