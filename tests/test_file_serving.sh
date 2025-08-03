#!/bin/bash

echo "=== HA Visualiser File Serving Test ==="
echo

# Check if we have the right files locally
echo "1. LOCAL FILES CHECK:"
if [ -f "custom_components/ha_visualiser/www/ha-visualiser-panel.js" ]; then
    echo "✓ Local panel JS file exists"
    echo "   Size: $(stat -f%z custom_components/ha_visualiser/www/ha-visualiser-panel.js 2>/dev/null || stat -c%s custom_components/ha_visualiser/www/ha-visualiser-panel.js) bytes"
    echo "   Modified: $(stat -f%Sm custom_components/ha_visualiser/www/ha-visualiser-panel.js 2>/dev/null || stat -c%y custom_components/ha_visualiser/www/ha-visualiser-panel.js)"
    
    # Check for version indicator
    if grep -q "v0.4" custom_components/ha_visualiser/www/ha-visualiser-panel.js; then
        echo "✓ File contains v0.4.x version marker"
    else
        echo "✗ File missing v0.4.x version marker"
    fi
    
    # Check for vis.js code
    if grep -q "loadVisJS" custom_components/ha_visualiser/www/ha-visualiser-panel.js; then
        echo "✓ File contains vis.js loading code"
    else
        echo "✗ File missing vis.js loading code"
    fi
else
    echo "✗ Local panel JS file not found"
fi

echo
echo "2. DEBUGGING STEPS:"
echo
echo "Copy files to HA (replace /path/to/homeassistant with your actual path):"
echo "  cp -rf custom_components/ha_visualiser/ /path/to/homeassistant/config/custom_components/"
echo
echo "Check copied file:"
echo "  ls -la /path/to/homeassistant/config/custom_components/ha_visualiser/www/ha-visualiser-panel.js"
echo "  grep 'v0.4' /path/to/homeassistant/config/custom_components/ha_visualiser/www/ha-visualiser-panel.js"
echo
echo "Restart HA and check URL directly in browser:"
echo "  http://your-ha-url:8123/hacsfiles/ha_visualiser/ha-visualiser-panel.js"
echo
echo "In browser console, check for version:"
echo "  Look for: 'HA Visualiser Panel v0.4.x: [latest feature description]'"
echo "  Look for: 'HA Visualiser Panel: Loading enhanced vis.js version'"
echo
echo "Clear browser cache:"
echo "  Ctrl+Shift+Del (Windows) or Cmd+Shift+Delete (Mac)"
echo "  Or right-click refresh → 'Empty Cache and Hard Reload'"

# Try to detect common HA paths
echo
echo "3. COMMON HA PATHS TO TRY:"
for path in \
    "/config/custom_components" \
    "/homeassistant/config/custom_components" \
    "$HOME/.homeassistant/custom_components" \
    "/usr/share/hassio/homeassistant/custom_components" \
    "/data/custom_components"; do
    echo "  $path/ha_visualiser/"
done