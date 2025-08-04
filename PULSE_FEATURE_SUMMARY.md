# Pulsing Animation Feature - v0.6.0

## Overview
Added visual pulsing animation to nodes that are in active/running states to provide immediate visual feedback of entity activity.

## Backend Changes

### GraphNode dataclass (graph_service.py:25)
- Added `is_active: bool = False` field to track entity activity state

### Activity Detection (_is_entity_active method - graph_service.py:784)
Comprehensive activity detection for multiple domains:

**Basic Active States:**
- lights: 'on'
- switches: 'on' 
- fans: 'on'
- media_players: 'playing', 'on'
- climate: heating/cooling modes
- automations: 'on' + recently triggered (last 5 minutes)
- scripts: 'on' (running)
- timers: 'active'
- cameras: 'recording', 'streaming'

**Advanced Detection:**
- Motion/occupancy sensors: 'on', 'detected'
- Power sensors: >0.1W consumption
- Media players: has active media_title
- Climate: temperature differential >0.5°C from target

### Node Creation Updates
- All GraphNode creations now include is_active detection
- Regular entities use _is_entity_active() method
- Device/area/zone/label nodes default to is_active=False

### WebSocket API (websocket_api.py:87,155)
- Added "is_active" field to node serialization in both neighborhood endpoints

## Frontend Changes

### Visual Styling (ha-visualiser-panel.js:430-462)
- Active nodes get orange border (#FF8C00) and enhanced border width
- Dynamic shadow configuration with orange glow effect
- Visual priority: Active > Focus > Normal nodes

### Pulsing Animation (startPulsingAnimation method - ha-visualiser-panel.js:617)
- Sine wave animation cycling shadow size (4-12px) and opacity (0.4-0.8)
- 100ms update intervals for smooth animation
- Automatic cleanup on graph reset/reload

### Tooltip Enhancement
- Active nodes display "🔵 Active" indicator in tooltip
- Provides immediate feedback on hover

## Technical Implementation

**Animation Method:**
- Uses vis.js shadow property for glow effect
- Sine wave mathematical progression for smooth pulsing
- setInterval-based animation loop with cleanup

**Performance Optimizations:**
- Only animate nodes that are actually active
- Clean up animations on graph changes
- Minimal DOM manipulation using vis.js DataSet updates

**Activity Detection Logic:**
- Domain-specific state evaluation
- Advanced attribute checking for complex entities
- Time-based triggers for automations (5-minute window)
- Numeric threshold detection for sensors

## Usage Examples

**Active Entities That Will Pulse:**
- Light with state "on"
- Running automation (on + recently triggered)
- Media player currently playing music
- Motion sensor detecting movement
- Climate system actively heating/cooling
- Script currently executing

**Integration Points:**
- Real-time state updates automatically reflect in animation
- Click navigation preserves animation state
- Compatible with all existing filtering and search functionality

## Future Enhancements
- Configurable pulse colors per domain
- Adjustable animation speed/intensity
- Activity level indicators (more/less active)
- Sound/notification integration options