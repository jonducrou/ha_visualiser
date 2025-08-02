# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Home Assistant custom integration that visualizes entities as an interactive graph. Users can search for entities, view their neighborhood relationships, and navigate through the graph. The tool helps understand entity connections based on devices, areas, automations, and templates.

## Architecture

**Custom Integration Structure:**
```
custom_components/ha_visualiser/
├── __init__.py              # Integration setup
├── manifest.json            # HACS metadata  
├── config_flow.py           # Configuration flow
├── graph_service.py         # Backend graph analysis
└── www/
    └── ha-visualiser-panel.js  # Frontend panel
```

**Technology Stack:**
- Backend: Python (HA integration framework)
- Frontend: JavaScript with vis.js (encapsulated for easy replacement)
- Data: HA state API, entity/device/area registries
- Communication: HA websocket API

## Key Implementation Details

**Relationship Detection:**
- Device-based: `hass.config.entities` for device groupings
- Area-based: `hass.config.areas` for zone relationships  
- Automation-based: Parse automation configs for dependencies
- Template-based: Parse template references

**Graph Visualization:**
- Search box → select entity → show neighborhood
- Click navigation with highlight/fade effects
- Domain/area filtering with hidden node count badges
- Server-side graph analysis, client-side display

## Development Commands

No specific build commands yet - this is a pure HA custom integration.

**Testing:**
- Test in HA development environment
- Manual testing via HA frontend panel
- Future: Add pytest for backend components

## Development Workflow

1. Develop/test in HA `custom_components/` directory
2. Use HA developer tools for debugging
3. Test frontend via HA panel interface
4. HACS validation for distribution