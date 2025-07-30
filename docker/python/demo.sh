#!/bin/bash

# Python OJ Runner Demo Script
# This script demonstrates the auto-generated result filename feature

echo "=== Python OJ Runner Demo ==="
echo

# Backup original user.py
if [ -f user.py ]; then
    cp user.py user_original_backup.py
fi

# Test 1: Basic integer manipulation (auto-generated filename)
echo "Test 1: Basic integer manipulation (auto-generated result file)"
echo "Config: config.json"
echo "User code: user.py"
python3 harness.py config.json
echo "Result:"
cat result_user.json | python3 -m json.tool 2>/dev/null || cat result_user.json
echo
echo "---"
echo

# Test 2: List processing (auto-generated result file)
echo "Test 2: List processing (auto-generated result file)"
echo "Config: config_list.json"
echo "User code: user_list.py"
cp user_list.py user.py
python3 harness.py config_list.json
echo "Result:"
cat result_user.json | python3 -m json.tool 2>/dev/null || cat result_user.json
echo
echo "---"
echo

# Test 3: Factorial calculation (auto-generated result file)
echo "Test 3: Factorial calculation (auto-generated result file)"
echo "Config: config_factorial.json"
echo "User code: user_factorial.py"
cp user_factorial.py user.py
python3 harness.py config_factorial.json
echo "Result:"
cat result_user.json | python3 -m json.tool 2>/dev/null || cat result_user.json
echo
echo "---"
echo

# Test 4: Explicit result filename
echo "Test 4: Explicit result filename"
echo "Creating user.py with syntax error..."
echo "def solve(a: int, b: int) -> int" > user.py  # Missing colon
echo "    return a + b" >> user.py
python3 harness.py config.json result_explicit.json
echo "Result:"
cat result_explicit.json | python3 -m json.tool 2>/dev/null || cat result_explicit.json
echo
echo "---"
echo

# Test 5: Runtime error test (auto-generated result file)
echo "Test 5: Runtime error test (auto-generated result file)"
echo "Creating user.py with runtime error..."
cat > user.py << 'EOF'
def solve(a: int, b: int) -> int:
    result = a / 0  # Division by zero
    return result
EOF
python3 harness.py config.json
echo "Result:"
cat result_user.json | python3 -m json.tool 2>/dev/null || cat result_user.json
echo

# Restore original user.py
if [ -f user_original_backup.py ]; then
    mv user_original_backup.py user.py
    echo "Original user.py restored."
fi

echo "=== Demo completed ==="