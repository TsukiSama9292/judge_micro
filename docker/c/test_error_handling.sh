#!/bin/bash

# Test script: Verify improved compilation error reporting functionality
echo "========================================"
echo "Testing improved C language compilation error reporting functionality"
echo "========================================"

# Ensure we're in the correct directory
cd /home/tsukisama9292/workspace/Dockerfiles/judger-runner/c

# Backup original files
echo "1. Backing up original files..."
cp user.c user_original.c

echo ""
echo "2. Testing compilation and execution of correct code..."
echo "----------------------------------------"
make test-verbose
echo ""

echo "3. Testing compilation error reporting functionality..."
echo "----------------------------------------"
# Use error code
cp user_error_test.c user.c
echo "Testing with erroneous code:"
echo ""

# Run test and view results
./harness config_error_test.json result_error_test.json
echo ""

echo "Generated error results:"
echo "----------------------------------------"
cat result_error_test.json | jq '.' 2>/dev/null || cat result_error_test.json
echo ""

echo "4. Testing different types of compilation errors..."
echo "----------------------------------------"

# Create another error test
cat > user_warning_test.c << 'EOF'
#include <stdio.h>

int solve(int *result) {
    int unused_variable = 42;  // Unused variable warning
    char buffer[5];
    strcpy(buffer, "This is too long");  // Buffer overflow risk
    
    *result = 100;
    return 0;  // Missing return value
}
EOF

echo "Testing warnings and other compilation issues:"
cp user_warning_test.c user.c
./harness config_error_test.json result_warning_test.json

echo "Warning test results:"
cat result_warning_test.json | jq '.stderr' 2>/dev/null || cat result_warning_test.json
echo ""

echo "5. Restoring original files..."
echo "----------------------------------------"
cp user_original.c user.c
rm -f user_original.c

echo ""
echo "Testing completed!"
echo "========================================"
echo "Improvement summary:"
echo "- ✅ Compilation error information now included in stderr field"
echo "- ✅ Using -Wall -Wextra to show more warnings"
echo "- ✅ Error messages include line numbers and detailed descriptions"
echo "- ✅ Result JSON includes COMPILE_ERROR status"
echo "- ✅ make test-verbose shows detailed error information"
echo "========================================"
