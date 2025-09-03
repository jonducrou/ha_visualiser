"""
Pytest configuration and shared fixtures for HA Visualiser testing.

This module provides mock fixtures for Home Assistant components to enable 
unit testing without requiring a full HA installation.
"""
import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, List, Any


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = Mock()
    
    # Mock states
    hass.states = Mock()
    hass.states.get = Mock()
    hass.states.async_entity_ids = Mock(return_value=[
        'light.living_room',
        'light.kitchen', 
        'sensor.temperature',
        'sensor.humidity',
        'switch.fan',
        'automation.morning_routine',
        'zone.home',
        'device_tracker.phone'
    ])
    
    # Mock config entries
    hass.config_entries = Mock()
    hass.config_entries.async_entries = Mock(return_value=[])
    
    # Mock data storage
    hass.data = {}
    
    # Mock WebSocket calls
    hass.callWS = AsyncMock()
    
    return hass


@pytest.fixture 
def mock_entity_registry():
    """Create a mock entity registry."""
    registry = Mock()
    
    # Create mock entity entries
    mock_entities = {
        'light.living_room': Mock(
            entity_id='light.living_room',
            device_id='device_living_room_light',
            area_id='living_room',
            domain='light',
            labels=['lighting']
        ),
        'sensor.temperature': Mock(
            entity_id='sensor.temperature', 
            device_id='device_temp_sensor',
            area_id='living_room',
            domain='sensor',
            labels=[]
        ),
        'automation.morning_routine': Mock(
            entity_id='automation.morning_routine',
            device_id=None,
            area_id=None,
            domain='automation',
            labels=['routine']
        )
    }
    
    registry.entities = mock_entities
    registry.async_get = Mock(side_effect=lambda entity_id: mock_entities.get(entity_id))
    
    return registry


@pytest.fixture
def mock_device_registry():
    """Create a mock device registry."""
    registry = Mock()
    
    # Create mock devices
    mock_devices = {
        'device_living_room_light': Mock(
            id='device_living_room_light',
            name='Living Room Light',
            name_by_user='Smart Bulb',
            area_id='living_room',
            disabled_by=None,
            labels=['smart_home']
        ),
        'device_temp_sensor': Mock(
            id='device_temp_sensor',
            name='Temperature Sensor',
            name_by_user=None,
            area_id='living_room', 
            disabled_by=None,
            labels=[]
        )
    }
    
    registry.devices = mock_devices
    registry.async_get = Mock(side_effect=lambda device_id: mock_devices.get(device_id))
    
    return registry


@pytest.fixture
def mock_area_registry():
    """Create a mock area registry."""
    registry = Mock()
    
    # Create mock areas
    mock_areas = {
        'living_room': Mock(
            id='living_room',
            name='Living Room',
            labels=['main_floor']
        ),
        'kitchen': Mock(
            id='kitchen', 
            name='Kitchen',
            labels=['main_floor']
        )
    }
    
    registry.areas = mock_areas
    registry.async_get_area = Mock(side_effect=lambda area_id: mock_areas.get(area_id))
    
    return registry


@pytest.fixture
def mock_label_registry():
    """Create a mock label registry."""
    registry = Mock()
    
    # Create mock labels  
    mock_labels = {
        'lighting': Mock(
            label_id='lighting',
            name='Lighting'
        ),
        'routine': Mock(
            label_id='routine',
            name='Routine'
        )
    }
    
    registry.async_get_label = Mock(side_effect=lambda label_id: mock_labels.get(label_id))
    
    return registry


@pytest.fixture
def mock_graph_service(mock_hass, mock_entity_registry, mock_device_registry, 
                      mock_area_registry, mock_label_registry):
    """Create a GraphService instance with mocked dependencies."""
    # Mock the registry imports to avoid HA dependency issues
    import sys
    from unittest.mock import Mock
    
    # Create mock modules
    mock_entity_registry_module = Mock()
    mock_entity_registry_module.async_get = Mock(return_value=mock_entity_registry)
    
    mock_device_registry_module = Mock() 
    mock_device_registry_module.async_get = Mock(return_value=mock_device_registry)
    
    mock_area_registry_module = Mock()
    mock_area_registry_module.async_get = Mock(return_value=mock_area_registry)
    
    mock_label_registry_module = Mock()
    mock_label_registry_module.async_get = Mock(return_value=mock_label_registry)
    
    # Mock the imports
    sys.modules['homeassistant.helpers.entity_registry'] = mock_entity_registry_module
    sys.modules['homeassistant.helpers.device_registry'] = mock_device_registry_module  
    sys.modules['homeassistant.helpers.area_registry'] = mock_area_registry_module
    sys.modules['homeassistant.helpers.label_registry'] = mock_label_registry_module
    
    # Now we can import and create GraphService
    try:
        from custom_components.ha_visualiser.graph_service import GraphService
        return GraphService(mock_hass)
    except ImportError:
        # If import still fails, return a mock
        return Mock()


@pytest.fixture
def sample_graph_data():
    """Sample graph data for testing."""
    return {
        'nodes': [
            {
                'id': 'light.living_room',
                'label': 'Living Room Light', 
                'domain': 'light',
                'area': 'Living Room',
                'device_id': 'device_living_room_light',
                'state': 'on',
                'icon': 'mdi:lightbulb'
            },
            {
                'id': 'sensor.temperature',
                'label': 'Temperature Sensor',
                'domain': 'sensor', 
                'area': 'Living Room',
                'device_id': 'device_temp_sensor',
                'state': '22.5',
                'icon': 'mdi:thermometer'
            }
        ],
        'edges': [
            {
                'from_node': 'device_living_room_light',
                'to_node': 'light.living_room',
                'relationship_type': 'device_contains',
                'label': 'contains'
            }
        ],
        'center_node': 'light.living_room'
    }


@pytest.fixture  
def mock_websocket_connection():
    """Create a mock WebSocket connection."""
    connection = Mock()
    connection.send_result = Mock()
    connection.send_error = Mock() 
    return connection


@pytest.fixture
def sample_preferences():
    """Sample user preferences for testing."""
    return {
        'showAreas': True,
        'depth': 3,
        'layout': 'hierarchical'
    }


@pytest.fixture
def mock_localStorage():
    """Mock localStorage for preference testing."""
    storage = {}
    
    def getItem(key):
        return storage.get(key)
    
    def setItem(key, value):
        storage[key] = str(value)
    
    def clear():
        storage.clear()
        
    mock = Mock()
    mock.getItem = Mock(side_effect=getItem)
    mock.setItem = Mock(side_effect=setItem) 
    mock.clear = Mock(side_effect=clear)
    mock._storage = storage  # For inspection in tests
    
    return mock