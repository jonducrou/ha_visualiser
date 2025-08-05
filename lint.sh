#!/bin/bash
# Comprehensive linting script for HA Visualiser
# Runs multiple linting tools and combines results

echo "🔍 HA Visualiser Comprehensive Linting"
echo "=============================================="

# Run simple AST-based linting (no dependencies)
echo "📋 Running simple code analysis..."
python3 lint_simple.py

echo ""
echo "🐍 Attempting advanced Python linting..."

# Try pylint if available
if command -v pylint &> /dev/null; then
    echo "  Running pylint..."
    pylint custom_components/ha_visualiser/*.py --rcfile=.pylintrc --score=n || true
else
    echo "  ⚠️  pylint not available (install with: pip install pylint)"
fi

# Try flake8 if available
if command -v flake8 &> /dev/null; then
    echo "  Running flake8..."
    flake8 custom_components/ha_visualiser/ --max-line-length=120 --ignore=E203,W503,E501,F401 || true
else
    echo "  ⚠️  flake8 not available (install with: pip install flake8)"
fi

echo ""
echo "🌐 Attempting JavaScript linting..."

# Try ESLint if available
if command -v npx &> /dev/null && npx eslint --version &> /dev/null; then
    echo "  Running ESLint..."
    npx eslint custom_components/ha_visualiser/www/*.js || true
else
    echo "  ⚠️  ESLint not available (install with: npm install eslint)"
fi

echo ""
echo "✅ Linting complete!"
echo "=============================================="