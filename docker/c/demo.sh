#!/bin/bash
# 簡單演示腳本

echo "🎯 C 語言配置驅動 OJ 微服務演示"
echo "================================"

# 確保 harness 已編譯
if [ ! -f harness ]; then
    echo "📦 編譯 harness..."
    make build
fi

echo ""
echo "📝 當前用戶代碼 (user.c):"
cat user.c

echo ""
echo "⚙️  當前配置 (config.json):"
cat config.json

echo ""
echo "🚀 運行測試..."
./harness config.json result.json

echo ""
echo "📊 測試結果:"
cat result.json | jq '.' 2>/dev/null || cat result.json

status=$(cat result.json | grep status | grep -o 'SUCCESS\|ERROR')
if [ "$status" = "SUCCESS" ]; then
    echo ""
    echo "✅ 測試通過！"
else
    echo ""
    echo "❌ 測試失敗"
fi
