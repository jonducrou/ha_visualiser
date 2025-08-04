# Event-Driven Node Animation - v0.6.1

## Overview
Replaced static `is_active` property with dynamic, event-driven node highlighting that responds to real-time Home Assistant state changes.

## ✅ Changes Made

### Removed Static Approach
- **Removed** `is_active: bool` field from `GraphNode` dataclass
- **Deleted** `_is_entity_active()` method with complex state detection logic
- **Removed** static activity detection from node creation
- **Cleaned up** WebSocket API serialization of static activity status

### Implemented Event-Driven Approach

#### 1. Home Assistant Event Listener (setupEventListeners - line 609)
```javascript
this.hass.connection.addEventListener('state_changed', this.stateChangeListener);
```
- Subscribes to HA's `state_changed` events via WebSocket connection
- Only triggers for entities currently visible in the graph
- Logs state transitions: `old_state → new_state`

#### 2. Dynamic Node Highlighting (highlightNodeOnStateChange - line 639)
```javascript
// Orange-red border and pulsing shadow
const highlightColor = {
  background: node.color.background,
  border: '#FF6B35',  // Orange-red highlight
};
```
- **Immediate visual feedback** on any state change
- Orange-red border (`#FF6B35`) with enhanced border width
- Dynamic shadow with pulsing animation
- **3-second duration** with automatic cleanup

#### 3. Real-Time Pulsing Animation (startNodePulse - line 700)
```javascript
const shadowSize = 8 + 6 * Math.sin(pulsePhase);
const shadowOpacity = 0.5 + 0.3 * Math.sin(pulsePhase);
```
- **Sine wave animation** for smooth pulsing effect
- Shadow size oscillates between 2-14px
- Opacity varies between 0.2-0.8 for breathing effect
- **100ms update intervals** for smooth 60fps-like animation

#### 4. Proper Cleanup Mechanisms (cleanupAnimations - line 770)
- **Tracked timeouts**: `this.highlightTimeouts[entityId]` for proper cleanup
- **Tracked animations**: `this.nodePulses[entityId]` for interval management
- **Automatic cleanup** on graph reset/navigation
- **Memory leak prevention** with comprehensive cleanup

## Technical Implementation Details

### Event Flow
1. **HA State Change** → WebSocket event fired
2. **Event Filter** → Only process if entity in current graph
3. **Visual Highlight** → Apply orange border + shadow
4. **Animation Start** → Begin pulsing effect
5. **Auto Cleanup** → Clear after 3 seconds

### Performance Optimizations
- **Selective listening**: Only entities in current graph trigger animations
- **Individual node tracking**: Each entity has its own animation lifecycle
- **Proper cleanup**: All intervals/timeouts cleared on navigation
- **Efficient updates**: Only update shadow properties during animation

### Visual Design
- **Color**: Orange-red (`#FF6B35`) for high visibility
- **Duration**: 3-second highlight window
- **Animation**: Smooth sine wave pulsing
- **Restoration**: Original appearance restored with proper border widths

## Usage Examples

**Triggers That Will Cause Node Pulsing:**
- Light turned on/off
- Sensor value changes
- Media player starts/stops
- Automation triggers
- Script execution
- Climate mode changes
- Door/window opens/closes
- Any entity state transition

**Visual Behavior:**
- Node border changes to orange-red immediately
- Pulsing shadow effect begins
- Animation continues for 3 seconds
- Node returns to original appearance
- Multiple state changes extend the highlight duration

## Advantages Over Static Approach

### ✅ Benefits
- **Real-time responsiveness**: Immediate visual feedback on any state change
- **Universal compatibility**: Works with all entity types without domain-specific logic
- **Performance optimized**: No constant polling or static state evaluation
- **Memory efficient**: Proper cleanup prevents resource leaks
- **User-friendly**: Clear visual indication of system activity

### ✅ Technical Improvements
- **Event-driven architecture**: Leverages HA's native event system
- **Selective processing**: Only entities in view trigger animations
- **Proper lifecycle management**: Creation → Animation → Cleanup
- **Concurrent animations**: Multiple entities can pulse simultaneously
- **Non-blocking**: Animations don't interfere with graph interaction

## Testing Recommendations
1. **Toggle lights** - Should see immediate orange pulse
2. **Change thermostat** - Climate state changes trigger highlighting
3. **Motion detection** - Binary sensors pulse on state change
4. **Media playback** - Play/pause music to see media player highlight
5. **Navigation test** - Verify animations clear when changing graph focus

## Future Enhancements
- Configurable highlight duration (currently 3 seconds)
- Domain-specific highlight colors
- Animation intensity based on state change importance
- Sound notifications for critical state changes
- Historical activity indicators