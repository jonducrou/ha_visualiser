# Technical Decisions & Known Issues

This document tracks technical approaches that have been attempted, what works, what doesn't, and why. This prevents repeating failed approaches and provides context for future development decisions.

## Testing Infrastructure

### What Works ✅
- **Code Syntax Validation**: `python3 tests/validate_code.py` - Reliable for basic syntax checking
- **File Serving Tests**: `bash tests/test_file_serving.sh` - Basic file existence and structure validation
- **Manual Testing**: Testing in actual HA development environment provides the most reliable results

### What Doesn't Work ❌
- **pytest in CI/Development Environment**: 
  - **Issue**: `ModuleNotFoundError: No module named 'pytest'` and `ModuleNotFoundError: No module named 'custom_components'`
  - **Root Cause**: 
    1. Missing pytest installation (`pip install pytest` not run)
    2. Missing Home Assistant core dependencies (`ModuleNotFoundError: No module named 'homeassistant'`)
    3. Integration imports HA modules (`from homeassistant.config_entries import ConfigEntry`) which aren't available outside HA
  - **Attempted Solutions**: 
    - Direct pytest execution: FAILED - missing pytest dependency
    - test_runner.py with fallback logic: FAILED - still tries to import HA modules
    - Adding current directory to Python path: FAILED - HA dependencies still missing
  - **Decision**: Current test infrastructure requires Home Assistant environment. For development, use syntax validation only.

### Test Strategy That Works ✅
1. **Syntax Validation**: Use `validate_code.py` for Python syntax checking
2. **File Structure**: Use `test_file_serving.sh` for basic file checks  
3. **Integration Testing**: Copy to HA `custom_components/` and test in live environment
4. **Manual Verification**: Use HA developer tools and logs for debugging

### Recommended Development Testing Workflow ✅
```bash
# 1. Syntax validation (reliable in development environment)
python3 tests/validate_code.py

# 2. Basic file structure check  
bash tests/test_file_serving.sh

# 3. Manual integration testing
# - Copy files to HA custom_components/ha_visualiser/
# - Restart Home Assistant
# - Check logs for errors
# - Test frontend panel functionality
# - Verify bug fixes with actual HA entities
```

### Why Current pytest Approach Fails ❌
The existing `tests/test_runner.py` and `tests/test_graph_service.py` assume a full Home Assistant environment with:
- Home Assistant core installed (`homeassistant` module)
- Entity/device/area registries available
- WebSocket infrastructure running
- Full HA state management

**To Fix This Would Require**:
- Complex HA environment mocking (high maintenance overhead)
- Installing HA core as development dependency (heavyweight)
- Rewriting tests to avoid HA imports (significant effort)

**Current Decision**: Development environment testing focuses on syntax validation. Comprehensive testing happens in actual HA environment.

## HACS Submission

### What Works ✅
- **Repository Structure**: HACS-compliant structure with proper manifest.json
- **GitHub Actions**: Both HACS and hassfest validation actions pass
- **Release Strategy**: Tagged releases with proper versioning
- **Documentation**: Comprehensive README with examples and features

### What Doesn't Work ❌
- **Auto-submission**: HACS PRs get auto-rejected for unknown reasons
- **Previous Attempts**: 
  - PR #4007: Auto-rejected immediately
  - **Likely Causes**: Unknown, possibly too many recent submissions or missing requirements

### Current Approach ✅
- **Manual PR Preparation**: Create branch and PR content without auto-submitting
- **Review First**: Allow manual review of PR content before submission
- **HACS_PR_DRAFT.md**: Template with proper HACS formatting and requirements

## Bug Fix Strategy

### What Works ✅
- **Device Trigger Issues**: Fixed by modifying `_extract_entities_from_config()` to use device nodes instead of all device entities
- **Group Helper Detection**: Enhanced with comprehensive attribute checking and debug logging
- **GitHub Issue Management**: Close issues with detailed technical explanations
- **Version Management**: Semantic versioning with clear changelog documentation

