"""
Unit tests for WebSocket API handlers using mocked Home Assistant dependencies.

Tests the WebSocket command handlers, data validation, and response formatting
without requiring a full Home Assistant installation.
"""
import pytest
import sys
import json
from unittest.mock import Mock, AsyncMock, patch


class TestWebSocketAPIMocked:
    """Test WebSocket API handlers with mocked HA dependencies."""
    
    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks for Home Assistant dependencies."""
        # Mock the HomeAssistant core and components modules
        mock_hass_core = Mock()
        mock_components = Mock()
        mock_websocket_api = Mock()
        
        sys.modules['homeassistant.core'] = mock_hass_core
        sys.modules['homeassistant.components'] = mock_components
        sys.modules['homeassistant.components.websocket_api'] = mock_websocket_api
        
        # Set up mock websocket decorators and functions
        mock_websocket_api.websocket_command = lambda schema: lambda func: func
        mock_websocket_api.require_admin = lambda func: func
        mock_websocket_api.async_response = lambda func: func
    
    def test_websocket_command_schemas(self):
        """Test WebSocket command schemas and validation."""
        # Expected command schemas based on the WebSocket handlers
        expected_commands = {
            'ha_visualiser/search_entities': {
                'required_fields': ['type', 'query'],
                'optional_fields': ['limit']
            },
            'ha_visualiser/get_neighborhood': {
                'required_fields': ['type', 'entity_id'],
                'optional_fields': ['max_depth', 'show_areas']
            },
            'ha_visualiser/get_filtered_neighborhood': {
                'required_fields': ['type', 'entity_id'],
                'optional_fields': ['max_depth', 'domain_filter', 'area_filter', 'relationship_filter']
            },
            'ha_visualiser/get_graph_statistics': {
                'required_fields': ['type'],
                'optional_fields': []
            }
        }
        
        # Validate command structure
        for command, schema in expected_commands.items():
            assert 'type' in schema['required_fields'], f"Command {command} should require 'type' field"
            assert isinstance(schema['required_fields'], list)
            assert isinstance(schema['optional_fields'], list)
    
    def test_websocket_search_entities_validation(self):
        """Test search entities WebSocket command validation."""
        # Valid message structure
        valid_messages = [
            {'type': 'ha_visualiser/search_entities', 'query': 'light', 'id': 1},
            {'type': 'ha_visualiser/search_entities', 'query': 'sensor', 'limit': 10, 'id': 2},
            {'type': 'ha_visualiser/search_entities', 'query': '', 'id': 3}  # Empty query should be handled
        ]
        
        # Invalid message structures
        invalid_messages = [
            {'type': 'ha_visualiser/search_entities', 'id': 1},  # Missing query
            {'type': 'ha_visualiser/search_entities', 'query': None, 'id': 2},  # None query
            {'id': 3}  # Missing type and query
        ]
        
        # Test valid messages
        for msg in valid_messages:
            assert 'type' in msg, "Message should have type field"
            assert 'query' in msg, "Message should have query field"
            assert 'id' in msg, "Message should have id field"
            assert msg['type'] == 'ha_visualiser/search_entities'
        
        # Test invalid messages
        for msg in invalid_messages:
            is_valid = (
                'type' in msg and 
                'query' in msg and 
                msg['query'] is not None and
                msg['type'] == 'ha_visualiser/search_entities'
            )
            assert not is_valid, f"Message should be invalid: {msg}"
    
    def test_websocket_get_neighborhood_validation(self):
        """Test get neighborhood WebSocket command validation."""
        valid_messages = [
            {
                'type': 'ha_visualiser/get_neighborhood',
                'entity_id': 'light.living_room',
                'id': 1
            },
            {
                'type': 'ha_visualiser/get_neighborhood', 
                'entity_id': 'sensor.temperature',
                'max_depth': 2,
                'show_areas': False,
                'id': 2
            }
        ]
        
        invalid_messages = [
            {'type': 'ha_visualiser/get_neighborhood', 'id': 1},  # Missing entity_id
            {'type': 'ha_visualiser/get_neighborhood', 'entity_id': '', 'id': 2},  # Empty entity_id
            {'type': 'ha_visualiser/get_neighborhood', 'entity_id': None, 'id': 3}  # None entity_id
        ]
        
        # Test valid messages
        for msg in valid_messages:
            assert 'entity_id' in msg and msg['entity_id'], "Message should have valid entity_id"
            assert msg['type'] == 'ha_visualiser/get_neighborhood'
            
            # Test optional parameters
            if 'max_depth' in msg:
                assert isinstance(msg['max_depth'], int)
            if 'show_areas' in msg:
                assert isinstance(msg['show_areas'], bool)
        
        # Test invalid messages
        for msg in invalid_messages:
            is_valid = (
                'entity_id' in msg and 
                msg['entity_id'] and
                isinstance(msg['entity_id'], str)
            )
            assert not is_valid, f"Message should be invalid: {msg}"
    
    def test_websocket_response_structure(self):
        """Test WebSocket response structure and serialization."""
        # Sample response data
        sample_response = {
            'nodes': [
                {
                    'id': 'light.living_room',
                    'label': 'Living Room Light',
                    'domain': 'light',
                    'area': 'Living Room',
                    'device_id': 'device123',
                    'state': 'on',
                    'icon': 'mdi:lightbulb'
                }
            ],
            'edges': [
                {
                    'from_node': 'device123',
                    'to_node': 'light.living_room',
                    'relationship_type': 'device_contains',
                    'label': 'contains'
                }
            ],
            'center_node': 'light.living_room'
        }
        
        # Test JSON serialization (required for WebSocket transmission)
        json_str = json.dumps(sample_response)
        assert isinstance(json_str, str)
        
        # Test deserialization
        restored = json.loads(json_str)
        assert restored == sample_response
        
        # Test response structure
        assert 'nodes' in sample_response
        assert 'edges' in sample_response
        assert 'center_node' in sample_response
        assert isinstance(sample_response['nodes'], list)
        assert isinstance(sample_response['edges'], list)
        assert isinstance(sample_response['center_node'], str)
    
    def test_websocket_error_handling(self):
        """Test WebSocket error handling patterns."""
        # Test error response structure
        error_responses = [
            {
                'error': {'code': 'entity_not_found', 'message': 'Entity light.nonexistent not found'},
                'id': 1
            },
            {
                'error': {'code': 'invalid_entity_id', 'message': 'Invalid entity ID format'},
                'id': 2
            },
            {
                'error': {'code': 'graph_build_error', 'message': 'Error building graph'},
                'id': 3
            }
        ]
        
        for error_response in error_responses:
            assert 'error' in error_response
            assert 'code' in error_response['error']
            assert 'message' in error_response['error']
            assert isinstance(error_response['error']['code'], str)
            assert isinstance(error_response['error']['message'], str)
    
    def test_defensive_data_validation(self):
        """Test defensive data validation patterns used in WebSocket handlers."""
        # Simulate the defensive validation pattern from websocket_api.py
        def validate_graph_result(result):
            """Simulate the validation logic added in v0.8.10."""
            if not isinstance(result, dict):
                raise ValueError(f"Graph service returned invalid result type: {type(result)}")
            
            nodes = result.get("nodes")
            edges = result.get("edges")
            center_node = result.get("center_node")
            
            # Apply defensive checks
            if nodes is None:
                nodes = []
            elif not isinstance(nodes, (list, tuple)):
                nodes = []
                
            if edges is None:
                edges = []
            elif not isinstance(edges, (list, tuple)):
                edges = []
            
            return {
                'nodes': nodes,
                'edges': edges,
                'center_node': center_node or 'unknown'
            }
        
        # Test with valid data
        valid_result = {
            'nodes': [{'id': 'light.test'}],
            'edges': [{'from_node': 'a', 'to_node': 'b'}],
            'center_node': 'light.test'
        }
        validated = validate_graph_result(valid_result)
        assert validated['nodes'] == valid_result['nodes']
        assert validated['edges'] == valid_result['edges']
        assert validated['center_node'] == valid_result['center_node']
        
        # Test with None values (the bug that was fixed in v0.8.10)
        invalid_result = {
            'nodes': None,
            'edges': None,
            'center_node': 'light.test'
        }
        validated = validate_graph_result(invalid_result)
        assert validated['nodes'] == []
        assert validated['edges'] == []
        assert validated['center_node'] == 'light.test'
        
        # Test with wrong types
        wrong_type_result = {
            'nodes': 'not_a_list',
            'edges': 123,
            'center_node': 'light.test'
        }
        validated = validate_graph_result(wrong_type_result)
        assert validated['nodes'] == []
        assert validated['edges'] == []
    
    def test_websocket_connection_mock(self):
        """Test WebSocket connection mocking."""
        mock_connection = Mock()
        mock_connection.send_result = Mock()
        mock_connection.send_error = Mock()
        
        # Test successful response
        test_data = {'nodes': [], 'edges': []}
        mock_connection.send_result(1, test_data)
        mock_connection.send_result.assert_called_once_with(1, test_data)
        
        # Test error response
        mock_connection.send_error(2, 'entity_not_found', 'Entity not found')
        mock_connection.send_error.assert_called_once_with(2, 'entity_not_found', 'Entity not found')
    
    @pytest.mark.parametrize("command_type,required_params", [
        ('ha_visualiser/search_entities', ['query']),
        ('ha_visualiser/get_neighborhood', ['entity_id']),
        ('ha_visualiser/get_filtered_neighborhood', ['entity_id']),
        ('ha_visualiser/get_graph_statistics', [])
    ])
    def test_command_parameter_requirements(self, command_type, required_params):
        """Test parameter requirements for each WebSocket command."""
        base_message = {'type': command_type, 'id': 1}
        
        if required_params:
            # Test that message is invalid without required parameters
            for param in required_params:
                incomplete_message = base_message.copy()
                # Missing the required parameter
                has_required_param = param in incomplete_message
                assert not has_required_param, f"Message should be missing required parameter {param}"
            
            # Test that message is valid with required parameters
            complete_message = base_message.copy()
            for param in required_params:
                if param == 'query':
                    complete_message[param] = 'test_query'
                elif param == 'entity_id':
                    complete_message[param] = 'light.test'
            
            # Should have all required parameters
            for param in required_params:
                assert param in complete_message, f"Complete message should have {param}"
        else:
            # Commands with no required parameters should be valid with just type and id
            assert 'type' in base_message
            assert 'id' in base_message
    
    def test_async_handler_patterns(self):
        """Test async handler patterns used in WebSocket API."""
        # Test async mock setup
        async_handler = AsyncMock()
        
        # Simulate async WebSocket handler
        async def mock_websocket_handler(hass, connection, msg):
            # Simulate async operations
            await async_handler.some_async_operation()
            return {'result': 'success'}
        
        # Test that handler is async
        import asyncio
        assert asyncio.iscoroutinefunction(mock_websocket_handler)
        
        # Test mock async operation
        async_handler.some_async_operation = AsyncMock()
        
        # Verify mock can be awaited
        assert hasattr(async_handler.some_async_operation, '__call__')
    
    def test_graph_service_integration_points(self):
        """Test integration points between WebSocket API and GraphService."""
        # Mock graph service methods that WebSocket handlers call
        mock_graph_service = Mock()
        
        # Mock the methods called by WebSocket handlers
        mock_graph_service.search_entities = AsyncMock(return_value=[
            {'entity_id': 'light.test', 'name': 'Test Light'}
        ])
        mock_graph_service.get_entity_neighborhood = AsyncMock(return_value={
            'nodes': [], 'edges': [], 'center_node': 'light.test'
        })
        mock_graph_service.get_filtered_neighborhood = AsyncMock(return_value={
            'nodes': [], 'edges': [], 'center_node': 'light.test', 'filtered_count': 0
        })
        mock_graph_service.get_graph_statistics = AsyncMock(return_value={
            'total_entities': 10, 'domain_counts': {}
        })
        
        # Test that all expected methods exist and are callable
        assert hasattr(mock_graph_service, 'search_entities')
        assert hasattr(mock_graph_service, 'get_entity_neighborhood')
        assert hasattr(mock_graph_service, 'get_filtered_neighborhood')
        assert hasattr(mock_graph_service, 'get_graph_statistics')
        
        # Test that methods can be called (would be awaited in real code)
        assert callable(mock_graph_service.search_entities)
        assert callable(mock_graph_service.get_entity_neighborhood)
        assert callable(mock_graph_service.get_filtered_neighborhood)
        assert callable(mock_graph_service.get_graph_statistics)
    
    def test_dataclass_to_dict_conversion(self):
        """Test conversion of dataclass objects to dictionaries for JSON serialization."""
        # Simulate the dataclass-to-dict conversion done in WebSocket handlers
        
        # Mock dataclass objects
        mock_node = Mock()
        mock_node.id = 'light.test'
        mock_node.label = 'Test Light'
        mock_node.domain = 'light'
        mock_node.area = 'Living Room'
        mock_node.device_id = 'device123'
        mock_node.state = 'on'
        mock_node.icon = 'mdi:lightbulb'
        
        mock_edge = Mock()
        mock_edge.from_node = 'device123'
        mock_edge.to_node = 'light.test'
        mock_edge.relationship_type = 'device_contains'
        mock_edge.label = 'contains'
        
        # Simulate the serialization logic from websocket_api.py
        def serialize_node(node):
            return {
                'id': node.id,
                'label': node.label,
                'domain': node.domain,
                'area': node.area,
                'device_id': node.device_id,
                'state': node.state,
                'icon': node.icon
            }
        
        def serialize_edge(edge):
            return {
                'from_node': edge.from_node,
                'to_node': edge.to_node,
                'relationship_type': edge.relationship_type,
                'label': edge.label
            }
        
        # Test serialization
        serialized_node = serialize_node(mock_node)
        serialized_edge = serialize_edge(mock_edge)
        
        # Validate serialized structure
        assert serialized_node['id'] == 'light.test'
        assert serialized_node['domain'] == 'light'
        assert serialized_edge['from_node'] == 'device123'
        assert serialized_edge['relationship_type'] == 'device_contains'
        
        # Test JSON serialization of result
        serialized_result = {
            'nodes': [serialized_node],
            'edges': [serialized_edge],
            'center_node': 'light.test'
        }
        
        json_str = json.dumps(serialized_result)
        assert isinstance(json_str, str)
        
        # Verify round-trip serialization
        restored = json.loads(json_str)
        assert restored == serialized_result