# Linting and Code Quality

This project includes comprehensive linting tools to detect unused variables, methods, and other code quality issues.

## Available Linting Tools

### 1. Simple AST-based Linter (`lint_simple.py`)
- **No external dependencies required**
- Uses Python AST parsing for accurate analysis
- Focuses on unused variables, methods, and imports
- Filters out Home Assistant integration patterns (entry points, WebSocket handlers)
- **Recommended for CI/CD and development**

```bash
python3 lint_simple.py
```

### 2. Comprehensive Linter (`lint.py`)
- Supports external tools (pylint, ESLint) with fallback to manual analysis
- More detailed analysis when tools are available
- **Requires**: `pip install pylint` and `npm install eslint` for full functionality

```bash
python3 lint.py
```

### 3. Shell Script (`lint.sh`)
- Runs multiple linting tools in sequence
- Combines results from all available tools
- **Bash-based wrapper for comprehensive analysis**

```bash
./lint.sh
```

## Configuration Files

### Python Linting
- **`.pylintrc`**: Pylint configuration with HA integration-specific settings
- **`pyproject.toml`**: Modern Python tooling configuration (Black, isort, etc.)

### JavaScript Linting
- **`.eslintrc.json`**: ESLint configuration for frontend code
- **`package.json`**: NPM scripts for linting commands

## Integration with Tests

The test runner (`tests/run_tests.py`) automatically includes linting checks:

```bash
python3 tests/run_tests.py
```

## NPM Scripts

If you have Node.js installed, you can use these commands:

```bash
# Run all linting
npm run lint

# Python linting only
npm run lint:python  

# JavaScript linting only
npm run lint:js

# Auto-fix JavaScript issues
npm run lint:fix
```

## What Gets Detected

### ✅ **Detected Issues**
- Unused imports (with HA integration filtering)
- Unused variables and methods
- Unused functions (excluding HA entry points)
- Basic syntax issues
- Excessive console.log statements

### 🔄 **Filtered Out (False Positives)**
- Home Assistant entry points (`async_setup`, `async_setup_entry`, etc.)
- WebSocket API handlers (registered dynamically)
- Configuration flow methods (`async_step_user`)
- Common variable names (`i`, `j`, `e`, `_`, etc.)
- DOM-related JavaScript variables
- Template placeholders and CSS properties

## Current Status

Based on the latest analysis:

✅ **Python Files**: Clean (0 critical issues)
✅ **JavaScript Files**: Clean (0 critical issues) 
⚠️ **Warnings**: 2 minor false positives (safe to ignore)

## Adding New Linting Rules

To add new rules or modify filtering:

1. **Python**: Edit `lint_simple.py` → `analyze_python_file()` method
2. **JavaScript**: Edit `lint_simple.py` → `analyze_javascript_file()` method  
3. **External tools**: Modify configuration files (`.pylintrc`, `.eslintrc.json`)

## CI/CD Integration

For automated linting in CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run linting
  run: python3 lint_simple.py
```

The simple linter returns:
- **Exit code 0**: No critical issues
- **Exit code 1**: Critical issues found (should fail CI)

## Manual Code Review

The linting tools are designed to catch obvious issues, but manual code review is still important for:

- Logic errors and edge cases
- Performance optimizations  
- Architecture and design patterns
- Domain-specific Home Assistant patterns
- User experience considerations

## Development Workflow

1. **Before committing**: Run `python3 lint_simple.py`
2. **Before releases**: Run full test suite with `python3 tests/run_tests.py`
3. **For detailed analysis**: Use `./lint.sh` with external tools installed
4. **Auto-fixing**: Use `npm run lint:fix` for JavaScript formatting