# Layout Debug Panel Examples

The debug panel allows real-time editing of vis.js layout options. Here are some useful configurations:

## Default Hierarchical Layout
```json
{
  "improvedLayout": true,
  "hierarchical": {
    "enabled": true,
    "direction": "UD",
    "sortMethod": "directed",
    "shakeTowards": "leaves",
    "edgeMinimization": true,
    "blockShifting": true,
    "parentCentralization": true,
    "levelSeparation": 120,
    "nodeSpacing": 120,
    "treeSpacing": 250
  },
  "randomSeed": 42
}
```

## Compact Layout (Less Spacing)
```json
{
  "improvedLayout": true,
  "hierarchical": {
    "enabled": true,
    "direction": "UD",
    "sortMethod": "directed",
    "shakeTowards": "leaves",
    "edgeMinimization": true,
    "blockShifting": true,
    "parentCentralization": true,
    "levelSeparation": 80,
    "nodeSpacing": 80,
    "treeSpacing": 150
  },
  "randomSeed": 42
}
```

## Wide Layout (More Horizontal Space)
```json
{
  "improvedLayout": true,
  "hierarchical": {
    "enabled": true,
    "direction": "UD",
    "sortMethod": "directed",
    "shakeTowards": "leaves",
    "edgeMinimization": true,
    "blockShifting": true,
    "parentCentralization": true,
    "levelSeparation": 150,
    "nodeSpacing": 200,
    "treeSpacing": 400
  },
  "randomSeed": 42
}
```

## Left-to-Right Layout
```json
{
  "improvedLayout": true,
  "hierarchical": {
    "enabled": true,
    "direction": "LR",
    "sortMethod": "directed",
    "shakeTowards": "leaves",
    "edgeMinimization": true,
    "blockShifting": true,
    "parentCentralization": true,
    "levelSeparation": 200,
    "nodeSpacing": 100,
    "treeSpacing": 200
  },
  "randomSeed": 42
}
```

## Force-Directed Layout (Non-Hierarchical)
```json
{
  "improvedLayout": true,
  "hierarchical": {
    "enabled": false
  },
  "randomSeed": 42
}
```

## Key Parameters

- **`levelSeparation`**: Distance between hierarchy levels (vertical spacing in UD mode)
- **`nodeSpacing`**: Minimum distance between nodes on the same level
- **`treeSpacing`**: Distance between different trees/branches  
- **`direction`**: Layout direction (`"UD"` = up-down, `"LR"` = left-right, `"RL"` = right-left, `"DU"` = down-up)
- **`sortMethod`**: How to sort nodes (`"hubsize"`, `"directed"`)
- **`randomSeed`**: Fixed seed for consistent layouts

## Usage Instructions

1. Click the 🔧 button in the top-right corner to open the debug panel
2. Edit the JSON in the text area
3. Changes are automatically applied after 500ms of typing
4. Use the "Apply" button for immediate application
5. Use "Reset" to return to default settings
6. Invalid JSON will show an error message

The panel validates JSON syntax and provides real-time feedback on layout changes.