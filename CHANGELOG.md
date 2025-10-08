# Changelog

All notable changes to the Home Assistant Entity Visualizer will be documented in this file.

## [0.8.18] - 2025-10-08

### Major Improvement
- **🔧 Template Compiler Integration**: Now uses Home Assistant's built-in template compiler for dependency detection
- **✨ More Reliable**: Uses `Template.async_render_to_info()` - the same method Developer Tools uses
- **📊 Better Coverage**: Handles complex templates with multi-line syntax, nested structures, all Jinja2 features

### Enhanced Template Detection
- **Template Select Entities**: Now correctly detects dependencies in template select helpers (Issue #15)
- **All Template Types**: Improved detection for sensors, binary sensors, switches, buttons, numbers, text
- **Automation Templates**: Better handling of template conditions in automations and scripts
- **Complex Templates**: Reliably parses templates that regex patterns would miss

### Technical
- Added `_extract_template_entities_using_ha()` using `Template.async_render_to_info()`
- Updated all template parsing to use HA's compiler instead of regex
- Graceful fallback to regex parsing if template compilation fails
- Template dependency detection now stays in sync with HA's capabilities

## [0.8.13] - 2025-09-04

### Major Fix
- **🎛️ Config Flow Enabled**: Integration can now be added via Settings → Integrations → Add Integration → Entity Visualizer
- **🔧 Root Cause Solution**: Fixed the core issue where `config_flow: false` prevented integration initialization for most users
- **📱 User-Friendly Setup**: Clear, helpful messages guide users through the setup process

### Enhanced User Experience
- **✨ Setup Description**: Rich description in config flow explains what users get and how to use it
- **🎯 Clear Instructions**: Step-by-step guidance from installation to accessing the panel
- **🔄 Backward Compatibility**: Existing YAML configurations still supported via automatic import

### Improved Diagnostics
- **📊 Enhanced Logging**: Comprehensive diagnostics to help troubleshoot any remaining issues
- **🔍 File Verification**: Automatic checks for missing frontend files with clear error messages
- **✅ Setup Confirmation**: Clear success messages with emojis to confirm successful installation
- **🧹 Better Cleanup**: Improved error handling and cleanup on failed installations

### Technical
- **Config Flow Implementation**: Added user-friendly `config_flow.py` with detailed setup messaging
- **Dual Setup Support**: Handles both UI config entries and YAML imports seamlessly
- **Frontend File Validation**: Checks for missing www directory and JS files before panel registration
- **Diagnostic Logging**: All setup steps now logged with clear success/failure indicators

## [0.8.12] - 2025-09-03

### Attempted Fix
- **📍 Panel Registration Robustness**: Attempted fix for side menu/panel not appearing after installation (Issue #11)
- **🔄 Setup Logic Improvement**: Made panel registration more robust to handle edge cases during HA restarts
- **⚠️ Experimental**: This is an attempted fix based on code analysis - unable to reproduce the issue locally

### Technical
- Added `_ensure_panel_registered()` function to retry panel registration in edge case scenarios
- Modified setup logic to always verify panel registration even when services are already initialized
- Enhanced error handling and logging around panel registration
- **Note**: If issue persists, we need more detailed reproduction steps and log files

## [0.8.11] - 2025-09-02

### Added
- **🔄 Persistent User Preferences**: Show Areas, Depth, and Layout settings now remembered between sessions
- **💾 Client-Side Storage**: All preferences stored locally using browser localStorage - completely private
- **⚡ Instant Preference Saving**: Settings automatically saved as soon as user changes them

### Enhanced
- **🎯 Smart Defaults**: Preferences gracefully fall back to sensible defaults when localStorage unavailable
- **🛡️ Error Resilience**: Comprehensive error handling for localStorage edge cases and corrupted data
- **📱 Cross-Session Experience**: Your preferred settings persist across browser restarts and HA reboots

### Technical
- Added `loadUserPreferences()`, `saveUserPreferences()`, and `applyUserPreferences()` methods
- Implemented localStorage-based preference management with validation and sanitization
- Enhanced all option event handlers to save preferences immediately on change
- Removed hardcoded HTML defaults in favor of dynamic preference application

## [0.8.10] - 2025-09-02

### Fixed
- **"No visualisations" Error**: Fixed critical error where graph visualization failed with "'NoneType' object is not iterable" (Issue #10)
- **Defensive Programming**: Added comprehensive error handling and validation in both WebSocket API and graph service
- **Safe Fallbacks**: Graph service now returns empty safe results on any error instead of corrupted data

### Technical
- Added try-catch blocks around all graph building methods in `graph_service.py`
- Added validation for nodes and edges data structures in `websocket_api.py`
- Enhanced error logging to help identify root causes of graph building failures
- Improved data structure validation before JSON serialization

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