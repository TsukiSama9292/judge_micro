#!/bin/bash

# 配置驅動 OJ 微服務 C++ 版本運行腳本

CONFIG_FILE=${1:-"config.json"}
RESULT_FILE=${2:-"result.json"}

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 配置文件 $CONFIG_FILE 不存在"
    exit 1
fi

echo "🚀 運行 C++ OJ 評測器"
echo "配置文件: $CONFIG_FILE"
echo "結果文件: $RESULT_FILE"
echo ""

# 編譯並運行
make build && ./harness "$CONFIG_FILE" "$RESULT_FILE"

# 顯示結果
if [ -f "$RESULT_FILE" ]; then
    echo ""
    echo "📋 評測結果:"
    echo "============"
    cat "$RESULT_FILE" | python3 -m json.tool 2>/dev/null || cat "$RESULT_FILE"
else
    echo "❌ 結果文件未生成"
    exit 1
fi
