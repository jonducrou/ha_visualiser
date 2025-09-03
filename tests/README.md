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

### 🚀 NEW Enhanced Test Suite with Mock-Based Unit Testing
```bash
cd /path/to/ha_visualiser
python3 tests/run_pytest_suite.py
```

**Features:**
- ✅ **Mock-Based Unit Testing**: Real unit tests using pytest with mocked HA dependencies
- ✅ **Preference Management Testing**: Complete coverage of localStorage-based user preferences
- ✅ **Graph Service Logic Testing**: Core relationship detection and data validation
- ✅ **WebSocket API Testing**: Command validation, error handling, and response formatting  
- ✅ **Comprehensive Validation**: Syntax checking, linting, and file integrity tests
- ✅ **Automatic Dependency Management**: Installs pytest dependencies if missing
- ✅ **Detailed Reporting**: Test results, success rates, and actionable next steps

### Legacy Comprehensive Test Suite
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

### ✅ Enhanced Test Results (50/50)
When running `python3 tests/run_pytest_suite.py`, you should see:

**Code Validation Tests (3/3 passed):**
- ✅ **Syntax Validation**: All Python files have valid syntax
- ✅ **Code Linting**: Clean code with minimal warnings (non-blocking)
- ✅ **File Serving**: File structure and deployment validation

**Mock-Based Unit Tests (47/47 passed):**
- ✅ **Preference Management (14 tests)**: Complete localStorage functionality coverage
  - Default value handling and validation
  - Data parsing (boolean, integer, string) with edge cases  
  - Cross-session persistence simulation
  - Error handling and fallback scenarios
- ✅ **Graph Service Logic (23 tests)**: Core business logic validation
  - Data structure validation (nodes, edges, results)
  - Entity ID patterns and special prefixes (device:, area:, zone., label:)
  - Parameter validation (depth, filters, show_areas)
  - Relationship type categorization
  - JSON serialization compatibility
- ✅ **WebSocket API Handlers (10 tests)**: Command processing and response validation
  - Command schema validation for all 4 WebSocket endpoints
  - Defensive data validation patterns (v0.8.10 fix validation)
  - Error response structure and handling
  - Data serialization for JSON transmission

**Overall Result: 50/50 passed = 🎉 All tests passing!**

### 🎯 v0.8.11 Feature Verification
All major features verified through unit testing:
- ✅ **Persistent Preferences**: localStorage-based preference management
- ✅ **Defensive Error Handling**: "'NoneType' object is not iterable" fixes (v0.8.10)
- ✅ **Graph Building Logic**: Comprehensive relationship detection
- ✅ **WebSocket Command Processing**: All 4 API endpoints validated
- ✅ **Data Structure Integrity**: Safe JSON serialization and transmission

## Archive Scripts

The archived scripts are historical documentation of bugs and their fixes. They're kept for:
- Understanding the evolution of the codebase
- Reference for similar issues
- Documentation of testing approaches used during development

These scripts generally follow the pattern:
1. Describe the original problem
2. Show the fix that was applied
3. Demonstrate the expected behavior after the fix