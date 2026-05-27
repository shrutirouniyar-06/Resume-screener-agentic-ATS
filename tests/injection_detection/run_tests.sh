#!/bin/bash

# Prompt Injection Detection Test Suite Runner
# Run from tests/injection_detection/ directory

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../" && pwd)"

echo "======================================================================="
echo "Prompt Injection Detection Test Suite"
echo "======================================================================="
echo ""
echo "Project Root: $PROJECT_ROOT"
echo "Test Dir:     $SCRIPT_DIR"
echo ""

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed"
    exit 1
fi

echo "Python: $(python --version)"
echo ""

# Change to test directory
cd "$SCRIPT_DIR"

# Run the test runner
echo "Running tests..."
echo ""
python test_runner.py

exit $?
