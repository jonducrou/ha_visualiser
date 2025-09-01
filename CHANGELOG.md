# Changelog

All notable changes to the Home Assistant Entity Visualizer will be documented in this file.

## [0.8.9] - 2025-09-01

### Fixed
- **CRITICAL: Home Assistant Boot Failures**: Fixed critical issue where v0.8.8 prevented HA from starting
- **Safer Auto-Initialization**: Restored safety checks while preserving automatic sidebar setup
- **Duplicate Initialization Prevention**: Added checks to prevent conflicts between setup methods
- **Comprehensive Error Handling**: Proper cleanup on initialization failures

### Technical
- Restored early return checks in `async_setup()` for safer initialization
- Implemented shared `_setup_integration()` logic to prevent YAML/config entry conflicts  
- Added comprehensive error handling and cleanup on failures
- Preserved automatic sidebar functionality with safer implementation

## [0.8.8] - 2025-09-01

### Fixed
- **Bidirectional Automation Relationships**: Fixed automation relationships not working from devices, areas, zones, labels, and scenes (Issue #5)
- **Automatic Sidebar Setup**: Removed config flow requirement - sidebar now appears automatically after installation (Issues #8, #9)

### Technical
- Added automation relationship checks to all special node handlers to prevent early return bugs
- Removed `config_flow: true` and made integration auto-setup when files are present
- Architectural fix ensures universal relationship detection across all node types

## [0.8.7] - 2025-08-27

### Fixed
- **Zone Self-References**: Zones no longer show relationships to themselves (Issue #6)
- **Device Reference Detection**: Enhanced automation parsing to detect device ID references

### Technical
- Added self-reference filtering in zone relationship methods
- Improved device ID detection in automation configurations

## [0.8.6] - 2025-08-22

### Fixed
- **Double-Click Navigation**: Fixed regression where double-click stopped working after adding entity dialogs (Issue #4)

### Technical
- Implemented proper click/double-click event handling with 300ms timeout
- Single-click opens dialogs, double-click navigates, no conflicts

## [0.8.5] - 2025-08-21

### Fixed
- **Scene Entity Relationships**: Enhanced scene parsing to handle multiple configuration formats (Issue #3)

### Added
- Support for `entity_data`, `states`, and `snapshot` scene formats
- UUID resolution for scene entities
- Comprehensive debug logging for scene troubleshooting

## [0.8.4] - 2025-08-21

### Added
- **Native HA Entity Dialogs**: Single-click entities to open Home Assistant more-info dialogs
- Seamless integration with Home Assistant's native UI

### Removed
- Technical debug panel (production-ready interface)

### Fixed
- Dialog z-index layering issues
- Event handling conflicts between dialogs and navigation

## [0.5.0] - 2025-01-03

### Added
- **Label System Integration**: Complete support for Home Assistant labels
  - Label nodes appear in graph with 🏷️ icon and light yellow styling
  - Search functionality includes labels with usage statistics
  - Bidirectional navigation: click labels to see labeled items, click items to see their labels
  - Support for entity labels, device labels, and area labels
  - Cross-version compatibility with manual filtering fallbacks

### Fixed
- Label registry compatibility errors across different Home Assistant versions
- Entity validation for label nodes to prevent "not found" errors
- Import scope issues with registry helper functions

### Technical
- Added label registry integration with `_get_*_for_label` compatibility methods
- Implemented manual filtering approach for universal HA version support
- Updated frontend visualization to support label relationship patterns
- Enhanced WebSocket API to handle label node validation

---

## [0.4.5] - 2024-12-XX

### Added
- Professional visual design overhaul with entity icons
- Advanced layout algorithms with edge crossing minimization
- Project organization with proper test/debug structure
- Comprehensive documentation update

### Fixed
- Automation relationship detection with UUID resolution
- Symmetrical navigation for all relationship types
- Visual design consistency across all node types

---

## [0.4.0] - 2024-12-XX

### Added
- Complete automation relationship support
- Symmetrical bidirectional navigation
- Focus node highlighting
- Advanced error handling and logging

---

## [0.3.0] - 2024-12-XX

### Added
- Visual design improvements
- Entity icons and clean styling
- Enhanced user interface

---

## [0.2.0] - 2024-12-XX

### Added
- 2-level neighborhood depth
- Zone support and geographic relationships
- Consistent arrow directions
- Device and area node support

---

## [0.1.0] - 2024-12-XX

### Added
- Initial release
- Basic entity relationship visualization
- Search functionality
- Device and area relationships