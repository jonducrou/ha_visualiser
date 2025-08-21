# Scene Relationship Test Scenarios

This document outlines test scenarios for verifying that scene relationship detection works correctly.

## Test Data Structure

### Scene Configuration Examples

#### Scenario 1: Basic Scene with Entities Dict
```yaml
scene:
  - name: "Movie Night"
    entities:
      light.living_room_lamp: "off"  
      light.kitchen_light:
        state: "on"
        brightness: 50
      media_player.tv: "on"
```

**Expected**: Scene should show relationships to:
- `light.living_room_lamp` (controls)
- `light.kitchen_light` (controls) 
- `media_player.tv` (controls)

#### Scenario 2: Scene with Snapshot Data
```yaml
scene:
  - name: "Bedtime"
    snapshot:
      light.bedroom_ceiling: "off"
      switch.fan: "off"
      alarm_control_panel.home: "armed_night"
```

**Expected**: Scene should show relationships to:
- `light.bedroom_ceiling` (controls)
- `switch.fan` (controls)
- `alarm_control_panel.home` (controls)

#### Scenario 3: Scene with Mixed Configuration
```yaml 
scene:
  - name: "Morning Routine"
    entities:
      light.hallway: "on"
    snapshot:
      cover.blinds: "open"
      climate.thermostat:
        temperature: 21
```

**Expected**: Scene should show relationships to:
- `light.hallway` (controls)
- `cover.blinds` (controls) 
- `climate.thermostat` (controls)

## Forward Relationship Tests

### Test 1: Entity → Scene Detection
**Given**: Search for `light.living_room_lamp`
**Expected**: Should show relationship to `scene.movie_night` with "scene_controls" type

### Test 2: Scene → Entities Detection  
**Given**: Search for `scene.movie_night`
**Expected**: Should show relationships to all controlled entities with "scene_controls" type

## Reverse Relationship Tests

### Test 3: Group Relationship Discovery
**Given**: Entity is member of both group and scene
**Expected**: Should show both group "contains" and scene "controls" relationships

### Test 4: Mixed Domain Detection
**Given**: Scene controls lights, switches, and media players
**Expected**: All entity types should be detected regardless of domain

## Edge Cases

### Test 5: Invalid Entity IDs
**Given**: Scene config contains invalid entity references (e.g., "invalid.entity")
**Expected**: Invalid entities should be filtered out, valid ones still detected

### Test 6: Empty Scene Configuration
**Given**: Scene with no entities or snapshot
**Expected**: No relationships should be created (graceful handling)

### Test 7: Nested Configuration
**Given**: Complex scene configuration with nested attributes
**Expected**: Entity extraction should handle nested structures

## Integration Tests

### Test 8: Relationship Direction
**Given**: Scene-entity relationship
**Expected**: Edge should be directed as Scene → Entity with "controls" label

### Test 9: Node Priority
**Given**: Scene vs Entity priority comparison
**Expected**: Scene should have priority 4 (same as automation/script)

### Test 10: Icon and Display
**Given**: Scene node creation
**Expected**: Scene should use `mdi:palette` icon and proper friendly name

## Performance Tests

### Test 11: Large Scene Collections
**Given**: 100+ scenes with multiple entities each
**Expected**: Relationship detection should complete without timeout

### Test 12: Deep Entity Networks
**Given**: Entities that are in multiple scenes and groups
**Expected**: All relationships should be detected correctly

## Error Handling Tests

### Test 13: Missing Scene State
**Given**: Scene entity without state object
**Expected**: Should handle gracefully without crashing

### Test 14: Malformed Configuration
**Given**: Scene with malformed configuration attribute
**Expected**: Should skip malformed data, continue processing

## Expected Behavior Summary

1. **Relationship Type**: `scene_controls`
2. **Direction**: Scene → Entity  
3. **Label**: "controls"
4. **Priority**: 4 (same as automations/scripts)
5. **Icon**: `mdi:palette`
6. **Integration**: Works with existing group/automation relationships

## Manual Testing Steps

1. **Setup**: Create test scenes in Home Assistant
2. **Search Entity**: Search for an entity controlled by scene
3. **Verify Forward**: Check scene appears in relationships
4. **Search Scene**: Search for the scene itself  
5. **Verify Reverse**: Check controlled entities appear
6. **Check Labels**: Verify "controls" label is used
7. **Check Direction**: Verify Scene → Entity direction

## Regression Testing

Ensure new scene support doesn't break existing functionality:
- ✅ Group relationships still work
- ✅ Automation relationships still work  
- ✅ Script relationships still work
- ✅ Device/Area relationships still work
- ✅ Template relationships still work