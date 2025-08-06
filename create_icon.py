#!/usr/bin/env python3
"""Create a simple icon for the HA Visualiser integration."""

import os
from pathlib import Path

def create_svg_icon():
    """Create a simple SVG icon representing a network/graph visualization with subtle colors."""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <!-- Subtle gradient background -->
  <defs>
    <radialGradient id="bgGradient" cx="50%" cy="50%" r="50%">
      <stop offset="0%" style="stop-color:#f8f9fa;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#e9ecef;stop-opacity:1" />
    </radialGradient>
  </defs>
  
  <!-- Background circle with subtle gradient -->
  <circle cx="256" cy="256" r="240" fill="url(#bgGradient)" stroke="#6c757d" stroke-width="4"/>
  
  <!-- Add subtle connecting lines between some outer nodes - put behind everything -->
  <line x1="256" y1="90" x2="390" y2="140" stroke="#6c757d" stroke-width="3" opacity="0.4"/>
  <line x1="390" y1="140" x2="422" y2="256" stroke="#6c757d" stroke-width="3" opacity="0.4"/>
  <line x1="422" y1="256" x2="390" y2="372" stroke="#6c757d" stroke-width="3" opacity="0.4"/>
  <line x1="122" y1="140" x2="90" y2="256" stroke="#6c757d" stroke-width="3" opacity="0.4"/>
  <line x1="90" y1="256" x2="122" y2="372" stroke="#6c757d" stroke-width="3" opacity="0.4"/>
  
  <!-- Central node (focus entity) - much bigger -->
  <circle cx="256" cy="256" r="40" fill="#ffffff" stroke="#495057" stroke-width="4"/>
  
  <!-- Connected nodes around the center - using subtle, muted colors and bigger positions -->
  <!-- Top node (light entity) -->
  <circle cx="256" cy="90" r="28" fill="#fff3cd" stroke="#856404" stroke-width="3"/>
  <line x1="256" y1="118" x2="256" y2="216" stroke="#6c757d" stroke-width="3"/>
  
  <!-- Top-right node (switch) -->
  <circle cx="390" cy="140" r="26" fill="#d1ecf1" stroke="#0c5460" stroke-width="3"/>
  <line x1="372" y1="158" x2="290" y2="232" stroke="#6c757d" stroke-width="3"/>
  
  <!-- Right node (sensor) -->
  <circle cx="422" cy="256" r="28" fill="#f8d7da" stroke="#721c24" stroke-width="3"/>
  <line x1="394" y1="256" x2="296" y2="256" stroke="#6c757d" stroke-width="3"/>
  
  <!-- Bottom-right node (automation) -->
  <circle cx="390" cy="372" r="26" fill="#e2e3e5" stroke="#383d41" stroke-width="3"/>
  <line x1="372" y1="354" x2="290" y2="280" stroke="#6c757d" stroke-width="3"/>
  
  <!-- Bottom node (device) -->
  <circle cx="256" cy="422" r="28" fill="#d4edda" stroke="#155724" stroke-width="3"/>
  <line x1="256" y1="394" x2="256" y2="296" stroke="#6c757d" stroke-width="3"/>
  
  <!-- Bottom-left node (area) -->
  <circle cx="122" cy="372" r="26" fill="#ffeaa7" stroke="#6c5ce7" stroke-width="3"/>
  <line x1="140" y1="354" x2="222" y2="280" stroke="#6c757d" stroke-width="3"/>
  
  <!-- Left node (group) -->
  <circle cx="90" cy="256" r="28" fill="#e7e9fc" stroke="#4834d4" stroke-width="3"/>
  <line x1="118" y1="256" x2="216" y2="256" stroke="#6c757d" stroke-width="3"/>
  
  <!-- Top-left node (zone) -->
  <circle cx="122" cy="140" r="26" fill="#ddd6fe" stroke="#5b21b6" stroke-width="3"/>
  <line x1="140" y1="158" x2="222" y2="232" stroke="#6c757d" stroke-width="3"/>
  
  <!-- Add extra large house icon in center -->
  <text x="256" y="290" text-anchor="middle" font-family="Arial, sans-serif" font-size="144" font-weight="bold" fill="#495057">🏠</text>
</svg>'''
    
    return svg_content

def main():
    """Create the SVG icon file."""
    print("Creating HA Visualiser integration icon...")
    
    # Create the SVG
    svg_content = create_svg_icon()
    
    # Save SVG file
    with open("ha_visualiser_icon.svg", "w") as f:
        f.write(svg_content)
    
    print("✅ Created ha_visualiser_icon.svg")
    print("\nNext steps:")
    print("1. Convert SVG to PNG files using online tool or ImageMagick:")
    print("   - icon.png (512x512) for HACS")
    print("   - icon@2x.png (256x256) for HA frontend")
    print("\nOnline converters you can use:")
    print("- https://convertio.co/svg-png/")
    print("- https://cloudconvert.com/svg-to-png")
    print("- Or use: convert ha_visualiser_icon.svg -resize 512x512 icon.png")
    print("         convert ha_visualiser_icon.svg -resize 256x256 icon@2x.png")

if __name__ == "__main__":
    main()