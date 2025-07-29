#!/bin/bash
# Simple demonstration script

echo "🎯 C Language Configuration-Driven OJ Microservice Demo"
echo "================================"

# Ensure harness is compiled
if [ ! -f harness ]; then
    echo "📦 Compiling harness..."
    make build
fi

echo ""
echo "📝 Current user code (user.c):"
cat user.c

echo ""
echo "⚙️  Current configuration (config.json):"
cat config.json

echo ""
echo "🚀 Running test..."
./harness config.json result.json

echo ""
echo "📊 Test result:"
cat result.json | jq '.' 2>/dev/null || cat result.json

status=$(cat result.json | grep status | grep -o 'SUCCESS\|ERROR')
if [ "$status" = "SUCCESS" ]; then
    echo ""
    echo "✅ Test passed!"
else
    echo ""
    echo "❌ Test failed"
fi
