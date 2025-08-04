# UI Event Logging Feature - v0.6.2

## Overview
Added real-time UI logging to display all Home Assistant state change events, making it easy to debug and monitor the event-driven animation system.

## ✅ Features Added

### 1. Event Log Toggle Button
- **Location**: Top-right corner of graph area (next to Fit/Reset buttons)
- **Icon**: 📋 Events / 📋 Hide
- **Functionality**: Shows/hides the floating event log overlay

### 2. Floating Event Log Overlay
- **Position**: Fixed top-right corner of screen
- **Styling**: Home Assistant theme-aware with proper shadows and borders
- **Max Height**: 60% of viewport to prevent overflow
- **Auto-scroll**: Newest events appear at top

### 3. Event Classification
Events are visually distinguished by type:

#### Highlighted Events (Orange Border)
- **Entities in current graph** that trigger node animations
- **Orange background** with `#FF6B35` left border
- **High visibility** to show which events cause visual effects

#### Ignored Events (Gray)
- **Entities not in current graph** (still logged for debugging)
- **Muted styling** with gray border and reduced opacity
- **Lower visual priority** but still informative

### 4. Event Information Display
Each log entry shows:
- **Timestamp**: `hh:mm:ss` format for precise timing
- **Entity Name**: Friendly name with domain emoji icon
- **State Transition**: `old_state → new_state` format
- **Visual Distinction**: Color coding based on relevance

### 5. Log Management
- **Auto-limit**: Keeps only latest 50 events (prevents memory bloat)
- **Clear Button**: Manual log clearing functionality
- **Close Button**: Hide overlay with ✕ button
- **Newest First**: Latest events appear at top for immediate visibility

## Technical Implementation

### Event Capture (logEvent method - line 957)
```javascript
this.logEvent(entityId, newState, oldState, isInGraph);
```
- **Universal logging**: Captures ALL state changes, not just graph entities
- **Metadata extraction**: Timestamp, friendly names, domain classification
- **Memory management**: Ring buffer with 50-event limit

### UI Updates (updateEventLogUI method - line 990)
```javascript
const cssClass = entry.isInGraph ? 'highlight-event' : 'ignored-event';
```
- **Dynamic styling**: Different visual treatment based on graph relevance
- **Domain icons**: Emoji representations for quick entity type identification
- **Template-based rendering**: Clean HTML generation with proper escaping

### Visual Hierarchy
- **Highlighted events**: Clear visual priority with orange accents
- **Ignored events**: Muted but still visible for debugging
- **Timestamps**: Consistent formatting for event correlation
- **Auto-scrolling**: Latest events immediately visible

## CSS Styling

### Overlay Structure
```css
.event-log-overlay {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 400px;
  max-height: 60vh;
}
```

### Event Entry Types
- `.highlight-event`: Orange border, tinted background
- `.ignored-event`: Gray border, muted appearance
- `.event-timestamp`: Small, secondary text color
- `.event-entity`: Bold, primary text with emoji icon

## Usage Examples

### Debugging Scenarios
1. **Node not animating?** → Check if entity appears in log as "ignored-event"
2. **Too many animations?** → See all triggering events in real-time
3. **State changes not detected?** → Verify events are being captured
4. **Performance issues?** → Monitor event frequency

### Visual Feedback
- **Light toggle** → Immediate log entry with 💡 icon
- **Media player start** → 🔊 icon with playing state change
- **Motion sensor** → 📡 icon with on/off transitions
- **Climate adjustment** → 🌡️ icon with temperature changes

## Benefits

### For Developers
- **Real-time debugging**: See exactly what events are firing
- **Event correlation**: Match log entries to node animations
- **System monitoring**: Understand HA event frequency and patterns
- **Performance analysis**: Identify chatty entities or event storms

### For Users
- **Visual feedback**: Confirm system is responding to changes
- **Activity monitoring**: See which entities are active
- **Troubleshooting**: Understand why certain nodes aren't animating
- **System awareness**: Monitor Home Assistant activity in real-time

## Controls

### Event Log Toggle Button
- **Show**: Click "📋 Events" to open overlay
- **Hide**: Click "📋 Hide" or use ✕ button to close
- **Position**: Fixed in graph controls area

### Log Management
- **Clear**: Remove all entries (keeps initialization message)
- **Auto-scroll**: Newest events always visible at top
- **Auto-limit**: Maintains 50 most recent events

## Integration with Animation System

The logging system is fully integrated with the event-driven animation:

1. **Event Received** → Logged immediately with classification
2. **Graph Check** → Determines highlight vs ignored styling
3. **Animation Trigger** → Only highlighted events cause node pulsing
4. **Visual Correlation** → Easy to match log entries to screen effects

This provides complete visibility into the event pipeline from HA state changes through to visual effects, making debugging and monitoring straightforward and intuitive.