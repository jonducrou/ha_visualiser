#!/usr/bin/env python3
"""Debug script to help diagnose HA integration issues."""

import json
from pathlib import Path

def check_integration_files():
    """Check if all required integration files exist and are valid."""
    print("=== HA Visualiser Integration Debug ===\n")
    
    required_files = {
        'custom_components/ha_visualiser/__init__.py': 'Integration entry point',
        'custom_components/ha_visualiser/manifest.json': 'HACS metadata',
        'custom_components/ha_visualiser/config_flow.py': 'Configuration flow',
        'custom_components/ha_visualiser/graph_service.py': 'Graph analysis backend',
        'custom_components/ha_visualiser/websocket_api.py': 'WebSocket API handlers',
        'custom_components/ha_visualiser/const.py': 'Constants',
        'custom_components/ha_visualiser/www/ha-visualiser-panel.js': 'Frontend panel'
    }
    
    print("1. FILE EXISTENCE CHECK:")
    missing_files = []
    for file_path, description in required_files.items():
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"   ✓ {file_path} ({size} bytes) - {description}")
        else:
            print(f"   ✗ {file_path} - MISSING - {description}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n   ERROR: {len(missing_files)} required files are missing!")
        return False
    
    print("\n2. MANIFEST.JSON VALIDATION:")
    try:
        with open('custom_components/ha_visualiser/manifest.json') as f:
            manifest = json.load(f)
        
        required_keys = ['domain', 'name', 'version', 'documentation', 'dependencies', 'codeowners']
        for key in required_keys:
            if key in manifest:
                print(f"   ✓ {key}: {manifest[key]}")
            else:
                print(f"   ✗ {key}: MISSING")
        
        # Check domain matches directory
        if manifest.get('domain') != 'ha_visualiser':
            print(f"   ⚠ Domain mismatch: {manifest.get('domain')} != ha_visualiser")
            
    except Exception as e:
        print(f"   ✗ Error reading manifest.json: {e}")
        return False
    
    print("\n3. INTEGRATION STRUCTURE:")
    # Check if websocket_api.py has the required functions
    websocket_path = Path('custom_components/ha_visualiser/websocket_api.py')
    if websocket_path.exists():
        content = websocket_path.read_text()
        required_functions = [
            'async_register_websocket_handlers',
            'websocket_get_entity_neighborhood',
            'websocket_search_entities'
        ]
        
        for func in required_functions:
            if func in content:
                print(f"   ✓ WebSocket function: {func}")
            else:
                print(f"   ✗ Missing WebSocket function: {func}")
    
    print("\n4. COMMON ISSUES TO CHECK:")
    print("   - Check HA logs for errors: tail -f home-assistant.log | grep ha_visualiser")
    print("   - Verify integration is in config/custom_components/ha_visualiser/")
    print("   - Restart HA after copying files")
    print("   - Check browser console for frontend errors")
    print("   - Verify HA version compatibility (needs 2023.7+)")
    
    print("\n5. DEBUGGING STEPS:")
    print("   a) Check if integration loads:")
    print("      grep 'ha_visualiser' home-assistant.log")
    print("   b) Check if panel registers:")
    print("      grep 'panel' home-assistant.log | grep visuali")
    print("   c) Test websocket in browser console:")
    print("      connection.sendMessage({type: 'ha_visualiser/search', query: 'light'})")
    
    return True

def generate_test_commands():
    """Generate commands to test the integration."""
    print("\n=== TEST COMMANDS FOR HA ===")
    
    print("\n1. Copy integration to HA:")
    print("   cp -r custom_components/ha_visualiser/ /path/to/homeassistant/config/custom_components/")
    
    print("\n2. Restart Home Assistant")
    
    print("\n3. Check if integration loaded:")
    print("   grep 'ha_visualiser' /path/to/homeassistant/home-assistant.log")
    
    print("\n4. Expected log entries:")
    print("   - 'Home Assistant Entity Visualizer integration loaded successfully'")
    print("   - 'Registering websocket command ha_visualiser/search'")
    print("   - 'Registering websocket command ha_visualiser/neighborhood'")
    
    print("\n5. Test in HA Developer Tools > Services:")
    print("   Look for 'Entity Visualizer' in the sidebar")
    
    print("\n6. Browser console test (F12):")
    print("   hass.connection.sendMessage({type: 'ha_visualiser/search', query: 'test'})")

if __name__ == "__main__":
    if check_integration_files():
        generate_test_commands()
    else:
        print("\n❌ Fix the file issues above before testing in HA")