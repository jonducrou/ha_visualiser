"""Tests for the graph service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry, device_registry, area_registry

from custom_components.ha_visualiser.graph_service import GraphService, GraphNode


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.states = Mock()
    hass.states.async_entity_ids.return_value = [
        "light.living_room",
        "switch.kitchen", 
        "sensor.temperature",
        "automation.morning_routine"
    ]
    
    # Mock states
    mock_states = {
        "light.living_room": Mock(
            entity_id="light.living_room",
            state="on", 
            attributes={"friendly_name": "Living Room Light"}
        ),
        "switch.kitchen": Mock(
            entity_id="switch.kitchen",
            state="off",
            attributes={"friendly_name": "Kitchen Switch"}
        ),
        "sensor.temperature": Mock(
            entity_id="sensor.temperature", 
            state="20.5",
            attributes={"friendly_name": "Temperature Sensor", "unit_of_measurement": "°C"}
        ),
        "automation.morning_routine": Mock(
            entity_id="automation.morning_routine",
            state="on",
            attributes={
                "friendly_name": "Morning Routine",
                "configuration": {
                    "trigger": [{"entity_id": "sensor.temperature"}],
                    "action": [{"entity_id": "light.living_room"}]
                }
            }
        )
    }
    hass.states.get.side_effect = lambda entity_id: mock_states.get(entity_id)
    
    return hass


@pytest.fixture
def mock_registries():
    """Create mock registries."""
    entity_reg = Mock(spec=entity_registry.EntityRegistry)
    device_reg = Mock(spec=device_registry.DeviceRegistry) 
    area_reg = Mock(spec=area_registry.AreaRegistry)
    
    # Mock entity entries
    entity_entries = {
        "light.living_room": Mock(
            entity_id="light.living_room",
            device_id="device_1",
            area_id="area_1"
        ),
        "switch.kitchen": Mock(
            entity_id="switch.kitchen", 
            device_id="device_2",
            area_id="area_2"
        ),
        "sensor.temperature": Mock(
            entity_id="sensor.temperature",
            device_id="device_1", 
            area_id="area_1"
        )
    }
    entity_reg.async_get.side_effect = lambda entity_id: entity_entries.get(entity_id)
    
    # Mock device entries
    devices = {
        "device_1": Mock(device_id="device_1", name="Smart Hub", area_id="area_1"),
        "device_2": Mock(device_id="device_2", name="Kitchen Switch", area_id="area_2")
    }
    device_reg.async_get.side_effect = lambda device_id: devices.get(device_id)
    
    # Mock area entries  
    areas = {
        "area_1": Mock(area_id="area_1", name="Living Room"),
        "area_2": Mock(area_id="area_2", name="Kitchen")
    }
    area_reg.async_get_area.side_effect = lambda area_id: areas.get(area_id)
    
    return entity_reg, device_reg, area_reg


@pytest.fixture
def graph_service(mock_hass, mock_registries):
    """Create a graph service instance with mocked dependencies."""
    entity_reg, device_reg, area_reg = mock_registries
    
    with patch("homeassistant.helpers.entity_registry.async_get", return_value=entity_reg), \
         patch("homeassistant.helpers.device_registry.async_get", return_value=device_reg), \
         patch("homeassistant.helpers.area_registry.async_get", return_value=area_reg):
        service = GraphService(mock_hass)
    
    return service


class TestGraphService:
    """Test the GraphService class."""
    
    async def test_search_entities(self, graph_service):
        """Test entity search functionality."""
        results = await graph_service.search_entities("living")
        
        assert len(results) == 1
        assert results[0]["entity_id"] == "light.living_room"
        assert results[0]["friendly_name"] == "Living Room Light"
        assert results[0]["domain"] == "light"
        
    async def test_search_entities_by_id(self, graph_service):
        """Test entity search by entity ID."""
        results = await graph_service.search_entities("temperature")
        
        assert len(results) == 1
        assert results[0]["entity_id"] == "sensor.temperature"
        
    async def test_create_node(self, graph_service):
        """Test node creation."""
        node = await graph_service._create_node("light.living_room")
        
        assert isinstance(node, GraphNode)
        assert node.id == "light.living_room"
        assert node.label == "Living Room Light"
        assert node.domain == "light"
        assert node.area == "Living Room"
        assert node.state == "on"
        
    async def test_create_node_nonexistent(self, graph_service):
        """Test node creation for non-existent entity."""
        node = await graph_service._create_node("nonexistent.entity")
        
        assert node is None
        
    async def test_find_device_relationships(self, graph_service, mock_registries):
        """Test device-based relationship detection.""" 
        entity_reg, _, _ = mock_registries
        
        # Mock device entities function
        with patch("homeassistant.helpers.entity_registry.async_entries_for_device") as mock_device_entries:
            mock_device_entries.return_value = [
                Mock(entity_id="light.living_room"),
                Mock(entity_id="sensor.temperature")
            ]
            
            entity_entry = entity_reg.async_get("light.living_room")
            related = await graph_service._find_device_relationships(entity_entry)
            
            assert len(related) == 1
            assert related[0][0] == "sensor.temperature"
            assert "device:" in related[0][1]
            
    async def test_find_area_relationships(self, graph_service, mock_registries):
        """Test area-based relationship detection."""
        entity_reg, _, _ = mock_registries
        
        # Mock area entities function
        with patch("homeassistant.helpers.entity_registry.async_entries_for_area") as mock_area_entries:
            mock_area_entries.return_value = [
                Mock(entity_id="light.living_room"),
                Mock(entity_id="sensor.temperature"),
                Mock(entity_id="switch.living_room")
            ]
            
            entity_entry = entity_reg.async_get("light.living_room")
            related = await graph_service._find_area_relationships(entity_entry, [])
            
            assert len(related) == 2
            entity_ids = [r[0] for r in related]
            assert "sensor.temperature" in entity_ids
            assert "switch.living_room" in entity_ids
            
    async def test_find_automation_relationships(self, graph_service):
        """Test automation-based relationship detection."""
        # Test entity referenced in automation action
        related = await graph_service._find_automation_relationships("light.living_room")
        
        assert len(related) == 1
        assert related[0][0] == "automation.morning_routine"
        assert "automation_action:" in related[0][1]
        
        # Test entity referenced in automation trigger
        related = await graph_service._find_automation_relationships("sensor.temperature")
        
        assert len(related) == 1
        assert related[0][0] == "automation.morning_routine"
        assert "automation_trigger:" in related[0][1]
        
    async def test_automation_referenced_entities(self, graph_service):
        """Test finding entities referenced by an automation."""
        related = await graph_service._find_automation_referenced_entities("automation.morning_routine")
        
        # Should find both trigger and action entities
        entity_ids = [r[0] for r in related]
        assert "sensor.temperature" in entity_ids
        assert "light.living_room" in entity_ids
        
        # Check relationship types
        trigger_rel = next(r for r in related if r[0] == "sensor.temperature")
        assert "triggers:" in trigger_rel[1]
        
        action_rel = next(r for r in related if r[0] == "light.living_room") 
        assert "controls:" in action_rel[1]
        
    async def test_entity_referenced_in_config(self, graph_service):
        """Test entity reference detection in automation config."""
        config = [
            {"entity_id": "light.living_room"},
            {"data": {"entity_id": ["switch.kitchen", "light.living_room"]}}
        ]
        
        assert graph_service._entity_referenced_in_config("light.living_room", config)
        assert graph_service._entity_referenced_in_config("switch.kitchen", config)
        assert not graph_service._entity_referenced_in_config("sensor.unknown", config)
        
    async def test_entity_referenced_in_templates(self, graph_service):
        """Test entity reference detection in templates."""
        attributes = {
            "value_template": "{{ states('sensor.temperature') | float > 20 }}",
            "other_attr": "some value"
        }
        
        assert graph_service._entity_referenced_in_templates("sensor.temperature", attributes)
        assert not graph_service._entity_referenced_in_templates("sensor.unknown", attributes)
        
    async def test_extract_entities_from_config(self, graph_service):
        """Test entity extraction from automation config."""
        config = [
            {"entity_id": "light.living_room"},
            {"entity_id": ["switch.kitchen", "light.bedroom"]},
            {"data": {"entity_id": "sensor.temperature"}},
            {"target": {"entity_id": ["light.hall", "switch.hall"]}}
        ]
        
        entities = graph_service._extract_entities_from_config(config)
        
        expected = {
            "light.living_room", "switch.kitchen", "light.bedroom", 
            "sensor.temperature", "light.hall", "switch.hall"
        }
        assert entities == expected
        
    async def test_get_entity_neighborhood_invalid(self, graph_service):
        """Test neighborhood retrieval for invalid entity."""
        with pytest.raises(ValueError, match="Entity nonexistent.entity not found"):
            await graph_service.get_entity_neighborhood("nonexistent.entity")
            
    async def test_passes_filters(self, graph_service):
        """Test filtering logic."""
        node = GraphNode(
            id="light.living_room",
            label="Living Room Light", 
            domain="light",
            area="Living Room",
            device_id="device_1",
            state="on"
        )
        
        # No filters - should pass
        assert graph_service._passes_filters(node)
        
        # Domain filter - should pass
        assert graph_service._passes_filters(node, domain_filter=["light", "switch"])
        
        # Domain filter - should fail
        assert not graph_service._passes_filters(node, domain_filter=["switch", "sensor"])
        
        # Area filter - should pass
        assert graph_service._passes_filters(node, area_filter=["Living Room", "Kitchen"])
        
        # Area filter - should fail
        assert not graph_service._passes_filters(node, area_filter=["Kitchen", "Bedroom"])


if __name__ == "__main__":
    pytest.main([__file__])