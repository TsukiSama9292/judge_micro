#!/bin/bash

# Python OJ Runner - Simple execution script

make build

python3 harness.py config.json

# Show the auto-generated result
if [ -f result_user.json ]; then
    cat result_user.json | jq '.' 2>/dev/null || cat result_user.json
else
    echo "No result file found"
fi
