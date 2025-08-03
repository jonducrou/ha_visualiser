#!/usr/bin/env python3
"""
Test and visualize 2-level neighborhood expansion.
"""

def visualize_neighborhood_expansion():
    """Show what 2-level neighborhoods will reveal."""
    print("=== 2-Level Neighborhood Expansion (v0.2.2) ===")
    
    # Example: Focus on a motion sensor
    print("Example: Focus on binary_sensor.living_room_motion")
    print()
    
    print("LEVEL 1 (direct relationships):")
    level1_relationships = [
        "device:motion_sensor_hub --has--> binary_sensor.living_room_motion",
        "area:living_room --contains--> binary_sensor.living_room_motion", 
        "binary_sensor.living_room_motion --triggers--> automation.motion_lights",
        "binary_sensor.living_room_motion --triggers--> automation.security_alert"
    ]
    
    for rel in level1_relationships:
        print(f"  {rel}")
    
    print("\nLEVEL 2 (relationships of related nodes):")
    level2_relationships = [
        # From device:motion_sensor_hub
        "device:motion_sensor_hub --has--> sensor.living_room_temperature",
        "device:motion_sensor_hub --has--> sensor.living_room_light_level",
        # From area:living_room  
        "area:living_room --contains--> light.living_room_ceiling",
        "area:living_room --contains--> switch.living_room_lamp",
        "area:living_room --contains--> media_player.living_room_tv",
        # From automation.motion_lights
        "automation.motion_lights --controls--> light.living_room_ceiling",
        "automation.motion_lights --controls--> light.living_room_accent",
        # From automation.security_alert
        "automation.security_alert --controls--> switch.alarm_siren",
        "automation.security_alert --controls--> camera.front_door"
    ]
    
    for rel in level2_relationships:
        print(f"  {rel}")
    
    print(f"\nTOTAL NODES: {1 + len(level1_relationships) + len(level2_relationships)} nodes")
    print("(Focus + Level 1 + Level 2)")

def compare_neighborhood_depths():
    """Compare 1-level vs 2-level neighborhoods."""
    print("\n=== Depth Comparison ===")
    
    scenarios = [
        {
            "focus": "light.kitchen_ceiling",
            "depth_1": [
                "device:smart_switch --has--> light.kitchen_ceiling",
                "area:kitchen --contains--> light.kitchen_ceiling",
                "automation.morning_routine --controls--> light.kitchen_ceiling"
            ],
            "depth_2_additional": [
                # From device:smart_switch
                "device:smart_switch --has--> switch.kitchen_outlets",
                # From area:kitchen
                "area:kitchen --contains--> sensor.kitchen_temperature", 
                "area:kitchen --contains--> binary_sensor.kitchen_motion",
                # From automation.morning_routine
                "automation.morning_routine --controls--> coffee_maker.kitchen",
                "automation.morning_routine --controls--> blinds.kitchen_window",
                # Level 2 can also reveal what triggers the automation
                "sensor.bedroom_motion --triggers--> automation.morning_routine"
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"Focus: {scenario['focus']}")
        print(f"  Depth 1: {len(scenario['depth_1'])} relationships")
        print(f"  Depth 2: {len(scenario['depth_1']) + len(scenario['depth_2_additional'])} relationships")
        print(f"  Expansion: +{len(scenario['depth_2_additional'])} additional relationships")
        print()
        
        print("  New relationships revealed at depth 2:")
        for rel in scenario['depth_2_additional']:
            print(f"    {rel}")

def show_relationship_discovery_paths():
    """Show how multi-level discovery works."""
    print("\n=== Relationship Discovery Paths ===")
    
    discovery_example = {
        "start": "switch.living_room_lamp",
        "paths": [
            {
                "path": "switch → device → other entities on device",
                "steps": [
                    "switch.living_room_lamp → device:smart_outlet_123",
                    "device:smart_outlet_123 → sensor.living_room_power_usage",
                    "device:smart_outlet_123 → binary_sensor.living_room_outlet_status"
                ]
            },
            {
                "path": "switch → area → other entities in area", 
                "steps": [
                    "switch.living_room_lamp → area:living_room",
                    "area:living_room → light.living_room_ceiling",
                    "area:living_room → media_player.living_room_tv"
                ]
            },
            {
                "path": "switch → automation → controlled entities",
                "steps": [
                    "switch.living_room_lamp ← automation.evening_scene",
                    "automation.evening_scene → light.living_room_accent",
                    "automation.evening_scene → blinds.living_room_window"
                ]
            },
            {
                "path": "switch → automation → triggering entities",
                "steps": [
                    "switch.living_room_lamp ← automation.manual_override", 
                    "automation.manual_override ← binary_sensor.living_room_switch",
                    "automation.manual_override ← input_boolean.guest_mode"
                ]
            }
        ]
    }
    
    print(f"Starting from: {discovery_example['start']}")
    print()
    
    for i, path in enumerate(discovery_example['paths'], 1):
        print(f"Path {i}: {path['path']}")
        for step in path['steps']:
            print(f"  {step}")
        print()

def estimate_performance_impact():
    """Estimate the performance impact of 2-level neighborhoods."""
    print("=== Performance Considerations ===")
    
    print("Estimated node counts for typical entities:")
    estimates = [
        {"entity": "Simple switch", "depth_1": "3-5 nodes", "depth_2": "8-15 nodes"},
        {"entity": "Motion sensor", "depth_1": "4-6 nodes", "depth_2": "12-25 nodes"},
        {"entity": "Area node", "depth_1": "5-10 nodes", "depth_2": "15-40 nodes"},
        {"entity": "Central automation", "depth_1": "6-12 nodes", "depth_2": "20-50 nodes"}
    ]
    
    for estimate in estimates:
        print(f"  {estimate['entity']:<18}: {estimate['depth_1']} → {estimate['depth_2']}")
    
    print("\nPerformance benefits:")
    print("  ✓ More context without additional clicks")
    print("  ✓ Better understanding of entity ecosystems") 
    print("  ✓ Reveals indirect relationships")
    print("  ✓ Shows automation trigger chains")
    
    print("\nPotential concerns:")
    print("  ⚠ Larger graphs (mitigated by vis.js performance)")
    print("  ⚠ More visual complexity (mitigated by good layout)")
    print("  ⚠ Longer load times (should still be <1 second)")

if __name__ == "__main__":
    visualize_neighborhood_expansion()
    compare_neighborhood_depths()
    show_relationship_discovery_paths()
    estimate_performance_impact()
    
    print("\n=== Summary ===")
    print("2-level neighborhoods will provide:")
    print("✓ Richer context around each entity")
    print("✓ Discovery of indirect relationships")
    print("✓ Complete automation chains (trigger → automation → targets)")
    print("✓ Device/area ecosystem views")
    print("✓ Better understanding of entity interconnections")
    print("\nThis creates a more comprehensive view while keeping")
    print("navigation intuitive through the existing click-to-explore interface.")