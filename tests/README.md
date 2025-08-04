# Tests Directory

This directory contains all testing and debugging scripts for the HA Visualiser project.

## Directory Structure

### `/tests/` (Root)
- **`test_graph_service.py`** - Main unit tests for the graph service
- **`test_runner.py`** - Legacy test runner script (basic functionality)
- **`run_tests.py`** - **NEW** Comprehensive test runner with dependency handling
- **`validate_code.py`** - Code syntax validation and structure checks
- **`test_file_serving.sh`** - Shell script to test file serving and deployment

### `/tests/integration/`
- **`test_websocket_commands.html`** - Interactive HTML page for testing WebSocket API commands

### `/tests/debugging/`
- **`debug_integration.py`** - Debug helper for integration testing
- **`debug_zones.py`** - Debug script for zone detection and relationships
- **`debug_frontend.html`** - Frontend debugging interface

### `/tests/archive/`
Historical test scripts that document issues that have been fixed:
- **`test_2level_fix.py`** - Documents 2-level depth bug fix (v0.2.3)
- **`test_area_fix.py`** - Documents area relationship fixes 
- **`test_arrow_consistency.py`** - Documents arrow direction consistency fixes
- **`test_symmetrical_relationships.py`** - Documents symmetrical relationship fixes (v0.2.5)
- **`test_container_fix.py`** - Documents container relationship fixes
- **`test_fixes.py`** - General fix documentation
- And more...

## Running Tests

### 🚀 NEW Comprehensive Test Suite
```bash
cd /path/to/ha_visualiser
python3 tests/run_tests.py
```

**Features:**
- ✅ Dependency detection and handling
- ✅ Code structure verification  
- ✅ Feature implementation validation (v0.6.0)
- ✅ Syntax checking for all Python files
- ✅ Integration configuration validation
- ⚠️ Graceful handling of missing HA dependencies

### Legacy Tests
```bash
# Basic unit tests (legacy)
python tests/test_runner.py

# Code validation
python tests/validate_code.py

# File serving test
bash tests/test_file_serving.sh
```

### WebSocket API Testing
1. Open `tests/integration/test_websocket_commands.html` in browser
2. Follow instructions in the HTML page

## Test Results & Interpretation

### ✅ Expected Pass Results (19/21)
When running `python3 tests/run_tests.py`, you should see:

**Code Structure (12/12 passed):**
- All integration files exist and are accessible
- Version correctly updated to 0.6.0 in manifest.json
- Default depth parameter set to 3 in backend
- Conditional relationship direction fixed (entity → automation)
- Frontend depth control properly implemented
- Reset button functionality corrected
- Canvas expansion and UI improvements verified

**Configuration & Syntax (7/7 passed):**
- All Python files have valid syntax
- Manifest.json has required fields and correct domain
- HACS configuration is valid JSON

### ⚠️ Expected Failures (2/21)
**These failures are normal without Home Assistant environment:**
- Graph service import test (requires HA modules)
- WebSocket API import test (requires HA components)

**Overall Result: 19/21 passed = ✅ All critical tests passing**

### 🎯 v0.6.0 Feature Verification
All major v0.6.0 features verified:
- ✅ Configurable depth (1-5 levels, default 3)
- ✅ Fixed conditional relationship semantics
- ✅ Inline depth control in search bar
- ✅ Proper reset button behavior (layout vs data)
- ✅ Expanded canvas utilizing full viewport
- ✅ Version consistency across all files

## Archive Scripts

The archived scripts are historical documentation of bugs and their fixes. They're kept for:
- Understanding the evolution of the codebase
- Reference for similar issues
- Documentation of testing approaches used during development

These scripts generally follow the pattern:
1. Describe the original problem
2. Show the fix that was applied
3. Demonstrate the expected behavior after the fix