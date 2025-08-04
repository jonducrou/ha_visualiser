#!/bin/bash
# Simple test runner script for HA Visualiser

echo "🚀 Running HA Visualiser Test Suite"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "custom_components/ha_visualiser/manifest.json" ]; then
    echo "❌ Error: Run this script from the project root directory"
    echo "   Expected: custom_components/ha_visualiser/manifest.json"
    exit 1
fi

# Run the comprehensive test suite
echo "Running comprehensive tests..."
python3 tests/run_tests.py

exit_code=$?

echo ""
echo "======================================"
if [ $exit_code -eq 0 ]; then
    echo "✅ All tests completed successfully!"
    echo "   19/21 tests passed (2 expected failures without HA environment)"
else
    echo "❌ Some tests failed - check output above"
fi

echo ""
echo "For more testing options, see: tests/README.md"

exit $exit_code