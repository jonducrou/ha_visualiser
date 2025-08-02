"""Home Assistant Entity Visualizer integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.http import StaticPathConfig
from homeassistant.components import panel_custom

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
    await hass.http.async_register_static_paths([
        StaticPathConfig(
            "/hacsfiles/ha_visualiser",
            hass.config.path("custom_components/ha_visualiser/www"),
            False
        )
    ])
    
    # Register the panel
    await panel_custom.async_register_panel(
        hass,
        frontend_url_path="ha_visualiser",
        webcomponent_name="ha-visualiser-panel",
        sidebar_title="Entity Visualizer",
        sidebar_icon="mdi:graph",
        module_url="/hacsfiles/ha_visualiser/ha-visualiser-panel.js",
        config={},
        require_admin=False,
    )
    
    _LOGGER.info("Home Assistant Entity Visualizer integration loaded successfully")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Home Assistant Entity Visualizer from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Check if already set up to avoid duplicates
    if "graph_service" not in hass.data[DOMAIN]:
        # Initialize the graph service
        graph_service = GraphService(hass)
        hass.data[DOMAIN]["graph_service"] = graph_service
        
        # Register websocket API handlers
        async_register_websocket_handlers(hass)
        
        # Register the frontend panel
        await hass.http.async_register_static_paths([
            StaticPathConfig(
                "/hacsfiles/ha_visualiser",
                hass.config.path("custom_components/ha_visualiser/www"),
                False
            )
        ])
        
        # Register the panel
        await panel_custom.async_register_panel(
            hass,
            frontend_url_path="ha_visualiser",
            webcomponent_name="ha-visualiser-panel",
            sidebar_title="Entity Visualizer",
            sidebar_icon="mdi:graph",
            module_url="/hacsfiles/ha_visualiser/ha-visualiser-panel.js",
            config={},
            require_admin=False,
        )
    
    _LOGGER.info("Home Assistant Entity Visualizer integration loaded")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if DOMAIN in hass.data:
        hass.data.pop(DOMAIN)
    
    return True