### Development Workflow That Works ✅
1. **Issue Investigation**: Read code, understand problem scope
2. **Targeted Fixes**: Modify specific functions rather than broad refactoring  
3. **Testing**: Use syntax validation + manual HA testing
4. **Documentation**: Update README, plan.md, and commit messages with details
5. **Version Bump**: Increment version and create tagged release
6. **Issue Closure**: Close GitHub issues with technical explanation

## Code Architecture

### What Works ✅
- **GraphService**: Centralized entity relationship detection
- **WebSocket API**: Real-time communication with frontend
- **Modular Relationship Detection**: Separate methods for different relationship types
- **Error Handling**: Comprehensive logging and graceful failures

### What Doesn't Work ❌
- **Complex Refactoring**: Large-scale changes often introduce new issues
- **Over-engineering**: Simple, targeted fixes work better than complex solutions

## Dependencies & Environment

### What Works ✅
- **Home Assistant Native APIs**: Using `hass.states`, `hass.config_entries`, etc.
- **Standard Library**: Using built-in Python modules when possible
- **Minimal External Dependencies**: Keep requirements.txt minimal

### What Doesn't Work ❌
- **Heavy External Libraries**: Avoid complex dependencies that may conflict with HA
- **Development Environment Testing**: Testing outside HA environment has limited value

## Key Lessons Learned

1. **Keep It Simple**: Targeted fixes work better than comprehensive refactoring
2. **Test in HA Environment**: Manual testing in actual HA is more reliable than unit tests
3. **Document Everything**: Clear commit messages and issue explanations prevent confusion
4. **Version Management**: Always bump version after significant changes
5. **HACS Process**: Manual review and submission works better than auto-submission

## Major Architectural Lessons (v0.8.7-0.8.8)

### Early Return Bug Pattern ❌
- **Issue**: Special node types (device, area, zone, label, scene) returned early, never reaching automation relationship checking
- **Impact**: Caused bidirectional relationship bugs (issue #5)
- **Root Cause**: Each special node handler had its own early return without calling shared relationship methods
- **Lesson**: When adding new node types, ensure they don't skip universal relationship checks

### Config Flow vs Auto-Setup ❌→✅
- **Original Approach**: Required manual integration setup via Settings > Integrations
- **Problem**: Users expected automatic setup after file installation (issues #8, #9)
- **Solution**: Removed `config_flow: true`, made `async_setup()` always initialize
- **Lesson**: For simple integrations, auto-setup provides better user experience than config flows

### Relationship Detection Architecture ✅
- **What Works**: Having universal relationship methods that can be called from anywhere
- **What Doesn't Work**: Node-specific handlers that bypass universal checks
- **Pattern**: All node types should call automation/script/scene relationship methods before returning

### Bug Investigation Methodology ✅
1. **Read GitHub Issue Carefully**: Issue #5 was reopened - our fix didn't actually work
2. **Trace Code Flow**: Found that device nodes returned early, never reaching automation code
3. **Fix Root Cause**: Add relationship checks to ALL special node handlers, not just regular entities
4. **Verify Fix**: Ensure the architectural problem is solved, not just the symptom

## Current Status (v0.8.8)

- ✅ **Testing**: Syntax validation reliable, manual HA testing preferred
- ✅ **Bug Fixes**: All major architectural issues resolved (bidirectional relationships, auto-setup)
- ✅ **User Experience**: Installation now automatic, no manual config flow required
- ✅ **GitHub Issues**: All open issues (#5, #8, #9) resolved and closed
- ✅ **Architecture**: Universal relationship checking ensures consistent behavior across node types

## Future Considerations

- **Testing**: Consider pytest setup with proper HA environment mocking (low priority)
- **HACS**: Monitor submission requirements for any changes
- **Architecture**: Current modular approach works well, avoid major refactoring
- **Performance**: Only optimize if specific performance issues reported by users