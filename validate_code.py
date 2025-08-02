#!/usr/bin/env python3
"""Code validation script for syntax and basic structure checks."""

import ast
import sys
from pathlib import Path

def validate_python_syntax(file_path):
    """Validate Python syntax of a file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        ast.parse(content)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def validate_integration():
    """Validate the integration files."""
    print("=== HA Visualiser Code Validation ===\n")
    
    files_to_check = [
        'custom_components/ha_visualiser/__init__.py',
        'custom_components/ha_visualiser/graph_service.py', 
        'custom_components/ha_visualiser/config_flow.py',
        'custom_components/ha_visualiser/websocket_api.py',
        'custom_components/ha_visualiser/const.py'
    ]
    
    all_valid = True
    
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            valid, message = validate_python_syntax(path)
            status = "✓" if valid else "✗"
            print(f"{status} {file_path}: {message}")
            if not valid:
                all_valid = False
        else:
            print(f"? {file_path}: File not found")
    
    # Check manifest.json
    manifest_path = Path('custom_components/ha_visualiser/manifest.json')
    if manifest_path.exists():
        try:
            import json
            with open(manifest_path) as f:
                json.load(f)
            print(f"✓ {manifest_path}: Valid JSON")
        except json.JSONDecodeError as e:
            print(f"✗ {manifest_path}: Invalid JSON - {e}")
            all_valid = False
    
    print(f"\n=== Summary ===")
    if all_valid:
        print("✓ All syntax checks passed!")
        print("\nNext steps for testing:")
        print("1. Install pytest: pip install -r requirements-test.txt")
        print("2. Run unit tests: python -m pytest tests/")
        print("3. Copy to HA custom_components/ for integration testing")
        print("4. Restart HA and check logs for any errors")
    else:
        print("✗ Some issues found - fix syntax errors first")
    
    return all_valid

if __name__ == "__main__":
    success = validate_integration()
    sys.exit(0 if success else 1)