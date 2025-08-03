"""Graph service for analyzing Home Assistant entity relationships."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Set
from dataclasses import dataclass

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry, entity_registry, area_registry
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE

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
        self, entity_id: str, max_depth: int = 2
    ) -> Dict[str, Any]:
        """Get the neighborhood graph for a specific entity, device, area, or zone."""
        
        # Handle device nodes
        if entity_id.startswith("device:"):
            device_id = entity_id.replace("device:", "")
            device = self._device_registry.async_get(device_id)
            if not device:
                raise ValueError(f"Device {device_id} not found")
        # Handle area nodes
        elif entity_id.startswith("area:"):
            area_id = entity_id.replace("area:", "")
            area = self._area_registry.async_get_area(area_id)
            if not area:
                raise ValueError(f"Area {area_id} not found")
        # Handle zone nodes
        elif entity_id.startswith("zone."):
            zone_state = self.hass.states.get(entity_id)
            if not zone_state:
                raise ValueError(f"Zone {entity_id} not found")
        # Handle regular entities
        elif entity_id not in self.hass.states.async_entity_ids():
            raise ValueError(f"Entity {entity_id} not found")

        nodes = {}
        edges = []
        visited = set()
        edge_set = set()  # Track edges to prevent duplicates
        
        # Start with the target entity or device
        await self._add_entity_and_neighbors(
            entity_id, nodes, edges, visited, edge_set, max_depth
        )
        
        return {
            "nodes": list(nodes.values()),
            "edges": edges,
            "center_node": entity_id
        }

    async def search_entities(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for entities and devices matching the query."""
        query_lower = query.lower()
        results = []
        
        # Search entities
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
        
        # Search devices if we have room for more results
        if len(results) < limit:
            for device_id, device in self._device_registry.devices.items():
                device_name = device.name_by_user or device.name or "Unknown Device"
                
                if query_lower in device_name.lower():
                    results.append({
                        "entity_id": f"device:{device_id}",
                        "friendly_name": f"Device: {device_name}",
                        "domain": "device",
                        "state": "connected" if device.disabled_by is None else "disabled"
                    })
                    
                    if len(results) >= limit:
                        break
        
        # Search areas if we have room for more results  
        if len(results) < limit:
            for area_id, area in self._area_registry.areas.items():
                if query_lower in area.name.lower():
                    results.append({
                        "entity_id": f"area:{area_id}",
                        "friendly_name": f"Area: {area.name}",
                        "domain": "area", 
                        "state": "active"
                    })
                    
                    if len(results) >= limit:
                        break
        
        # Search zones if we have room for more results
        if len(results) < limit:
            zone_entities = [
                eid for eid in self.hass.states.async_entity_ids() 
                if eid.startswith("zone.")
            ]
            
            for zone_id in zone_entities:
                zone_state = self.hass.states.get(zone_id)
                if not zone_state:
                    continue
                    
                zone_name = zone_state.attributes.get("friendly_name", zone_id)
                
                if query_lower in zone_name.lower() or query_lower in zone_id.lower():
                    results.append({
                        "entity_id": zone_id,
                        "friendly_name": f"Zone: {zone_name}",
                        "domain": "zone",
                        "state": zone_state.state
                    })
                    
                    if len(results) >= limit:
                        break
        
        return results

    async def get_filtered_neighborhood(
        self, 
        entity_id: str, 
        max_depth: int = 2,
        domain_filter: List[str] = None,
        area_filter: List[str] = None,
        relationship_filter: List[str] = None
    ) -> Dict[str, Any]:
        """Get filtered neighborhood graph for a specific entity, device, area, or zone."""
        
        # Handle device nodes
        if entity_id.startswith("device:"):
            device_id = entity_id.replace("device:", "")
            device = self._device_registry.async_get(device_id)
            if not device:
                raise ValueError(f"Device {device_id} not found")
        # Handle area nodes
        elif entity_id.startswith("area:"):
            area_id = entity_id.replace("area:", "")
            area = self._area_registry.async_get_area(area_id)
            if not area:
                raise ValueError(f"Area {area_id} not found")
        # Handle zone nodes
        elif entity_id.startswith("zone."):
            zone_state = self.hass.states.get(entity_id)
            if not zone_state:
                raise ValueError(f"Zone {entity_id} not found")
        # Handle regular entities
        elif entity_id not in self.hass.states.async_entity_ids():
            raise ValueError(f"Entity {entity_id} not found")

        nodes = {}
        edges = []
        visited = set()
        edge_set = set()  # Track edges to prevent duplicates
        filtered_count = 0
        
        # Start with the target entity
        await self._add_entity_and_neighbors_filtered(
            entity_id, nodes, edges, visited, edge_set, max_depth,
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
        edge_set: Set[str],
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
                            # Use centralized edge creation for consistent directions
                            edge = self._create_symmetrical_edge(entity_id, related_id, relationship_type)
                            if edge:
                                # Create unique edge identifier for deduplication
                                edge_key = f"{edge.from_node}:{edge.to_node}:{edge.relationship_type}"
                                if edge_key not in edge_set:
                                    edges.append(edge)
                                    edge_set.add(edge_key)
                            
                            # Recursively add neighbor
                            filtered_count = await self._add_entity_and_neighbors_filtered(
                                related_id, nodes, edges, visited, edge_set, depth - 1,
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
            
        if area_filter and node.area and node.area not in area_filter:
            return False
            
        return True

    async def _add_entity_and_neighbors(
        self, 
        entity_id: str, 
        nodes: Dict[str, GraphNode], 
        edges: List[GraphEdge], 
        visited: Set[str], 
        edge_set: Set[str],
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
                        # Use centralized edge creation for consistent directions
                        edge = self._create_symmetrical_edge(entity_id, related_id, relationship_type)
                        if edge:
                            # Create unique edge identifier for deduplication
                            edge_key = f"{edge.from_node}:{edge.to_node}:{edge.relationship_type}"
                            if edge_key not in edge_set:
                                edges.append(edge)
                                edge_set.add(edge_key)
                        
                        # Recursively add neighbor
                        await self._add_entity_and_neighbors(
                            related_id, nodes, edges, visited, edge_set, depth - 1
                        )
    
    def _create_symmetrical_edge(self, node_a: str, node_b: str, relationship_type: str) -> GraphEdge | None:
        """Create a symmetrical edge with consistent direction regardless of discovery order.
        
        Edge directions are determined by node types and relationship semantics, not by which
        node was discovered first. This ensures symmetrical navigation.
        """
        
        
        # Determine canonical direction based on node types and relationship semantics
        # Priority hierarchy: area > device > entity > automation > zone
        
        def get_node_priority(node_id: str) -> int:
            """Get priority for canonical edge ordering."""
            if node_id.startswith("area:"):
                return 1  # Highest priority - areas contain everything
            elif node_id.startswith("device:"):
                return 2  # Devices contain entities
            elif node_id.startswith("zone."):
                return 3  # Zones contain entities
            elif node_id.startswith("automation."):
                return 4  # Automations have specific trigger/control semantics
            else:
                return 5  # Regular entities
        
        # Standard containment relationships - always container -> contained
        if relationship_type in ["has_entity", "device_has", "area_contains", "area_contains_device", 
                                "device_in_area", "zone_contains", "in_zone"]:
            
            priority_a = get_node_priority(node_a)
            priority_b = get_node_priority(node_b)
            
            # Container (lower priority number) -> Contained (higher priority number)
            if priority_a < priority_b:
                from_node, to_node = node_a, node_b
            else:
                from_node, to_node = node_b, node_a
                
            # Determine label based on container type
            if from_node.startswith("area:"):
                label = "contains"
            elif from_node.startswith("device:"):
                label = "has entity"
            elif from_node.startswith("zone."):
                label = "contains"
            else:
                label = "contains"
                
        # Automation relationships have specific semantics
        elif relationship_type == "automation_trigger":
            # Entity -> Automation (Entity triggers Automation)
            if node_a.startswith("automation."):
                from_node, to_node = node_b, node_a  # entity -> automation
            else:
                from_node, to_node = node_a, node_b  # entity -> automation
            label = "triggers"
            
        elif relationship_type == "automation_action":
            # Automation -> Entity (Automation controls Entity)
            if node_a.startswith("automation."):
                from_node, to_node = node_a, node_b  # automation -> entity
            else:
                from_node, to_node = node_b, node_a  # automation -> entity
            label = "controls"
            
        elif relationship_type.startswith("template:"):
            # Template -> Entity (Template uses Entity)
            # For now, assume template relationships point from template to entity
            from_node, to_node = node_a, node_b
            label = "uses"
            
        else:
            # Default: use node priority to determine direction
            priority_a = get_node_priority(node_a)
            priority_b = get_node_priority(node_b)
            
            if priority_a <= priority_b:
                from_node, to_node = node_a, node_b
            else:
                from_node, to_node = node_b, node_a
                
            label = relationship_type.replace("_", " ")
        
        return GraphEdge(
            from_node=from_node,
            to_node=to_node,
            relationship_type=relationship_type,
            label=label
        )

    async def _create_node(self, entity_id: str) -> GraphNode | None:
        """Create a graph node for an entity or device."""
        
        # Handle device nodes
        if entity_id.startswith("device:"):
            device_id = entity_id.replace("device:", "")
            device = self._device_registry.async_get(device_id)
            if not device:
                return None
                
            device_name = device.name_by_user or device.name or "Unknown Device"
            area_name = None
            
            # Get area name for device
            if device.area_id:
                area = self._area_registry.async_get_area(device.area_id)
                area_name = area.name if area else None
                
            return GraphNode(
                id=entity_id,
                label=device_name,
                domain="device",
                area=area_name,
                device_id=device_id,
                state="connected" if device.disabled_by is None else "disabled"
            )
        
        # Handle area nodes
        if entity_id.startswith("area:"):
            area_id = entity_id.replace("area:", "")
            area = self._area_registry.async_get_area(area_id)
            if not area:
                return None
                
            return GraphNode(
                id=entity_id,
                label=area.name,
                domain="area",
                area=area.name,
                device_id=None,
                state="active"
            )
        
        # Handle zone nodes
        if entity_id.startswith("zone."):
            zone_state = self.hass.states.get(entity_id)
            if not zone_state:
                return None
                
            zone_name = zone_state.attributes.get("friendly_name", entity_id)
            return GraphNode(
                id=entity_id,
                label=zone_name,
                domain="zone",
                area=None,
                device_id=None,
                state=zone_state.state
            )
        
        # Handle regular entity nodes
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
        
        # Handle device node relationships - show all entities on the device
        if entity_id.startswith("device:"):
            device_id = entity_id.replace("device:", "")
            _LOGGER.debug(f"Finding entities for device: {device_id}")
            
            from homeassistant.helpers import entity_registry
            device_entities = entity_registry.async_entries_for_device(
                self._entity_registry, device_id
            )
            
            _LOGGER.debug(f"Found {len(device_entities)} entities on device {device_id}")
            for entity_entry in device_entities:
                _LOGGER.debug(f"  Device entity: {entity_entry.entity_id}")
                # Device contains entity: return entity with device_has relationship
                related.append((entity_entry.entity_id, "device_has"))
            
            # Also find the area that contains this device
            device = self._device_registry.async_get(device_id)
            if device and device.area_id:
                area = self._area_registry.async_get_area(device.area_id)
                area_name = area.name if area else "Unknown Area"
                area_node_id = f"area:{device.area_id}"
                _LOGGER.debug(f"  Device is in area: {area_node_id}")
                # Area contains device: return area with device_in_area relationship
                related.append((area_node_id, "device_in_area"))
            
            return related
        
        # Handle area node relationships - show all entities in the area
        if entity_id.startswith("area:"):
            area_id = entity_id.replace("area:", "")
            _LOGGER.debug(f"Finding entities for area: {area_id}")
            
            from homeassistant.helpers import entity_registry
            
            # Find entities directly assigned to the area
            area_entities = entity_registry.async_entries_for_area(
                self._entity_registry, area_id
            )
            
            _LOGGER.debug(f"Found {len(area_entities)} entities directly in area {area_id}")
            for entity_entry in area_entities:
                _LOGGER.debug(f"  Direct area entity: {entity_entry.entity_id}")
                # Area contains entity: return entity with area_contains relationship
                related.append((entity_entry.entity_id, "area_contains"))
            
            # Also find entities on devices that are in this area
            devices_in_area = [
                device for device in self._device_registry.devices.values()
                if device.area_id == area_id
            ]
            
            _LOGGER.debug(f"Found {len(devices_in_area)} devices in area {area_id}")
            for device in devices_in_area:
                # Add the device itself as a node that the area contains
                device_node_id = f"device:{device.id}"
                _LOGGER.debug(f"  Area contains device: {device_node_id}")
                related.append((device_node_id, "area_contains_device"))
                
                # Also add entities on devices in this area (for completeness)
                device_entities = entity_registry.async_entries_for_device(
                    self._entity_registry, device.id
                )
                _LOGGER.debug(f"  Device {device.name or device.id} has {len(device_entities)} entities")
                for entity_entry in device_entities:
                    _LOGGER.debug(f"    Device entity: {entity_entry.entity_id}")
                    # Area contains entity (via device): return entity with area_contains relationship
                    related.append((entity_entry.entity_id, "area_contains"))
            
            return related
        
        # Handle zone node relationships - show all entities in the zone
        if entity_id.startswith("zone."):
            # Find all entities that have location and are in this zone
            zone_state = self.hass.states.get(entity_id)
            if not zone_state:
                return related
                
            zone_lat = zone_state.attributes.get(ATTR_LATITUDE)
            zone_lon = zone_state.attributes.get(ATTR_LONGITUDE)
            zone_radius = zone_state.attributes.get("radius", 100)
            
            if zone_lat is None or zone_lon is None:
                return related
                
            # Check all entities for location
            for test_entity_id in self.hass.states.async_entity_ids():
                test_state = self.hass.states.get(test_entity_id)
                if not test_state:
                    continue
                    
                entity_lat = test_state.attributes.get(ATTR_LATITUDE)
                entity_lon = test_state.attributes.get(ATTR_LONGITUDE)
                
                if entity_lat is not None and entity_lon is not None:
                    distance = self._calculate_distance(entity_lat, entity_lon, zone_lat, zone_lon)
                    if distance <= zone_radius:
                        # Zone contains entity: return entity with zone_contains relationship
                        related.append((test_entity_id, "zone_contains"))
            
            return related
        
        # Automation-based relationships (do this for ALL entities, including automations)
        automation_related = await self._find_automation_relationships(entity_id)
        related.extend(automation_related)
        
        # Handle regular entity relationships
        entity_entry = self._entity_registry.async_get(entity_id)
        
        if entity_entry:
            # Device-based relationships
            device_related = await self._find_device_relationships(entity_entry)
            related.extend(device_related)
            
            # Area-based relationships (exclude entities already found via device)
            area_related = await self._find_area_relationships(entity_entry, device_related)
            related.extend(area_related)
            
            # Zone-based relationships
            zone_related = await self._find_zone_relationships(entity_id)
            related.extend(zone_related)
            
            # Template-based relationships
            template_related = await self._find_template_relationships(entity_id)
            related.extend(template_related)
        
        return related

    async def _find_device_relationships(self, entity_entry) -> List[tuple[str, str]]:
        """Find device relationship - device has entity."""
        related = []
        
        if not entity_entry.device_id:
            return related
            
        # Add relationship to the device itself
        device = self._device_registry.async_get(entity_entry.device_id)
        device_name = device.name_by_user or device.name if device else "Unknown Device"
        device_node_id = f"device:{entity_entry.device_id}"
        
        # Create relationship: device -> entity with "has_entity" relationship
        # This will be reversed in the graph to show device -> entity
        related.append((device_node_id, "has_entity"))
        
        return related

    async def _find_area_relationships(self, entity_entry, exclude_list: List[tuple[str, str]]) -> List[tuple[str, str]]:
        """Find area relationship - area has entity."""
        related = []
        
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
        area_node_id = f"area:{area_id}"
        
        # Create relationship: area -> entity with "has_entity" relationship
        related.append((area_node_id, "has_entity"))
        
        return related

    async def _find_zone_relationships(self, entity_id: str) -> List[tuple[str, str]]:
        """Find zone relationships - entity in zone."""
        related = []
        
        # Get entity state to check for location
        state = self.hass.states.get(entity_id)
        if not state:
            return related
            
        # Check if entity has location attributes
        latitude = state.attributes.get(ATTR_LATITUDE)
        longitude = state.attributes.get(ATTR_LONGITUDE)
        
        # Debug logging
        if latitude is not None or longitude is not None:
            _LOGGER.debug(f"Entity {entity_id} has location: lat={latitude}, lon={longitude}")
        
        if latitude is None or longitude is None:
            return related
            
        # Check all zone entities to see if this entity is in any zones
        zone_entities = [
            eid for eid in self.hass.states.async_entity_ids() 
            if eid.startswith("zone.")
        ]
        
        _LOGGER.debug(f"Found {len(zone_entities)} zones to check: {zone_entities}")
        
        for zone_id in zone_entities:
            zone_state = self.hass.states.get(zone_id)
            if not zone_state:
                continue
                
            zone_lat = zone_state.attributes.get(ATTR_LATITUDE)
            zone_lon = zone_state.attributes.get(ATTR_LONGITUDE)
            zone_radius = zone_state.attributes.get("radius", 100)  # Default 100m radius
            
            if zone_lat is None or zone_lon is None:
                _LOGGER.debug(f"Zone {zone_id} missing coordinates: lat={zone_lat}, lon={zone_lon}")
                continue
                
            # Calculate distance (simple approximation)
            distance = self._calculate_distance(latitude, longitude, zone_lat, zone_lon)
            _LOGGER.debug(f"Entity {entity_id} distance from zone {zone_id}: {distance}m (radius: {zone_radius}m)")
            
            if distance <= zone_radius:
                _LOGGER.info(f"Entity {entity_id} is in zone {zone_id}")
                related.append((zone_id, "in_zone"))
                
        return related
    
    def _calculate_distance(self, entity_lat: float, entity_lon: float, 
                           zone_lat: float, zone_lon: float) -> float:
        """Calculate distance between two coordinates in meters."""
        import math
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [entity_lat, entity_lon, zone_lat, zone_lon])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance = 6371000 * c  # Earth radius in meters
        
        return distance
    
    def _is_in_zone(self, entity_lat: float, entity_lon: float, 
                    zone_lat: float, zone_lon: float, radius: float) -> bool:
        """Check if entity is in zone."""
        distance = self._calculate_distance(entity_lat, entity_lon, zone_lat, zone_lon)
        return distance <= radius

    async def _find_automation_relationships(self, entity_id: str) -> List[tuple[str, str]]:
        """Find entities related through automation triggers/actions."""
        related = []
        
        _LOGGER.debug(f"Finding automation relationships for: {entity_id}")
        
        # If this IS an automation, find all entities it references
        if entity_id.startswith("automation."):
            _LOGGER.debug(f"Entity is automation, finding referenced entities")
            automation_related = await self._find_automation_referenced_entities(entity_id)
            related.extend(automation_related)
            _LOGGER.debug(f"Found {len(automation_related)} automation-referenced entities: {automation_related}")
        
        # Find automations that reference this entity
        automation_entities = [
            eid for eid in self.hass.states.async_entity_ids() 
            if eid.startswith("automation.")
        ]
        
        _LOGGER.debug(f"Found {len(automation_entities)} total automations to check")
        
        for automation_id in automation_entities:
            if automation_id == entity_id:  # Skip self
                continue
                
            state = self.hass.states.get(automation_id)
            if not state:
                _LOGGER.debug(f"No state for automation: {automation_id}")
                continue
                
            # Check automation configuration for entity references
            automation_config = state.attributes.get("configuration", {})
            if not automation_config:
                _LOGGER.debug(f"No configuration for automation: {automation_id}")
                _LOGGER.debug(f"Available attributes: {list(state.attributes.keys())}")
                
                # Try to get automation config from automation registry/component
                try:
                    # Access automation component to get config
                    automation_component = self.hass.data.get("automation")
                    if automation_component:
                        _LOGGER.debug(f"Found automation component: {type(automation_component)}")
                        
                        # EntityComponent has entities accessible via get_entity()
                        automation_entity = automation_component.get_entity(automation_id)
                        if automation_entity:
                            _LOGGER.debug(f"Found automation entity: {type(automation_entity)}")
                            # Try different config attribute names
                            for config_attr in ["raw_config", "config", "_config", "_raw_config", "automation_config"]:
                                if hasattr(automation_entity, config_attr):
                                    config_value = getattr(automation_entity, config_attr)
                                    if config_value:
                                        automation_config = config_value
                                        _LOGGER.debug(f"Found config via {config_attr}: {type(automation_config)}")
                                        break
                        else:
                            _LOGGER.debug(f"No automation entity found for: {automation_id}")
                            
                        # Also try direct access to entities dict
                        if not automation_config and hasattr(automation_component, "entities"):
                            entities_dict = automation_component.entities
                            if automation_id in entities_dict:
                                automation_entity = entities_dict[automation_id]
                                _LOGGER.debug(f"Found automation in entities dict: {type(automation_entity)}")
                                for config_attr in ["raw_config", "config", "_config", "_raw_config"]:
                                    if hasattr(automation_entity, config_attr):
                                        config_value = getattr(automation_entity, config_attr)
                                        if config_value:
                                            automation_config = config_value
                                            _LOGGER.debug(f"Found config via entities.{config_attr}: {type(automation_config)}")
                                            break
                                
                    # Try alternative data sources
                    if not automation_config:
                        automation_configs = self.hass.data.get("automation_config")
                        if automation_configs and automation_id in automation_configs:
                            automation_config = automation_configs[automation_id]
                            _LOGGER.debug(f"Found config from automation_config data")
                            
                except Exception as e:
                    _LOGGER.debug(f"Error accessing automation component: {e}")
                        
                if not automation_config:
                    continue
                
            _LOGGER.debug(f"Checking automation {automation_id} for references to {entity_id}")
            
            # Parse triggers for entity references (try both 'triggers' and 'trigger')
            triggers = automation_config.get("triggers", automation_config.get("trigger", []))
            if not isinstance(triggers, list):
                triggers = [triggers] if triggers else []
                
            # Parse actions for entity references (try both 'actions' and 'action')
            actions = automation_config.get("actions", automation_config.get("action", []))
            if not isinstance(actions, list):
                actions = [actions] if actions else []
            
            _LOGGER.debug(f"  Triggers: {len(triggers)}, Actions: {len(actions)}")
            
            # Check if our entity is referenced in triggers
            if self._entity_referenced_in_config(entity_id, triggers):
                automation_name = state.attributes.get("friendly_name", automation_id)
                related.append((automation_id, "automation_trigger"))
                _LOGGER.debug(f"  Found trigger relationship: {automation_name}")
            # Check if our entity is referenced in actions  
            elif self._entity_referenced_in_config(entity_id, actions):
                automation_name = state.attributes.get("friendly_name", automation_id)
                related.append((automation_id, "automation_action"))
                _LOGGER.debug(f"  Found action relationship: {automation_name}")
        
        _LOGGER.debug(f"Total automation relationships found: {len(related)}")
        return related

    async def _find_automation_referenced_entities(self, automation_id: str) -> List[tuple[str, str]]:
        """Find all entities referenced by a specific automation."""
        related = []
        
        _LOGGER.debug(f"Finding entities referenced by automation: {automation_id}")
        
        state = self.hass.states.get(automation_id)
        if not state:
            _LOGGER.debug(f"No state found for automation: {automation_id}")
            return related
            
        automation_config = state.attributes.get("configuration", {})
        if not automation_config:
            _LOGGER.debug(f"No configuration found for automation: {automation_id}")
            _LOGGER.debug(f"Available attributes: {list(state.attributes.keys())}")
            
            # Try to get automation config from automation registry/component
            try:
                # Access automation component to get config
                automation_component = self.hass.data.get("automation")
                if automation_component:
                    _LOGGER.debug(f"Found automation component: {type(automation_component)}")
                    
                    # EntityComponent has entities accessible via get_entity()
                    automation_entity = automation_component.get_entity(automation_id)
                    if automation_entity:
                        _LOGGER.debug(f"Found automation entity: {type(automation_entity)}")
                        # Try different config attribute names
                        for config_attr in ["raw_config", "config", "_config", "_raw_config", "automation_config"]:
                            if hasattr(automation_entity, config_attr):
                                config_value = getattr(automation_entity, config_attr)
                                if config_value:
                                    automation_config = config_value
                                    _LOGGER.debug(f"Found config via {config_attr}: {type(automation_config)}")
                                    break
                    else:
                        _LOGGER.debug(f"No automation entity found for: {automation_id}")
                        
                    # Also try direct access to entities dict
                    if not automation_config and hasattr(automation_component, "entities"):
                        entities_dict = automation_component.entities
                        if automation_id in entities_dict:
                            automation_entity = entities_dict[automation_id]
                            _LOGGER.debug(f"Found automation in entities dict: {type(automation_entity)}")
                            for config_attr in ["raw_config", "config", "_config", "_raw_config"]:
                                if hasattr(automation_entity, config_attr):
                                    config_value = getattr(automation_entity, config_attr)
                                    if config_value:
                                        automation_config = config_value
                                        _LOGGER.debug(f"Found config via entities.{config_attr}: {type(automation_config)}")
                                        break
                            
                # Try alternative data sources
                if not automation_config:
                    automation_configs = self.hass.data.get("automation_config")
                    if automation_configs and automation_id in automation_configs:
                        automation_config = automation_configs[automation_id]
                        _LOGGER.debug(f"Found config from automation_config data")
                        
            except Exception as e:
                _LOGGER.debug(f"Error accessing automation component: {e}")
                    
            if not automation_config:
                _LOGGER.debug(f"No automation config found through any method")
                return related
            
        automation_name = state.attributes.get("friendly_name", automation_id)
        _LOGGER.debug(f"Automation name: {automation_name}")
        _LOGGER.debug(f"Raw automation config structure: {automation_config}")
        _LOGGER.debug(f"Config keys: {list(automation_config.keys()) if automation_config else 'No config'}")
        
        # Parse triggers for entity references (try both 'triggers' and 'trigger')
        triggers = automation_config.get("triggers", automation_config.get("trigger", []))
        if not isinstance(triggers, list):
            triggers = [triggers] if triggers else []
            
        _LOGGER.debug(f"Parsing {len(triggers)} triggers: {triggers}")
        trigger_entities = self._extract_entities_from_config(triggers)
        _LOGGER.debug(f"Found trigger entities: {trigger_entities}")
        
        for entity_id in trigger_entities:
            if entity_id != automation_id:  # Avoid self-reference
                related.append((entity_id, "automation_trigger"))
                _LOGGER.debug(f"Added trigger relationship: {entity_id} -> {automation_name}")
        
        # Parse actions for entity references (try both 'actions' and 'action')
        actions = automation_config.get("actions", automation_config.get("action", []))
        if not isinstance(actions, list):
            actions = [actions] if actions else []
            
        _LOGGER.debug(f"Parsing {len(actions)} actions: {actions}")
        action_entities = self._extract_entities_from_config(actions)
        _LOGGER.debug(f"Found action entities: {action_entities}")
        
        for entity_id in action_entities:
            if entity_id != automation_id and (entity_id, "automation_trigger") not in related:
                related.append((entity_id, "automation_action"))
                _LOGGER.debug(f"Added control relationship: {automation_name} -> {entity_id}")
        
        _LOGGER.debug(f"Total entities found for {automation_name}: {len(related)}")
        return related


    def _extract_entities_from_config(self, config_list: List[Dict[str, Any]]) -> Set[str]:
        """Extract all entity IDs from automation config."""
        entities = set()
        
        _LOGGER.debug(f"Extracting entities from config list: {config_list}")
        
        for config in config_list:
            if not isinstance(config, dict):
                _LOGGER.debug(f"Skipping non-dict config: {config}")
                continue
                
            _LOGGER.debug(f"Processing config item: {config}")
                
            # Check direct entity_id references
            entity_id = config.get("entity_id")
            if isinstance(entity_id, str):
                # Check if this is a UUID that needs to be resolved to actual entity_id
                resolved_entity_id = self._resolve_entity_uuid(entity_id)
                if resolved_entity_id:
                    entities.add(resolved_entity_id)
                else:
                    entities.add(entity_id)  # Add as-is if not a UUID
            elif isinstance(entity_id, list):
                for eid in entity_id:
                    resolved_entity_id = self._resolve_entity_uuid(eid)
                    if resolved_entity_id:
                        entities.add(resolved_entity_id)
                    else:
                        entities.add(eid)
                
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
                # If there's both device_id and entity_id, prioritize the specific entity
                specific_entity_id = config.get("entity_id")
                if specific_entity_id:
                    # Resolve UUID to actual entity ID if needed
                    resolved_entity_id = self._resolve_entity_uuid(specific_entity_id)
                    if resolved_entity_id:
                        entities.add(resolved_entity_id)
                        _LOGGER.debug(f"Found specific entity {resolved_entity_id} on device {device_id}")
                    else:
                        # UUID resolution failed, fall back to all device entities
                        device_entities = self._get_entities_for_device(device_id)
                        entities.update(device_entities)
                        _LOGGER.debug(f"Could not resolve entity UUID {specific_entity_id}, using all device entities: {device_entities}")
                else:
                    # No specific entity, use all device entities
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

    def _resolve_entity_uuid(self, uuid_or_entity_id: str) -> str | None:
        """Resolve entity UUID to actual entity ID, or return None if it's not a UUID."""
        # Entity UUIDs are typically 32-character hex strings without dots
        if len(uuid_or_entity_id) == 32 and all(c in '0123456789abcdef' for c in uuid_or_entity_id.lower()):
            # This looks like a UUID, try to resolve it
            try:
                # Look through entity registry to find entity with this UUID
                for entity_entry in self._entity_registry.entities.values():
                    if hasattr(entity_entry, 'id') and entity_entry.id == uuid_or_entity_id:
                        _LOGGER.debug(f"Resolved UUID {uuid_or_entity_id} to entity {entity_entry.entity_id}")
                        return entity_entry.entity_id
                    elif hasattr(entity_entry, 'unique_id') and entity_entry.unique_id == uuid_or_entity_id:
                        _LOGGER.debug(f"Resolved unique_id {uuid_or_entity_id} to entity {entity_entry.entity_id}")
                        return entity_entry.entity_id
                        
                _LOGGER.debug(f"Could not resolve UUID {uuid_or_entity_id} to any entity")
                return None
            except Exception as e:
                _LOGGER.debug(f"Error resolving UUID {uuid_or_entity_id}: {e}")
                return None
        
        # Not a UUID pattern, return as-is if it's a valid entity ID format
        if '.' in uuid_or_entity_id:
            return uuid_or_entity_id
        
        return None

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