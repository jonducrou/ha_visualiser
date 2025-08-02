"""Graph service for analyzing Home Assistant entity relationships."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Set
from dataclasses import dataclass

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry, entity_registry, area_registry

_LOGGER = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """Represents a node in the entity graph."""
    id: str
    label: str
    domain: str
    area: str | None
    device_id: str | None
    state: str | None


@dataclass
class GraphEdge:
    """Represents an edge in the entity graph."""
    from_node: str
    to_node: str
    relationship_type: str
    label: str


class GraphService:
    """Service for building and analyzing entity relationship graphs."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the graph service."""
        self.hass = hass
        self._entity_registry = entity_registry.async_get(hass)
        self._device_registry = device_registry.async_get(hass)
        self._area_registry = area_registry.async_get(hass)

    async def get_entity_neighborhood(
        self, entity_id: str, max_depth: int = 1
    ) -> Dict[str, Any]:
        """Get the neighborhood graph for a specific entity."""
        if entity_id not in self.hass.states.async_entity_ids():
            raise ValueError(f"Entity {entity_id} not found")

        nodes = {}
        edges = []
        visited = set()
        
        # Start with the target entity
        await self._add_entity_and_neighbors(
            entity_id, nodes, edges, visited, max_depth
        )
        
        return {
            "nodes": list(nodes.values()),
            "edges": edges,
            "center_node": entity_id
        }

    async def search_entities(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for entities matching the query."""
        query_lower = query.lower()
        results = []
        
        for entity_id in self.hass.states.async_entity_ids():
            state = self.hass.states.get(entity_id)
            if not state:
                continue
                
            # Search in entity_id and friendly_name
            friendly_name = state.attributes.get("friendly_name", entity_id)
            
            if (query_lower in entity_id.lower() or 
                query_lower in friendly_name.lower()):
                
                results.append({
                    "entity_id": entity_id,
                    "friendly_name": friendly_name,
                    "domain": entity_id.split(".")[0],
                    "state": state.state
                })
                
                if len(results) >= limit:
                    break
        
        return results

    async def _add_entity_and_neighbors(
        self, 
        entity_id: str, 
        nodes: Dict[str, GraphNode], 
        edges: List[GraphEdge], 
        visited: Set[str], 
        depth: int
    ) -> None:
        """Recursively add entity and its neighbors to the graph."""
        if entity_id in visited or depth < 0:
            return
            
        visited.add(entity_id)
        
        # Add the entity as a node
        node = await self._create_node(entity_id)
        if node:
            nodes[entity_id] = node
            
            if depth > 0:
                # Find and add related entities
                related_entities = await self._find_related_entities(entity_id)
                
                for related_id, relationship_type in related_entities:
                    if related_id not in visited:
                        # Add edge
                        edges.append(GraphEdge(
                            from_node=entity_id,
                            to_node=related_id,
                            relationship_type=relationship_type,
                            label=relationship_type.replace("_", " ").title()
                        ))
                        
                        # Recursively add neighbor
                        await self._add_entity_and_neighbors(
                            related_id, nodes, edges, visited, depth - 1
                        )

    async def _create_node(self, entity_id: str) -> GraphNode | None:
        """Create a graph node for an entity."""
        state = self.hass.states.get(entity_id)
        if not state:
            return None
            
        entity_entry = self._entity_registry.async_get(entity_id)
        area_name = None
        device_id = None
        
        if entity_entry:
            device_id = entity_entry.device_id
            area_id = entity_entry.area_id
            
            # Get area name
            if area_id:
                area = self._area_registry.async_get_area(area_id)
                area_name = area.name if area else None
            
            # If no direct area, try to get it from device
            elif device_id:
                device = self._device_registry.async_get(device_id)
                if device and device.area_id:
                    area = self._area_registry.async_get_area(device.area_id)
                    area_name = area.name if area else None
        
        return GraphNode(
            id=entity_id,
            label=state.attributes.get("friendly_name", entity_id),
            domain=entity_id.split(".")[0],
            area=area_name,
            device_id=device_id,
            state=state.state
        )

    async def _find_related_entities(self, entity_id: str) -> List[tuple[str, str]]:
        """Find entities related to the given entity."""
        related = []
        entity_entry = self._entity_registry.async_get(entity_id)
        
        if not entity_entry:
            return related
        
        # Find entities with same device
        if entity_entry.device_id:
            device_entities = entity_registry.async_entries_for_device(
                self._entity_registry, entity_entry.device_id
            )
            for other_entity in device_entities:
                if other_entity.entity_id != entity_id:
                    related.append((other_entity.entity_id, "device"))
        
        # Find entities in same area
        area_id = entity_entry.area_id
        if not area_id and entity_entry.device_id:
            # Get area from device
            device = self._device_registry.async_get(entity_entry.device_id)
            if device:
                area_id = device.area_id
        
        if area_id:
            area_entities = entity_registry.async_entries_for_area(
                self._entity_registry, area_id
            )
            for other_entity in area_entities:
                if (other_entity.entity_id != entity_id and 
                    (other_entity.entity_id, "device") not in related):
                    related.append((other_entity.entity_id, "area"))
        
        return related