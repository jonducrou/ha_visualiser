"""Home Assistant Entity Visualizer integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.http import StaticPathConfig
from homeassistant.components import panel_custom
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import DOMAIN
from .graph_service import GraphService
from .websocket_api import async_register_websocket_handlers

_LOGGER = logging.getLogger(__name__)

# Add a module-level log to confirm import
_LOGGER.info("ha_visualiser __init__.py module loaded")

PLATFORMS: list[str] = []

# Configuration schema - empty since this integration has no YAML config
CONFIG_SCHEMA = vol.Schema({DOMAIN: cv.empty_config_schema}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Home Assistant Entity Visualizer integration."""
    _LOGGER.info("Setting up Home Assistant Entity Visualizer integration")
    
    # Check if already initialized to prevent conflicts
    if DOMAIN in hass.data:
        _LOGGER.debug("Integration already initialized, skipping setup")
        return True
    
    # For config_flow: false integrations, always initialize when files are present
    # This provides automatic setup without requiring manual configuration
    if DOMAIN not in config:
        _LOGGER.debug("No YAML configuration found, initializing automatically for sidebar setup")
        # Create minimal config to proceed with initialization
        config = {DOMAIN: {}}
    
    try:
        return await _setup_integration(hass, config)
    except Exception as e:
        _LOGGER.error("Failed to setup integration: %s", e, exc_info=True)
        # Clean up on failure to prevent partial initialization
        if DOMAIN in hass.data:
            hass.data.pop(DOMAIN)
        return False


async def _ensure_panel_registered(hass: HomeAssistant) -> bool:
    """Ensure the panel is registered, used for retry scenarios."""
    _LOGGER.debug("Ensuring panel registration")
    
    try:
        # Register static paths if not already registered
        await hass.http.async_register_static_paths([
            StaticPathConfig(
                "/api/ha_visualiser/static",
                hass.config.path("custom_components/ha_visualiser/www"),
                False
            )
        ])
        _LOGGER.debug("Static paths registered successfully")
    except Exception as e:
        # Static paths might already be registered, this is not critical
        _LOGGER.debug("Static paths registration skipped or failed: %s", e)
    
    # Register the panel with defensive error handling
    try:
        await panel_custom.async_register_panel(
            hass,
            frontend_url_path="ha_visualiser",
            webcomponent_name="ha-visualiser-panel",
            sidebar_title="Entity Visualizer",
            sidebar_icon="mdi:graph",
            module_url="/api/ha_visualiser/static/ha-visualiser-panel.js",
            config={},
            require_admin=False,
        )
        _LOGGER.info("Panel registered successfully")
        return True
    except ValueError as e:
        if "Overwriting panel" in str(e):
            _LOGGER.debug("Panel already registered, skipping registration")
            return True
        else:
            _LOGGER.error("Failed to register panel: %s", e)
            return False
    except Exception as e:
        _LOGGER.error("Unexpected error during panel registration: %s", e)
        return False


async def _setup_integration(hass: HomeAssistant, config: ConfigType) -> bool:
    """Shared setup logic for both YAML and config entry setup."""
    hass.data.setdefault(DOMAIN, {})
    
    # Check if already set up to avoid duplicates
    if "graph_service" in hass.data[DOMAIN]:
        _LOGGER.debug("Integration services already initialized, checking panel registration")
        # Even if services are initialized, we need to ensure panel is registered
        # This handles cases where panel registration failed on previous attempts
        return await _ensure_panel_registered(hass)
    
    # Initialize the graph service
    graph_service = GraphService(hass)
    hass.data[DOMAIN]["graph_service"] = graph_service
    
    # Register websocket API handlers
    async_register_websocket_handlers(hass)
    
    # Register the frontend panel
    panel_result = await _ensure_panel_registered(hass)
    if not panel_result:
        _LOGGER.error("Failed to register panel during initial setup")
        return False
    
    _LOGGER.info("Home Assistant Entity Visualizer integration setup completed")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Home Assistant Entity Visualizer from a config entry."""
    _LOGGER.info("Setting up Entity Visualizer from config entry")
    
    # Check if already initialized via YAML setup to prevent conflicts
    if DOMAIN in hass.data and "graph_service" in hass.data[DOMAIN]:
        _LOGGER.debug("Integration already initialized via YAML, skipping config entry setup")
        return True
    
    try:
        result = await _setup_integration(hass, {})
        if result:
            _LOGGER.info("Entity Visualizer loaded successfully via config entry")
        return result
    except Exception as e:
        _LOGGER.error("Failed to setup integration from config entry: %s", e, exc_info=True)
        # Clean up on failure
        if DOMAIN in hass.data:
            hass.data.pop(DOMAIN)
        return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Clean up stored data
    if DOMAIN in hass.data:
        hass.data.pop(DOMAIN)
    
    # Try to remove the panel (this helps with clean restarts)
    try:
        hass.components.frontend.async_remove_panel("ha_visualiser")
        _LOGGER.debug("Panel removed successfully during unload")
    except (AttributeError, KeyError):
        # Panel wasn't registered or already removed
        _LOGGER.debug("Panel was not registered or already removed")
    except Exception as e:
        # Log but don't fail unload for panel removal issues
        _LOGGER.debug("Could not remove panel during unload: %s", e)
    
    _LOGGER.info("Home Assistant Entity Visualizer integration unloaded")
    return True