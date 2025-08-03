class HaVisualiserPanel extends HTMLElement {
  constructor() {
    super();
    this.hass = null;
    this.narrow = false;
    this.route = null;
    this.panel = null;
  }

  static get properties() {
    return {
      hass: { type: Object },
      narrow: { type: Boolean },
      route: { type: Object },
      panel: { type: Object },
    };
  }
 
  connectedCallback() {
    console.log('HA Visualiser Panel v0.5.0: Added label relationship support');
    console.log('HA Visualiser Panel: Loading enhanced vis.js version');
    
    // Load vis.js if not already loaded
    this.loadVisJS().then(() => {
      this.initializePanel();
    });
  }
  
  async loadVisJS() {
    return new Promise((resolve) => {
      if (window.vis) {
        resolve();
        return;
      }
      
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/vis-network@latest/dist/vis-network.min.js';
      script.onload = resolve;
      document.head.appendChild(script);
    });
  }
  
  initializePanel() {
    this.innerHTML = `
      <style>
        .container {
          padding: 16px;
          max-width: 1200px;
          margin: 0 auto;
        }
        
        .search-section {
          margin-bottom: 24px;
          padding: 16px;
          background: var(--card-background-color);
          border-radius: 8px;
          box-shadow: var(--ha-card-box-shadow);
        }
        
        .search-input {
          width: 100%;
          padding: 12px;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          font-size: 16px;
          background: var(--primary-background-color);
          color: var(--primary-text-color);
        }
        
        .search-results {
          margin-top: 12px;
          max-height: 200px;
          overflow-y: auto;
        }
        
        .search-result {
          padding: 8px 12px;
          border-bottom: 1px solid var(--divider-color);
          cursor: pointer;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .search-result:hover {
          background: var(--secondary-background-color);
        }
        
        .result-info {
          flex: 1;
        }
        
        .result-name {
          font-weight: 500;
          color: var(--primary-text-color);
        }
        
        .result-id {
          font-size: 12px;
          color: var(--secondary-text-color);
        }
        
        .result-state {
          font-size: 12px;
          color: var(--secondary-text-color);
          background: var(--secondary-background-color);
          padding: 2px 6px;
          border-radius: 3px;
        }
        
        .graph-section {
          background: var(--card-background-color);
          border-radius: 8px;
          box-shadow: var(--ha-card-box-shadow);
          height: 600px;
          position: relative;
        }
        
        .graph-container {
          width: 100%;
          height: 100%;
          border-radius: 8px;
          position: relative;
        }
        
        #visNetwork {
          width: 100%;
          height: 100%;
          border-radius: 8px;
        }
        
        .graph-controls {
          position: absolute;
          top: 16px;
          right: 16px;
          z-index: 100;
          display: flex;
          gap: 8px;
        }
        
        .control-button {
          padding: 8px 12px;
          background: var(--primary-color);
          color: var(--text-primary-color);
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
        }
        
        .control-button:hover {
          background: var(--primary-color-dark);
        }
        
        .graph-info {
          position: absolute;
          bottom: 16px;
          left: 16px;
          background: rgba(0, 0, 0, 0.7);
          color: white;
          padding: 8px 12px;
          border-radius: 4px;
          font-size: 12px;
          z-index: 100;
        }
        
        .loading {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: var(--secondary-text-color);
        }
        
        .no-selection {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: var(--secondary-text-color);
          text-align: center;
        }
        
        .error {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: var(--error-color);
          text-align: center;
        }
      </style>
      
      <div class="container">
        <div class="search-section">
          <input 
            type="text" 
            class="search-input" 
            placeholder="Search for entities..." 
            id="entitySearch"
          />
          <div class="search-results" id="searchResults" style="display: none;"></div>
        </div>
        
        <div class="graph-section">
          <div class="graph-container" id="graphContainer">
            <div id="visNetwork"></div>
            <div class="graph-controls">
              <button class="control-button" id="fitBtn">Fit</button>
              <button class="control-button" id="resetBtn">Reset</button>
            </div>
            <div class="graph-info" id="graphInfo">
              Select an entity to see its relationships
            </div>
          </div>
            <div class="no-selection">
              <div>
                <h3>Entity Visualizer</h3>
                <p>Search for an entity above to visualize its relationships</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    this.setupEventListeners();
  }

  setupEventListeners() {
    const searchInput = this.querySelector('#entitySearch');
    const searchResults = this.querySelector('#searchResults');
    
    let searchTimeout;
    
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      const query = e.target.value.trim();
      
      if (query.length < 2) {
        searchResults.style.display = 'none';
        return;
      }
      
      searchTimeout = setTimeout(() => {
        this.searchEntities(query);
      }, 300);
    });
    
    // Hide search results when clicking outside
    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
        searchResults.style.display = 'none';
      }
    });
  }

  async searchEntities(query) {
    console.log('HA Visualiser: Searching for entities with query:', query);
    try {
      console.log('HA Visualiser: Calling WebSocket API...');
      const results = await this.hass.callWS({
        type: 'ha_visualiser/search_entities',
        query: query,
        limit: 10
      });
      
      console.log('HA Visualiser: Search successful, results:', results);
      this.displaySearchResults(results);
    } catch (error) {
      console.error('HA Visualiser: Search failed, using fallback:', error);
      // For now, fall back to simple client-side search
      this.fallbackSearch(query);
    }
  }
  
  fallbackSearch(query) {
    const queryLower = query.toLowerCase();
    const results = [];
    
    Object.keys(this.hass.states).forEach(entityId => {
      const state = this.hass.states[entityId];
      const friendlyName = state.attributes.friendly_name || entityId;
      
      if (entityId.toLowerCase().includes(queryLower) || 
          friendlyName.toLowerCase().includes(queryLower)) {
        results.push({
          entity_id: entityId,
          friendly_name: friendlyName,
          domain: entityId.split('.')[0],
          state: state.state
        });
      }
      
      if (results.length >= 10) return;
    });
    
    this.displaySearchResults(results);
  }

  displaySearchResults(results) {
    const searchResults = this.querySelector('#searchResults');
    
    if (results.length === 0) {
      searchResults.style.display = 'none';
      return;
    }
    
    searchResults.innerHTML = results.map(result => `
      <div class="search-result" data-entity-id="${result.entity_id}">
        <div class="result-info">
          <div class="result-name">${result.friendly_name}</div>
          <div class="result-id">${result.entity_id}</div>
        </div>
        <div class="result-state">${result.state}</div>
      </div>
    `).join('');
    
    searchResults.style.display = 'block';
    
    // Add click handlers
    searchResults.querySelectorAll('.search-result').forEach(result => {
      result.addEventListener('click', () => {
        const entityId = result.dataset.entityId;
        this.selectEntity(entityId);
        searchResults.style.display = 'none';
      });
    });
  }

  async selectEntity(entityId) {
    const graphInfo = this.querySelector('#graphInfo');
    if (graphInfo) {
      graphInfo.textContent = 'Loading graph...';
    }
    
    // Clear the vis network but keep the container structure
    if (this.network) {
      this.network.setData({ nodes: new vis.DataSet(), edges: new vis.DataSet() });
    }
    
    try {
      const graphData = await this.hass.callWS({
        type: 'ha_visualiser/get_neighborhood',
        entity_id: entityId
      });
      
      this.renderGraph(graphData);
    } catch (error) {
      console.error('Failed to load graph:', error);
      
      // Show error in info panel instead of replacing entire container
      if (graphInfo) {
        graphInfo.innerHTML = `<span style="color: red;">Error: Failed to load entity relationships</span>`;
      }
      
      // Optionally show error overlay
      const networkContainer = this.querySelector('#visNetwork');
      if (networkContainer) {
        networkContainer.innerHTML = `
          <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666;">
            <div style="text-align: center;">
              <h3>Error Loading Graph</h3>
              <p>Failed to load entity relationships.<br/>Check the console for details.</p>
            </div>
          </div>
        `;
      }
    }
  }

  renderGraph(graphData) {
    console.log('HA Visualiser: Rendering graph with data:', graphData);
    
    if (!window.vis) {
      console.error('HA Visualiser: vis.js not loaded');
      this.showLoadingMessage();
      return;
    }
    
    // Detect if this is a complex graph that might benefit from force-directed layout
    const nodes = graphData.nodes || [];
    const edges = graphData.edges || [];
    const isComplexGraph = edges.length > nodes.length * 1.5; // High edge-to-node ratio
    
    console.log(`HA Visualiser: Graph analysis - ${nodes.length} nodes, ${edges.length} edges, ratio: ${(edges.length / nodes.length).toFixed(2)}, using ${isComplexGraph ? 'force-directed' : 'hierarchical'} layout`);
    
    const networkContainer = this.querySelector('#visNetwork');
    const graphInfo = this.querySelector('#graphInfo');
    
    if (!networkContainer) {
      console.error('HA Visualiser: Network container not found. Available containers:', 
        Array.from(this.querySelectorAll('div')).map(div => div.id || div.className));
      
      // Try to recreate the structure
      this.ensureGraphStructure();
      
      // Try again
      const retryContainer = this.querySelector('#visNetwork');
      if (!retryContainer) {
        console.error('HA Visualiser: Failed to create network container');
        return;
      }
    }
    
    // Prepare vis.js data (nodes and edges already declared above)
    const visNodes = new vis.DataSet(nodes.map(node => {
      const isFocusNode = node.id === graphData.center_node;
      const icon = this.getEntityIcon(node.domain);
      const backgroundColor = isFocusNode ? this.getFocusNodeColor(node.domain) : this.getNodeColor(node.domain);
      
      return {
        id: node.id,
        label: `${icon} | ${node.label}`,
        title: this.createNodeTooltip(node),
        shape: this.getNodeShape(node.domain),
        color: {
          background: backgroundColor,
          border: isFocusNode ? '#999' : '#D0D0D0',
          highlight: {
            background: backgroundColor,
            border: '#999'
          }
        },
        font: { 
          size: isFocusNode ? 14 : 12, 
          color: '#333',
          bold: isFocusNode
        },
        borderWidth: isFocusNode ? 3 : 1,
        shadow: false,
        margin: 8
      };
    }));
    
    const visEdges = new vis.DataSet(edges.map(edge => ({
      from: edge.from_node,
      to: edge.to_node,
      label: edge.label,
      title: `${edge.relationship_type}: ${edge.label}`,
      arrows: 'to',
      color: this.getEdgeColor(edge.relationship_type),
      width: 2
    })));
    
    const data = { nodes: visNodes, edges: visEdges };

    // Choose layout algorithm based on graph complexity
    const layoutOptions = isComplexGraph ? {
      // Force-directed layout for complex graphs
      improvedLayout: true,
      randomSeed: 42
    } : {
      // Hierarchical layout for simpler graphs
      improvedLayout: true,
      hierarchical: {
        enabled: true,
        direction: 'UD',
        sortMethod: 'directed',
        shakeTowards: 'leaves',        // Helps with edge crossing reduction
        edgeMinimization: true,
        blockShifting: true,
        parentCentralization: true,
        levelSeparation: 180,          // Increased for better clarity
        nodeSpacing: 120,              // Increased spacing
        treeSpacing: 250               // More space between trees
      },
      randomSeed: 42                   // Consistent layouts
    };

    const options = {
      layout: layoutOptions,
      physics: {
        enabled: true,
        solver: 'barnesHut',
        stabilization: { 
          iterations: 1000,              // More iterations for better stabilization
          updateInterval: 100,
          onlyDynamicEdges: false,
          fit: true
        },
        barnesHut: {
          gravitationalConstant: -3000,  // Stronger repulsion
          centralGravity: 0.2,           // Reduced central gravity
          springLength: 150,             // Longer springs for less crowding
          springConstant: 0.05,
          damping: 0.15,                 // More damping for stability
          avoidOverlap: 0.5              // Prevent node overlap
        },
        maxVelocity: 30,                 // Slower movement for stability
        minVelocity: 0.75                // Higher minimum for quicker settling
      },
      interaction: {
        hover: true,
        tooltipDelay: 200,
        hideEdgesOnDrag: false,
        hideNodesOnDrag: false
      },
      nodes: {
        borderWidth: 1,
        shadow: false,
        font: { 
          size: 12,
          color: '#333'
        },
        shape: 'box',
        margin: 8,
        color: {
          border: '#D0D0D0'
        },
        chosen: {
          node: function(values, id, selected, hovering) {
            values.borderColor = '#999';
            values.borderWidth = 2;
          }
        }
      },
      edges: {
        width: 1.5,
        shadow: false,
        smooth: {
          type: 'cubicBezier',           // Better curve algorithm
          roundness: 0.6,                // More pronounced curves
          forceDirection: 'vertical'     // Help with hierarchical layout
        },
        color: {
          color: '#D0D0D0',
          highlight: '#999',
          hover: '#999'
        },
        arrows: {
          to: {
            enabled: true,
            scaleFactor: 0.8,
            type: 'arrow'
          }
        },
        length: 200                      // Preferred edge length
      }
    };
    
    // Create or update the network
    if (this.network) {
      this.network.destroy();
    }
    
    this.network = new vis.Network(networkContainer, data, options);
    
    // Optimize layout after stabilization
    this.network.on('stabilizationIterationsDone', () => {
      console.log('HA Visualiser: Layout stabilized, disabling physics for performance');
      this.network.setOptions({
        physics: { enabled: false }
      });
    });
    
    // Add event listeners
    this.network.on('click', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        this.onNodeClick(nodeId);
      }
    });
    
    this.network.on('hoverNode', (params) => {
      const node = nodes.find(n => n.id === params.node);
      if (node) {
        graphInfo.textContent = `${node.label} (${node.domain})${node.area ? ' - ' + node.area : ''}`;
      }
    });
    
    this.network.on('blurNode', () => {
      graphInfo.textContent = `${nodes.length} entities, ${edges.length} relationships`;
    });
    
    // Setup control buttons
    this.setupGraphControls();
    
    // Update info
    graphInfo.textContent = `${nodes.length} entities, ${edges.length} relationships`;
    
    console.log('HA Visualiser: Graph rendered successfully');
  }
  
  showLoadingMessage() {
    const graphContainer = this.querySelector('#graphContainer');
    if (graphContainer) {
      graphContainer.innerHTML = `
        <div class="loading">
          <div>Loading vis.js library...</div>
        </div>
      `;
    }
  }
  
  ensureGraphStructure() {
    console.log('HA Visualiser: Ensuring graph structure exists');
    const graphContainer = this.querySelector('#graphContainer');
    
    if (graphContainer && !this.querySelector('#visNetwork')) {
      console.log('HA Visualiser: Recreating graph structure');
      graphContainer.innerHTML = `
        <div id="visNetwork"></div>
        <div class="graph-controls">
          <button class="control-button" id="fitBtn">Fit</button>
          <button class="control-button" id="resetBtn">Reset</button>
        </div>
        <div class="graph-info" id="graphInfo">
          Select an entity to see its relationships
        </div>
      `;
      
      // Re-setup control buttons
      this.setupGraphControls();
    }
  }
  
  createNodeTooltip(node) {
    let tooltip = `<strong>${node.label}</strong><br/>`;
    
    if (node.domain === 'device') {
      tooltip += `Type: Device<br/>`;
      tooltip += `ID: ${node.device_id}<br/>`;
      if (node.area) tooltip += `Area: ${node.area}<br/>`;
      tooltip += `Status: ${node.state}<br/>`;
      tooltip += `Click to see entities`;
    } else if (node.domain === 'label') {
      tooltip += `Type: Label<br/>`;
      tooltip += `ID: ${node.id}<br/>`;
      tooltip += `Usage: ${node.state}<br/>`;
      tooltip += `Click to see labelled items`;
    } else {
      tooltip += `ID: ${node.id}<br/>`;
      tooltip += `Domain: ${node.domain}<br/>`;
      if (node.area) tooltip += `Area: ${node.area}<br/>`;
      if (node.state) tooltip += `State: ${node.state}<br/>`;
      if (node.device_id) tooltip += `Device: ${node.device_id}`;
    }
    
    return tooltip;
  }
  
  getNodeShape(domain) {
    // Use consistent rounded box shape for all nodes
    return 'box';
  }
  
  getNodeColor(domain) {
    // Light, subtle color palette
    const colors = {
      'light': '#F5F5F5',        // Light grey
      'switch': '#F0F4F8',       // Very light blue
      'sensor': '#F7F9FC',       // Very light blue-grey
      'automation': '#FDF4FF',   // Very light purple
      'script': '#FFF5F5',       // Very light red
      'scene': '#FFFDF0',        // Very light yellow
      'input_boolean': '#F0FDFF', // Very light cyan
      'input_number': '#F5F3FF',  // Very light indigo
      'binary_sensor': '#F8F9FA', // Light grey
      'device_tracker': '#FFF8F0', // Very light orange
      'device': '#F6F6F6',       // Light grey
      'area': '#F0F8F0',         // Very light green
      'zone': '#F0FDFD',         // Very light teal
      'label': '#FFF8DC',        // Very light yellow (cornsilk)
      'media_player': '#FFF0F8',  // Very light pink
      'number': '#F8F5FF',       // Very light violet
      'todo': '#F5FFF0'          // Very light lime
    };
    return colors[domain] || '#F8F9FA';
  }
  
  getFocusNodeColor(domain) {
    // Slightly more prominent but still subtle colors for the focus node
    const focusColors = {
      'light': '#E8E8E8',        // Slightly darker grey
      'switch': '#E1EBF0',       // Slightly darker light blue
      'sensor': '#EDF2F7',       // Slightly darker blue-grey
      'automation': '#F4E6FF',   // Slightly darker light purple
      'script': '#FFE8E8',       // Slightly darker light red
      'scene': '#FFF8E1',        // Slightly darker light yellow
      'input_boolean': '#E1F8FF', // Slightly darker light cyan
      'input_number': '#E8E1FF',  // Slightly darker light indigo
      'binary_sensor': '#F0F1F2', // Slightly darker grey
      'device_tracker': '#FFE8D6', // Slightly darker light orange
      'device': '#E8E8E8',       // Slightly darker grey
      'area': '#E1F0E1',         // Slightly darker light green
      'zone': '#E1F8F8',         // Slightly darker light teal
      'label': '#FFF0B8',        // Slightly darker light yellow
      'media_player': '#FFE1F0',  // Slightly darker light pink
      'number': '#F0E8FF',       // Slightly darker light violet
      'todo': '#E8FFE1'          // Slightly darker light lime
    };
    return focusColors[domain] || '#F0F1F2';
  }
  
  getEntityIcon(domain) {
    // Map Home Assistant domains to simple text icons
    const icons = {
      'light': '💡',
      'switch': '🔌',
      'sensor': '📊',
      'automation': '🤖',
      'script': '📝',
      'scene': '🎬',
      'input_boolean': '☑️',
      'input_number': '🔢',
      'binary_sensor': '📡',
      'device_tracker': '📍',
      'device': '📱',
      'area': '🏠',
      'zone': '📍',
      'label': '🏷️',
      'media_player': '🔊',
      'number': '🔢',
      'todo': '✅',
      'climate': '🌡️',
      'cover': '🪟',
      'fan': '💨',
      'vacuum': '🧹',
      'camera': '📷',
      'lock': '🔒',
      'alarm_control_panel': '🚨',
      'weather': '🌤️',
      'sun': '☀️',
      'person': '👤',
      'button': '🔘',
      'select': '📋',
      'input_select': '📋',
      'input_text': '📝',
      'input_datetime': '📅',
      'timer': '⏲️',
      'counter': '🔢',
      'remote': '📱',
      'water_heater': '🚿',
      'humidifier': '💧',
      'siren': '🚨',
      'update': '🔄',
      'calendar': '📅'
    };
    return icons[domain] || '⚫';
  }
  
  getEdgeColor(relationshipType) {
    // Simple, subtle edge colors
    if (relationshipType.includes('automation') || relationshipType.includes('trigger') || relationshipType.includes('control')) {
      return '#B0B0B0';  // Light grey for automation relationships
    }
    if (relationshipType.includes('area') || relationshipType.includes('contains') || relationshipType.includes('device')) {
      return '#C0C0C0';  // Slightly lighter grey for containment relationships
    }
    return '#D0D0D0';    // Very light grey for other relationships
  }
  
  setupGraphControls() {
    const fitBtn = this.querySelector('#fitBtn');
    const resetBtn = this.querySelector('#resetBtn');
    
    if (fitBtn) {
      fitBtn.addEventListener('click', () => {
        if (this.network) {
          this.network.fit();
        }
      });
    }
    
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        if (this.network) {
          this.network.setData({ nodes: new vis.DataSet(), edges: new vis.DataSet() });
          const graphInfo = this.querySelector('#graphInfo');
          if (graphInfo) {
            graphInfo.textContent = 'Select an entity to see its relationships';
          }
        }
      });
    }
  }
  
  onNodeClick(nodeId) {
    console.log('HA Visualiser: Node clicked:', nodeId);
    // Navigate to the clicked entity's neighborhood
    this.selectEntity(nodeId);
  }

  set hass(hass) {
    this._hass = hass;
  }

  get hass() {
    return this._hass;
  }
}

customElements.define('ha-visualiser-panel', HaVisualiserPanel);