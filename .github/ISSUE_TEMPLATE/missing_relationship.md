---
name: Missing Relationship
about: Report missing connections or relationships in the entity graph
title: '[Missing Relationship] '
labels: enhancement, relationship
assignees: ''
---

**Describe the missing relationship**
A clear description of what entities should be connected in the graph but aren't showing up.

**Entities involved**
- **Source Entity**: [e.g. light.living_room_main]
- **Target Entity**: [e.g. binary_sensor.living_room_motion] 
- **Expected Connection**: [e.g. automation turns light on when motion detected]

**Where the relationship exists**
Explain where this relationship is defined in Home Assistant:
- [ ] Automation
- [ ] Script  
- [ ] Template
- [ ] Device grouping
- [ ] Area assignment
- [ ] Scene
- [ ] Other: ___________

**Configuration example**
If possible, share the relevant automation/script/template configuration (remove sensitive info):
```yaml
# Your automation/script/template config here
```

**Current behavior**
What happens when you search for these entities in the visualizer?

**Environment (please complete the following information):**
 - Home Assistant Version: [e.g. 2025.9.0]
 - Integration Version: [e.g. 0.8.13]

**Additional context**
Any other details about why this relationship is important for your setup.