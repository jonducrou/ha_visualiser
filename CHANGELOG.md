# Changelog

All notable changes to the Home Assistant Entity Visualizer will be documented in this file.

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