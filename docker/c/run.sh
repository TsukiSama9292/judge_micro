#!/bin/bash

# 純淨版

make build

./harness config.json result.json

cat result.json | jq '.' 2>/dev/null || cat result.json