"""Home Assistant Entity Visualizer integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .graph_service import GraphService
from .websocket_api import async_register_websocket_handlers

_LOGGER = logging.getLogger(__name__)

# Add a module-level log to confirm import
_LOGGER.info("ha_visualiser __init__.py module loaded")

PLATFORMS: list[str] = []


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Home Assistant Entity Visualizer integration."""
    _LOGGER.info("Setting up Home Assistant Entity Visualizer integration")
    
    if DOMAIN not in config:
        _LOGGER.debug("No configuration found for %s", DOMAIN)
        return True
    
    hass.data.setdefault(DOMAIN, {})
    
    # Initialize the graph service
    graph_service = GraphService(hass)
    hass.data[DOMAIN]["graph_service"] = graph_service
    
    # Register websocket API handlers
    async_register_websocket_handlers(hass)
    
    # Register the frontend panel
    hass.http.register_static_path(
        "/hacsfiles/ha_visualiser",
        hass.config.path("custom_components/ha_visualiser/www"),
        cache_headers=False,
    )
    
    # Register the panel
    hass.components.frontend.async_register_built_in_panel(
        component_name="custom",
        sidebar_title="Entity Visualizer",
        sidebar_icon="mdi:graph",
        frontend_url_path="ha_visualiser",
        config={
            "_panel_custom": {
                "name": "ha-visualiser-panel",
                "module_url": "/hacsfiles/ha_visualiser/ha-visualiser-panel.js",
            }
        },
    )
    
    _LOGGER.info("Home Assistant Entity Visualizer integration loaded successfully")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Home Assistant Entity Visualizer from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Initialize the graph service
    graph_service = GraphService(hass)
    hass.data[DOMAIN]["graph_service"] = graph_service
    
    # Register websocket API handlers
    async_register_websocket_handlers(hass)
    
    # Register the frontend panel
    hass.http.register_static_path(
        "/hacsfiles/ha_visualiser",
        hass.config.path("custom_components/ha_visualiser/www"),
        cache_headers=False,
    )
    
    # Register the panel
    hass.components.frontend.async_register_built_in_panel(
        component_name="custom",
        sidebar_title="Entity Visualizer",
        sidebar_icon="mdi:graph",
        frontend_url_path="ha_visualiser",
        config={
            "_panel_custom": {
                "name": "ha-visualiser-panel",
                "module_url": "/hacsfiles/ha_visualiser/ha-visualiser-panel.js",
            }
        },
    )
    
    _LOGGER.info("Home Assistant Entity Visualizer integration loaded")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if DOMAIN in hass.data:
        hass.data.pop(DOMAIN)
    
    return True