#!/bin/bash

# 配置驅動 OJ 微服務 C++ 版本演示腳本

set -e

echo "🎯 配置驅動 OJ 微服務 C++ 版本演示"
echo "===================================="
echo ""

# 檢查環境
echo "🔍 檢查編譯環境..."
if ! command -v g++ &> /dev/null; then
    echo "❌ g++ 編譯器未找到，請安裝 g++"
    exit 1
fi

# 檢查 C++17 支持
echo 'int main() { auto x = 42; return 0; }' | g++ -std=c++17 -x c++ - -o /tmp/cpp17_test 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ C++17 支持正常"
    rm -f /tmp/cpp17_test
else
    echo "❌ C++17 支持有問題，請檢查編譯器版本"
    exit 1
fi

echo ""

# 編譯 harness
echo "🔨 編譯 harness..."
make build
echo ""

# 演示 1: 基本數學運算
echo "🧮 演示 1: 基本數學運算"
echo "======================="
echo "配置文件: config.json"
echo "用戶代碼: user.cpp"
echo ""

# 確保使用默認用戶代碼
if [ ! -f user.cpp ]; then
    echo "❌ 找不到 user.cpp，請確保文件存在"
    exit 1
fi

./harness config.json result_demo1.json
echo "結果:"
cat result_demo1.json | python3 -m json.tool 2>/dev/null || cat result_demo1.json
echo ""
echo ""

# 演示 2: 字符串處理
echo "📝 演示 2: 字符串處理"
echo "===================="
echo "配置文件: config_string.json"
echo "用戶代碼: user_string.cpp"
echo ""

if [ -f user_string.cpp ]; then
    cp user_string.cpp user.cpp
    ./harness config_string.json result_demo2.json
    echo "結果:"
    cat result_demo2.json | python3 -m json.tool 2>/dev/null || cat result_demo2.json
    echo ""
    echo ""
else
    echo "⚠️  跳過字符串處理演示（user_string.cpp 不存在）"
fi

# 演示 3: 容器操作
echo "📊 演示 3: 容器操作"
echo "=================="
echo "配置文件: config_vector.json"
echo "用戶代碼: user_vector.cpp"
echo ""

if [ -f user_vector.cpp ]; then
    cp user_vector.cpp user.cpp
    ./harness config_vector.json result_demo3.json
    echo "結果:"
    cat result_demo3.json | python3 -m json.tool 2>/dev/null || cat result_demo3.json
    echo ""
    echo ""
else
    echo "⚠️  跳過容器操作演示（user_vector.cpp 不存在）"
fi

# 演示 4: 階乘計算
echo "🔢 演示 4: 階乘計算"
echo "=================="
echo "配置文件: config_factorial.json"
echo "用戶代碼: user_factorial.cpp"
echo ""

if [ -f user_factorial.cpp ]; then
    cp user_factorial.cpp user.cpp
    ./harness config_factorial.json result_demo4.json
    echo "結果:"
    cat result_demo4.json | python3 -m json.tool 2>/dev/null || cat result_demo4.json
    echo ""
    echo ""
else
    echo "⚠️  跳過階乘計算演示（user_factorial.cpp 不存在）"
fi

# 性能對比
echo "⚡ 性能測試"
echo "=========="
echo "運行 5 次基本測試以測量性能..."

# 恢復原始用戶代碼
if [ -f user.cpp.bak ]; then
    cp user.cpp.bak user.cpp
fi

total_time=0
for i in {1..5}; do
    echo -n "第 $i 次: "
    start_time=$(date +%s.%N)
    ./harness config.json result_perf.json > /dev/null 2>&1
    end_time=$(date +%s.%N)
    run_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0.001")
    total_time=$(echo "$total_time + $run_time" | bc -l 2>/dev/null || echo "$total_time")
    printf "%.3f 秒\n" $run_time
done

if command -v bc &> /dev/null; then
    avg_time=$(echo "scale=3; $total_time / 5" | bc -l)
    echo "平均時間: ${avg_time} 秒"
else
    echo "平均時間: 無法計算（需要 bc 命令）"
fi

echo ""

# 功能特性展示
echo "✨ 功能特性展示"
echo "=============="
echo ""

echo "🎯 支援的資料型別:"
echo "  • 基本型別: int, long, long long, float, double, bool"
echo "  • 字串型別: string, char"
echo "  • 容器型別: vector<T>"
echo "  • 返回型別: void, int, bool, 其他基本型別"
echo ""

echo "🔧 配置驅動特性:"
echo "  • 零代碼修改: harness.cpp 永遠不需要改動"
echo "  • 純函數介面: 無需處理全域變數"
echo "  • 自動型別推導: 支援 C++17 特性"
echo "  • 異常處理: 完善的錯誤檢測和報告"
echo ""

echo "📊 評測功能:"
echo "  • 編譯時間測量"
echo "  • 執行時間測量"
echo "  • 記憶體使用量監控"
echo "  • CPU 時間統計"
echo "  • 結果自動驗證"
echo ""

echo "🛠️  開發工具:"
echo "  • Makefile 自動化"
echo "  • 多種測試模式"
echo "  • 調試與發佈模式"
echo "  • 效能基準測試"
echo ""

# 文件清單
echo "📁 生成的文件:"
echo "============="
for file in result_demo*.json result_perf.json solve.hpp test_main.cpp test_runner; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    fi
done
echo ""

# 使用指南
echo "📖 使用指南"
echo "=========="
echo "1. 編輯 user.cpp 實現 solve 函數"
echo "2. 修改 config.json 定義輸入和期望輸出"
echo "3. 運行 'make test' 執行評測"
echo "4. 查看 result.json 獲取詳細結果"
echo ""

echo "🎉 演示完成！"
echo ""
echo "💡 提示："
echo "   • 使用 'make help' 查看所有可用命令"
echo "   • 使用 'make test-all' 運行所有示例"
echo "   • 使用 'make clean' 清理生成的文件"
echo ""
echo "🔗 更多信息請參考 README.md"
