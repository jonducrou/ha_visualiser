#!/usr/bin/env python3
"""
Debug helper for testing zone detection in Home Assistant.
This file should be copied to HA and run via the Scripts section or developer tools.
"""

# For HA script execution, this would be accessed via the hass object
DEBUG_SCRIPT = '''
# Find all zone entities
zone_entities = [
    entity_id for entity_id in hass.states.entity_ids() 
    if entity_id.startswith("zone.")
]

logger.info(f"Found {len(zone_entities)} zones: {zone_entities}")

# Check each zone's attributes
for zone_id in zone_entities:
    zone_state = hass.states.get(zone_id)
    if zone_state:
        attrs = zone_state.attributes
        lat = attrs.get("latitude")
        lon = attrs.get("longitude") 
        radius = attrs.get("radius", 100)
        friendly_name = attrs.get("friendly_name", zone_id)
        
        logger.info(f"Zone {zone_id}:")
        logger.info(f"  Name: {friendly_name}")
        logger.info(f"  Lat: {lat}, Lon: {lon}")
        logger.info(f"  Radius: {radius}m")
        logger.info(f"  State: {zone_state.state}")

# Find entities with location data
entities_with_location = []
for entity_id in hass.states.entity_ids():
    entity_state = hass.states.get(entity_id)
    if entity_state:
        lat = entity_state.attributes.get("latitude")
        lon = entity_state.attributes.get("longitude")
        if lat is not None and lon is not None:
            entities_with_location.append({
                "entity_id": entity_id,
                "lat": lat,
                "lon": lon,
                "friendly_name": entity_state.attributes.get("friendly_name", entity_id)
            })

logger.info(f"Found {len(entities_with_location)} entities with location data:")
for entity in entities_with_location[:10]:  # Show first 10
    logger.info(f"  {entity['entity_id']}: {entity['friendly_name']} at ({entity['lat']}, {entity['lon']})")

if len(entities_with_location) > 10:
    logger.info(f"  ... and {len(entities_with_location) - 10} more")

# Test zone calculations if we have data
if zone_entities and entities_with_location:
    import math
    
    def calculate_distance(entity_lat, entity_lon, zone_lat, zone_lon):
        lat1, lon1, lat2, lon2 = map(math.radians, [entity_lat, entity_lon, zone_lat, zone_lon])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance = 6371000 * c
        return distance
    
    logger.info("Testing zone calculations:")
    
    for zone_id in zone_entities[:3]:  # Test first 3 zones
        zone_state = hass.states.get(zone_id)
        if not zone_state:
            continue
            
        zone_lat = zone_state.attributes.get("latitude")
        zone_lon = zone_state.attributes.get("longitude")
        zone_radius = zone_state.attributes.get("radius", 100)
        
        if zone_lat is None or zone_lon is None:
            logger.info(f"  Zone {zone_id} missing coordinates")
            continue
            
        entities_in_zone = []
        for entity in entities_with_location[:5]:  # Test first 5 entities
            distance = calculate_distance(entity["lat"], entity["lon"], zone_lat, zone_lon)
            if distance <= zone_radius:
                entities_in_zone.append(f"{entity['entity_id']} ({distance:.1f}m)")
        
        logger.info(f"  Zone {zone_id}: {len(entities_in_zone)} entities in range")
        for entity_info in entities_in_zone:
            logger.info(f"    {entity_info}")
'''

def generate_ha_debug_commands():
    """Generate specific debug commands for HA developer tools."""
    print("=== Home Assistant Debug Commands ===")
    print("\n1. Check for zones:")
    print("{{ states | selectattr('entity_id', 'match', 'zone\\..*') | list | length }}")
    
    print("\n2. List all zones:")
    print("{% for state in states %}")
    print("  {% if state.entity_id.startswith('zone.') %}")
    print("    {{ state.entity_id }}: {{ state.attributes.friendly_name }}")
    print("  {% endif %}")
    print("{% endfor %}")
    
    print("\n3. Check entities with location:")
    print("{{ states | selectattr('attributes.latitude', 'defined') | list | length }}")
    
    print("\n4. List entities with location (first 5):")
    print("{% set entities_with_location = states | selectattr('attributes.latitude', 'defined') | list %}")
    print("{% for entity in entities_with_location[:5] %}")
    print("  {{ entity.entity_id }}: {{ entity.attributes.latitude }}, {{ entity.attributes.longitude }}")
    print("{% endfor %}")
    
    print("\n5. Test script for developer tools (Services tab):")
    print("Service: python_script.debug_zones")
    print("Or create a script in Home Assistant scripts.yaml:")
    print("""
debug_zones:
  alias: "Debug Zone Detection"
  sequence:
    - service: system_log.write
      data:
        message: "Starting zone debug..."
        level: info
""")

def main():
    print("=== Zone Detection Debug Helper ===")
    print("\nThis file helps debug why zones might not be appearing in the visualizer.")
    print("\nTo use this in Home Assistant:")
    print("1. Go to Developer Tools > Scripts")
    print("2. Copy the debug script section and run it")
    print("3. Check the Home Assistant logs for output")
    
    print("\n" + "="*50)
    print("DEBUG SCRIPT FOR HOME ASSISTANT:")
    print("="*50)
    print(DEBUG_SCRIPT)
    
    print("\n" + "="*50)
    generate_ha_debug_commands()
    
    print("\n=== Possible Issues and Solutions ===")
    print("1. No zones defined:")
    print("   - Check Configuration > Areas & Zones")
    print("   - Create a zone with coordinates and radius")
    
    print("\n2. No entities with location:")
    print("   - device_tracker entities usually have location") 
    print("   - person entities have location")
    print("   - Some sensors may have location")
    
    print("\n3. Zone coordinates missing:")
    print("   - Ensure zones have latitude/longitude set")
    print("   - Check zone radius is reasonable (100m default)")
    
    print("\n4. Debug logging not visible:")
    print("   - Set logger level to debug in configuration.yaml:")
    print("   logger:")
    print("     logs:")
    print("       custom_components.ha_visualiser: debug")

if __name__ == "__main__":
    main()