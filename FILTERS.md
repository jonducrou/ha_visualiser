# Entity Graph Filters

The HA Visualiser supports various filters to control which entities and relationships are displayed in the graph.

## Show Areas Filter

### Overview
The "Show Areas" checkbox allows you to toggle the visibility of Home Assistant areas and area-related relationships in the entity graph.

### Location
- **Position**: Right of the depth selector in the search controls
- **Default State**: Checked (areas shown)
- **Label**: "Show Areas"

### Functionality

#### When Checked (Default)
- **Areas Displayed**: Area nodes (`area.kitchen`, `area.living_room`, etc.) appear in the graph
- **Area Relationships**: Shows relationships like:
  - `area_contains`: Area → Entity relationships
  - `area_contains_device`: Area → Device relationships  
  - `device_in_area`: Device → Area relationships
- **Full Context**: Provides complete spatial context for your Home Assistant setup

#### When Unchecked
- **Areas Hidden**: All `area:*` nodes are filtered out during graph traversal
- **Area Relationships Filtered**: Area-related edges are excluded:
  - No `area_contains` relationships
  - No `area_contains_device` relationships
  - No `device_in_area` relationships
- **Simplified View**: Shows only entity-to-entity and entity-to-device relationships

### Use Cases

#### Show Areas (Checked)
- **Spatial Organization**: Understanding how entities are physically organized
- **Room-based Automation**: Seeing which entities are in which rooms
- **Area-wide Control**: Finding all entities controlled by area-based automations
- **Setup Validation**: Ensuring entities are assigned to correct areas

#### Hide Areas (Unchecked)
- **Functional Focus**: Concentrating on logical relationships between entities
- **Simplified Debugging**: Reducing visual clutter when troubleshooting entity connections
- **Device Relationships**: Focusing on device-to-entity connections without spatial context
- **Clean Screenshots**: Creating cleaner visualizations for documentation

### Technical Implementation

#### Frontend
```javascript
// Checkbox state is checked before API calls
const showAreas = showAreasCheckbox ? showAreasCheckbox.checked : true;

// Sent as parameter to WebSocket API
const graphData = await this.hass.callWS({
  type: 'ha_visualiser/get_neighborhood',
  entity_id: entityId,
  max_depth: maxDepth,
  show_areas: showAreas
});
```

#### Backend
```python
# WebSocket API parameter
@websocket_api.websocket_command({
    vol.Optional("show_areas", default=True): bool,
})

# Graph traversal filtering
if not show_areas:
    if (related_id.startswith("area:") or 
        relationship_type in ["area_contains", "area_contains_device", "device_in_area"]):
        continue  # Skip area-related nodes and relationships
```

### Filtered Relationship Types

When areas are hidden, these relationship types are excluded:
- **`area_contains`**: Direct entity-to-area assignments
- **`area_contains_device`**: Device-to-area assignments  
- **`device_in_area`**: Reverse device-area relationships

### Interaction with Other Features

#### Depth Control
- Area filtering applies at all depth levels
- Depth traversal continues through non-area relationships
- May result in different entity counts at the same depth

#### Search
- Area entities still appear in search results
- Clicking an area when "Show Areas" is unchecked will show minimal connections
- Areas can be used as starting points regardless of filter setting

### Performance Benefits

#### Reduced Complexity
- **Fewer Nodes**: Eliminating area nodes reduces graph complexity
- **Fewer Edges**: Less relationships to render and manage
- **Faster Layout**: Simpler graphs stabilize more quickly
- **Better Performance**: Reduced memory usage and processing

#### Visual Clarity
- **Less Clutter**: Focus on functional rather than spatial relationships
- **Clearer Patterns**: Easier to see direct entity interactions
- **Simplified Debugging**: Reduced visual noise when troubleshooting

### Future Filter Possibilities

The architecture supports additional filters:
- **Show Devices**: Toggle device visibility
- **Show Groups**: Toggle group entity visibility  
- **Show Scripts**: Filter out script entities
- **Show Automations**: Filter out automation entities
- **Domain Filters**: Show/hide specific entity domains

### Examples

#### With Areas (Default)
```
light.kitchen_main ←→ device.kitchen_hub ←→ area.kitchen ←→ automation.kitchen_lights
```

#### Without Areas (Filtered)
```
light.kitchen_main ←→ device.kitchen_hub     automation.kitchen_lights
                                                      ↑
                              (direct automation relationship)
```

The area filtering provides a powerful way to simplify complex entity graphs while maintaining the ability to see complete spatial context when needed.