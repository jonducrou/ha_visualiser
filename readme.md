# Home Assistant Entity Visualizer

A Home Assistant custom integration that visualizes your entities as an interactive graph, helping you understand and manage the relationships in your smart home setup.

## Features

- **Interactive Graph Visualization**: View entities as nodes with relationships shown as edges
- **Neighborhood Navigation**: Focus on a selected entity and its connected neighbors, then navigate to explore other areas
- **Multiple Relationship Types**: Automatically detects connections based on:
  - Device groupings
  - Area/zone associations  
  - Automation dependencies
  - Template references
- **Smart Filtering**: Filter by entity domain, area, or relationship type while showing hidden node counts
- **Embedded in Home Assistant**: Appears as a panel in your HA sidebar with integrated authentication

## Use Cases

- Understand which entities are connected before making changes
- Troubleshoot automation dependencies
- Explore your smart home setup visually
- Identify orphaned or unused entities
- Plan device and area organization

## Installation

This integration will be available through HACS (Home Assistant Community Store):

1. Install HACS if you haven't already
2. Add this repository to HACS
3. Download "Home Assistant Entity Visualizer"
4. Restart Home Assistant
5. The visualizer will appear in your sidebar

## Usage

1. Open the "Entity Visualizer" panel from your HA sidebar
2. Use the search box to find and select an entity of interest
3. View the entity's neighborhood in the interactive graph
4. Click on other nodes to navigate and explore different areas
5. Use filters to focus on specific types of entities or relationships

## Requirements

- Home Assistant 2023.7 or later
- Modern web browser with JavaScript enabled
