#!/usr/bin/env python3
"""Simple test runner script for the HA Visualiser integration."""

import asyncio
import sys
import os

# Add the custom_components directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

try:
    import pytest
    print("Running tests with pytest...")
    exit_code = pytest.main([
        'tests/',
        '-v',
        '--tb=short'
    ])
    sys.exit(exit_code)
except ImportError:
    print("pytest not available, running basic manual test...")
    
    # Manual test without pytest
    from unittest.mock import Mock, patch
    from custom_components.ha_visualiser.graph_service import GraphService, GraphNode
    
    async def manual_test():
        """Run a basic manual test of the graph service."""
        print("Testing GraphService manually...")
        
        # Create mock HA instance
        mock_hass = Mock()
        mock_hass.states = Mock()
        mock_hass.states.async_entity_ids.return_value = ["light.test", "switch.test"]
        mock_hass.states.get.return_value = Mock(
            entity_id="light.test",
            state="on",
            attributes={"friendly_name": "Test Light"}
        )
        
        # Mock registries
        with patch("homeassistant.helpers.entity_registry.async_get"), \
             patch("homeassistant.helpers.device_registry.async_get"), \
             patch("homeassistant.helpers.area_registry.async_get"):
            
            service = GraphService(mock_hass)
            
            # Test search
            results = await service.search_entities("test")
            print(f"Search results: {len(results)} entities found")
            
            # Test node creation
            node = await service._create_node("light.test")
            if node:
                print(f"Node created: {node.id} - {node.label}")
            else:
                print("Failed to create node")
                
            print("Manual test completed successfully!")
    
    # Run the manual test
    asyncio.run(manual_test())