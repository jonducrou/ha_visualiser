# Tests Directory

This directory contains all testing and debugging scripts for the HA Visualiser project.

## Directory Structure

### `/tests/` (Root)
- **`test_graph_service.py`** - Main unit tests for the graph service
- **`test_runner.py`** - Test runner script that executes all tests  
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

### Unit Tests
```bash
cd /path/to/ha_visualiser
python tests/test_runner.py
```

### Code Validation
```bash
python tests/validate_code.py
```

### File Serving Test
```bash
cd /path/to/ha_visualiser
bash tests/test_file_serving.sh
```

### WebSocket API Testing
1. Open `tests/integration/test_websocket_commands.html` in browser
2. Follow instructions in the HTML page

## Archive Scripts

The archived scripts are historical documentation of bugs and their fixes. They're kept for:
- Understanding the evolution of the codebase
- Reference for similar issues
- Documentation of testing approaches used during development

These scripts generally follow the pattern:
1. Describe the original problem
2. Show the fix that was applied
3. Demonstrate the expected behavior after the fix