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

    async def get_filtered_neighborhood(
        self, 
        entity_id: str, 
        max_depth: int = 1,
        domain_filter: List[str] = None,
        area_filter: List[str] = None,
        relationship_filter: List[str] = None
    ) -> Dict[str, Any]:
        """Get filtered neighborhood graph for a specific entity."""
        if entity_id not in self.hass.states.async_entity_ids():
            raise ValueError(f"Entity {entity_id} not found")

        nodes = {}
        edges = []
        visited = set()
        filtered_count = 0
        
        # Start with the target entity
        await self._add_entity_and_neighbors_filtered(
            entity_id, nodes, edges, visited, max_depth,
            domain_filter, area_filter, relationship_filter, filtered_count
        )
        
        return {
            "nodes": list(nodes.values()),
            "edges": edges,
            "center_node": entity_id,
            "filtered_count": filtered_count
        }

    async def get_graph_statistics(self) -> Dict[str, Any]:
        """Get overall graph statistics."""
        entity_ids = self.hass.states.async_entity_ids()
        total_entities = len(entity_ids)
        
        # Count by domain
        domain_counts = {}
        area_counts = {}
        device_counts = {}
        
        for entity_id in entity_ids:
            domain = entity_id.split(".")[0]
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            entity_entry = self._entity_registry.async_get(entity_id)
            if entity_entry:
                # Count by area
                area_id = entity_entry.area_id
                if not area_id and entity_entry.device_id:
                    device = self._device_registry.async_get(entity_entry.device_id)
                    if device:
                        area_id = device.area_id
                
                if area_id:
                    area = self._area_registry.async_get_area(area_id)
                    area_name = area.name if area else "Unknown"
                    area_counts[area_name] = area_counts.get(area_name, 0) + 1
                
                # Count by device
                if entity_entry.device_id:
                    device = self._device_registry.async_get(entity_entry.device_id)
                    device_name = device.name_by_user or device.name if device else "Unknown"
                    device_counts[device_name] = device_counts.get(device_name, 0) + 1
        
        return {
            "total_entities": total_entities,
            "domain_counts": domain_counts,
            "area_counts": area_counts,
            "device_counts": device_counts,
            "total_areas": len(area_counts),
            "total_devices": len(device_counts),
            "total_domains": len(domain_counts)
        }

    async def _add_entity_and_neighbors_filtered(
        self, 
        entity_id: str, 
        nodes: Dict[str, GraphNode], 
        edges: List[GraphEdge], 
        visited: Set[str], 
        depth: int,
        domain_filter: List[str] = None,
        area_filter: List[str] = None, 
        relationship_filter: List[str] = None,
        filtered_count: int = 0
    ) -> int:
        """Recursively add entity and its neighbors with filtering."""
        if entity_id in visited or depth < 0:
            return filtered_count
            
        visited.add(entity_id)
        
        # Add the entity as a node if it passes filters
        node = await self._create_node(entity_id)
        if node and self._passes_filters(node, domain_filter, area_filter):
            nodes[entity_id] = node
            
            if depth > 0:
                # Find and add related entities
                related_entities = await self._find_related_entities(entity_id)
                
                for related_id, relationship_type in related_entities:
                    # Apply relationship filter
                    if relationship_filter and not any(
                        rel_filter in relationship_type for rel_filter in relationship_filter
                    ):
                        filtered_count += 1
                        continue
                        
                    if related_id not in visited:
                        # Check if related entity passes filters
                        related_node = await self._create_node(related_id)
                        if related_node and self._passes_filters(related_node, domain_filter, area_filter):
                            # Add edge
                            edges.append(GraphEdge(
                                from_node=entity_id,
                                to_node=related_id,
                                relationship_type=relationship_type,
                                label=relationship_type.replace("_", " ").title()
                            ))
                            
                            # Recursively add neighbor
                            filtered_count = await self._add_entity_and_neighbors_filtered(
                                related_id, nodes, edges, visited, depth - 1,
                                domain_filter, area_filter, relationship_filter, filtered_count
                            )
                        else:
                            filtered_count += 1
        else:
            filtered_count += 1
            
        return filtered_count

    def _passes_filters(
        self, 
        node: GraphNode, 
        domain_filter: List[str] = None, 
        area_filter: List[str] = None
    ) -> bool:
        """Check if a node passes the specified filters."""
        if domain_filter and node.domain not in domain_filter:
            return False
            
        if area_filter and node.area not in area_filter:
            return False
            
        return True

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
        
        # Device-based relationships
        device_related = await self._find_device_relationships(entity_entry)
        related.extend(device_related)
        
        # Area-based relationships (exclude entities already found via device)
        area_related = await self._find_area_relationships(entity_entry, device_related)
        related.extend(area_related)
        
        # Automation-based relationships
        automation_related = await self._find_automation_relationships(entity_id)
        related.extend(automation_related)
        
        # Template-based relationships
        template_related = await self._find_template_relationships(entity_id)
        related.extend(template_related)
        
        return related

    async def _find_device_relationships(self, entity_entry) -> List[tuple[str, str]]:
        """Find entities related through device membership."""
        related = []
        
        if not entity_entry.device_id:
            return related
            
        # Get all entities on the same device
        device_entities = entity_registry.async_entries_for_device(
            self._entity_registry, entity_entry.device_id
        )
        
        device = self._device_registry.async_get(entity_entry.device_id)
        device_name = device.name_by_user or device.name if device else "Unknown Device"
        
        for other_entity in device_entities:
            if other_entity.entity_id != entity_entry.entity_id:
                related.append((other_entity.entity_id, f"device:{device_name}"))
        
        return related

    async def _find_area_relationships(self, entity_entry, exclude_list: List[tuple[str, str]]) -> List[tuple[str, str]]:
        """Find entities related through area membership."""
        related = []
        excluded_entity_ids = {entity_id for entity_id, _ in exclude_list}
        
        # Determine the area for this entity
        area_id = entity_entry.area_id
        if not area_id and entity_entry.device_id:
            # Get area from device
            device = self._device_registry.async_get(entity_entry.device_id)
            if device:
                area_id = device.area_id
        
        if not area_id:
            return related
            
        area = self._area_registry.async_get_area(area_id)
        area_name = area.name if area else "Unknown Area"
        
        # Get all entities in the same area
        area_entities = entity_registry.async_entries_for_area(
            self._entity_registry, area_id
        )
        
        for other_entity in area_entities:
            if (other_entity.entity_id != entity_entry.entity_id and 
                other_entity.entity_id not in excluded_entity_ids):
                related.append((other_entity.entity_id, f"area:{area_name}"))
        
        return related

    async def _find_automation_relationships(self, entity_id: str) -> List[tuple[str, str]]:
        """Find entities related through automation triggers/actions."""
        related = []
        
        # If this IS an automation, find all entities it references
        if entity_id.startswith("automation."):
            automation_related = await self._find_automation_referenced_entities(entity_id)
            related.extend(automation_related)
        
        # Find automations that reference this entity
        automation_entities = [
            eid for eid in self.hass.states.async_entity_ids() 
            if eid.startswith("automation.")
        ]
        
        for automation_id in automation_entities:
            if automation_id == entity_id:  # Skip self
                continue
                
            state = self.hass.states.get(automation_id)
            if not state:
                continue
                
            # Check automation configuration for entity references
            automation_config = state.attributes.get("configuration", {})
            
            # Parse triggers for entity references
            triggers = automation_config.get("trigger", [])
            if not isinstance(triggers, list):
                triggers = [triggers] if triggers else []
                
            # Parse actions for entity references  
            actions = automation_config.get("action", [])
            if not isinstance(actions, list):
                actions = [actions] if actions else []
            
            # Check if our entity is referenced in triggers
            if self._entity_referenced_in_config(entity_id, triggers):
                automation_name = state.attributes.get("friendly_name", automation_id)
                related.append((automation_id, f"automation_trigger:{automation_name}"))
            # Check if our entity is referenced in actions  
            elif self._entity_referenced_in_config(entity_id, actions):
                automation_name = state.attributes.get("friendly_name", automation_id)
                related.append((automation_id, f"automation_action:{automation_name}"))
        
        return related

    async def _find_automation_referenced_entities(self, automation_id: str) -> List[tuple[str, str]]:
        """Find all entities referenced by a specific automation."""
        related = []
        
        state = self.hass.states.get(automation_id)
        if not state:
            return related
            
        automation_config = state.attributes.get("configuration", {})
        automation_name = state.attributes.get("friendly_name", automation_id)
        
        # Parse triggers for entity references
        triggers = automation_config.get("trigger", [])
        if not isinstance(triggers, list):
            triggers = [triggers] if triggers else []
            
        trigger_entities = self._extract_entities_from_config(triggers)
        for entity_id in trigger_entities:
            if entity_id != automation_id:  # Avoid self-reference
                related.append((entity_id, f"triggers:{automation_name}"))
        
        # Parse actions for entity references  
        actions = automation_config.get("action", [])
        if not isinstance(actions, list):
            actions = [actions] if actions else []
            
        action_entities = self._extract_entities_from_config(actions)
        for entity_id in action_entities:
            if entity_id != automation_id and (entity_id, f"triggers:{automation_name}") not in related:
                related.append((entity_id, f"controls:{automation_name}"))
        
        return related

    def _extract_entities_from_config(self, config_list: List[Dict[str, Any]]) -> Set[str]:
        """Extract all entity IDs from automation config."""
        entities = set()
        
        for config in config_list:
            if not isinstance(config, dict):
                continue
                
            # Check direct entity_id references
            entity_id = config.get("entity_id")
            if isinstance(entity_id, str):
                entities.add(entity_id)
            elif isinstance(entity_id, list):
                entities.update(entity_id)
                
            # Check in service data
            service_data = config.get("data", {})
            if isinstance(service_data, dict):
                data_entity_id = service_data.get("entity_id")
                if isinstance(data_entity_id, str):
                    entities.add(data_entity_id)
                elif isinstance(data_entity_id, list):
                    entities.update(data_entity_id)
                    
            # Check target entities (for newer HA automation format)
            target = config.get("target", {})
            if isinstance(target, dict):
                target_entity_id = target.get("entity_id")
                if isinstance(target_entity_id, str):
                    entities.add(target_entity_id)
                elif isinstance(target_entity_id, list):
                    entities.update(target_entity_id)
                    
            # Check device_id references and resolve to entities
            device_id = config.get("device_id")
            if device_id:
                device_entities = self._get_entities_for_device(device_id)
                entities.update(device_entities)
                
            # Check area_id references and resolve to entities  
            area_id = config.get("area_id")
            if area_id:
                area_entities = self._get_entities_for_area(area_id)
                entities.update(area_entities)
                
            # Recursively check nested configurations
            for value in config.values():
                if isinstance(value, list):
                    entities.update(self._extract_entities_from_config(value))
                elif isinstance(value, dict):
                    entities.update(self._extract_entities_from_config([value]))
        
        return entities

    def _get_entities_for_device(self, device_id: str) -> Set[str]:
        """Get all entity IDs for a given device."""
        try:
            from homeassistant.helpers import entity_registry
            device_entities = entity_registry.async_entries_for_device(
                self._entity_registry, device_id
            )
            return {entity.entity_id for entity in device_entities}
        except Exception:
            return set()

    def _get_entities_for_area(self, area_id: str) -> Set[str]:
        """Get all entity IDs for a given area."""
        try:
            from homeassistant.helpers import entity_registry
            area_entities = entity_registry.async_entries_for_area(
                self._entity_registry, area_id
            )
            return {entity.entity_id for entity in area_entities}
        except Exception:
            return set()

    async def _find_template_relationships(self, entity_id: str) -> List[tuple[str, str]]:
        """Find entities related through template references."""
        related = []
        
        # Get all template entities and input_* entities that might use templates
        template_domains = ["template", "input_boolean", "input_number", "input_text", "input_select"]
        
        for domain in template_domains:
            domain_entities = [
                eid for eid in self.hass.states.async_entity_ids() 
                if eid.startswith(f"{domain}.")
            ]
            
            for template_entity_id in domain_entities:
                state = self.hass.states.get(template_entity_id)
                if not state:
                    continue
                
                # Check if entity is referenced in template attributes
                if self._entity_referenced_in_templates(entity_id, state.attributes):
                    template_name = state.attributes.get("friendly_name", template_entity_id)
                    related.append((template_entity_id, f"template:{template_name}"))
        
        return related

    def _entity_referenced_in_config(self, entity_id: str, config_list: List[Dict[str, Any]]) -> bool:
        """Check if entity is referenced in automation config."""
        for config in config_list:
            if not isinstance(config, dict):
                continue
                
            # Check direct entity_id references
            if config.get("entity_id") == entity_id:
                return True
                
            # Check in lists of entity_ids
            entity_ids = config.get("entity_id", [])
            if isinstance(entity_ids, list) and entity_id in entity_ids:
                return True
                
            # Check in service data
            service_data = config.get("data", {})
            if isinstance(service_data, dict):
                if service_data.get("entity_id") == entity_id:
                    return True
                if isinstance(service_data.get("entity_id"), list) and entity_id in service_data.get("entity_id", []):
                    return True
                    
            # Recursively check nested configurations
            for value in config.values():
                if isinstance(value, list):
                    if self._entity_referenced_in_config(entity_id, value):
                        return True
                elif isinstance(value, dict):
                    if self._entity_referenced_in_config(entity_id, [value]):
                        return True
        
        return False

    def _entity_referenced_in_templates(self, entity_id: str, attributes: Dict[str, Any]) -> bool:
        """Check if entity is referenced in template attributes."""
        # Common template attributes that might reference entities
        template_attrs = [
            "state_template", "value_template", "icon_template", 
            "entity_picture_template", "availability_template"
        ]
        
        for attr in template_attrs:
            template_str = attributes.get(attr, "")
            if isinstance(template_str, str) and entity_id in template_str:
                return True
                
        # Check in any string attribute that looks like a template
        for key, value in attributes.items():
            if isinstance(value, str) and "{{" in value and entity_id in value:
                return True
                
        return False