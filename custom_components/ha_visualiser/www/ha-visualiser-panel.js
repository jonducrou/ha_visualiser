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
    console.log('HA Visualiser Panel v0.3.2: Connected callback started - Fixed automation relationship symmetry');
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
    
    const nodes = graphData.nodes || [];
    const edges = graphData.edges || [];
    
    // Prepare vis.js data
    const visNodes = new vis.DataSet(nodes.map(node => {
      const isFocusNode = node.id === graphData.center_node;
      return {
        id: node.id,
        label: node.label,
        title: this.createNodeTooltip(node),
        shape: this.getNodeShape(node.domain),
        color: isFocusNode ? this.getFocusNodeColor(node.domain) : this.getNodeColor(node.domain),
        font: { 
          size: isFocusNode ? 14 : 12, 
          color: isFocusNode ? '#000' : '#333',
          bold: isFocusNode
        },
        borderWidth: isFocusNode ? 4 : 1,
        borderWidthSelected: 4,
        shadow: isFocusNode ? { enabled: true, size: 10, x: 0, y: 0 } : true
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

    const options = {
      layout: {
        improvedLayout: true,
        hierarchical: {
          direction: 'UD',        // Left to Right
          sortMethod: 'directed', // Respects edge directions
          levelSeparation: 150,   // Horizontal spacing between levels
          nodeSpacing: 100,       // Vertical spacing between nodes
          treeSpacing: 200        // Spacing between separate trees
        }
      },
      physics: {
        enabled: true,
        stabilization: { iterations: 100 },
        barnesHut: {
          gravitationalConstant: -2000,
          centralGravity: 0.3,
          springLength: 95,
          springConstant: 0.04,
          damping: 0.09
        }
      },
      interaction: {
        hover: true,
        tooltipDelay: 200,
        hideEdgesOnDrag: false,
        hideNodesOnDrag: false
      },
      nodes: {
        borderWidth: 1,
        shadow: true,
        font: { size: 12 }
      },
      edges: {
        width: 2,
        shadow: true,
        smooth: {
          type: 'continuous',
          roundness: 0.3
        }
      }
    };
    
    // Create or update the network
    if (this.network) {
      this.network.destroy();
    }
    
    this.network = new vis.Network(networkContainer, data, options);
    
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
    const shapes = {
      'light': 'dot',
      'switch': 'square',
      'sensor': 'triangle',
      'automation': 'star',
      'script': 'hexagon',
      'scene': 'diamond',
      'input_boolean': 'square',
      'input_number': 'box',
      'binary_sensor': 'triangle',
      'device_tracker': 'dot',
      'device': 'database',
      'area': 'box',
      'zone': 'circle'
    };
    return shapes[domain] || 'ellipse';
  }
  
  getNodeColor(domain) {
    const colors = {
      'light': '#FFA726',
      'switch': '#66BB6A',
      'sensor': '#42A5F5', 
      'automation': '#AB47BC',
      'script': '#EF5350',
      'scene': '#FFCA28',
      'input_boolean': '#26C6DA',
      'input_number': '#5C6BC0',
      'binary_sensor': '#78909C',
      'device_tracker': '#FF7043',
      'device': '#795548',
      'area': '#607D8B',
      'zone': '#00BCD4'
    };
    return colors[domain] || '#90A4AE';
  }
  
  getFocusNodeColor(domain) {
    // Brighter, more prominent colors for the focus node
    const focusColors = {
      'light': '#FF8F00',        // Bright orange
      'switch': '#4CAF50',       // Bright green
      'sensor': '#2196F3',       // Bright blue
      'automation': '#9C27B0',   // Bright purple
      'script': '#F44336',       // Bright red
      'scene': '#FFC107',        // Bright yellow
      'input_boolean': '#00BCD4', // Bright cyan
      'input_number': '#3F51B5',  // Bright indigo
      'binary_sensor': '#607D8B', // Blue grey
      'device_tracker': '#FF5722', // Deep orange
      'device': '#5D4037',       // Brown
      'area': '#455A64',         // Blue grey
      'zone': '#00ACC1'          // Cyan
    };
    return focusColors[domain] || '#546E7A';
  }
  
  getEdgeColor(relationshipType) {
    if (relationshipType === 'has_entity') return '#4CAF50';
    if (relationshipType === 'in_zone') return '#00BCD4';
    if (relationshipType.startsWith('belongs_to:')) return '#795548';
    if (relationshipType.startsWith('device:')) return '#4CAF50';
    if (relationshipType.startsWith('area:')) return '#607D8B';
    if (relationshipType.startsWith('automation')) return '#9C27B0';
    if (relationshipType.startsWith('template:')) return '#FF9800';
    if (relationshipType.startsWith('triggers:')) return '#E91E63';
    if (relationshipType.startsWith('controls:')) return '#3F51B5';
    return '#757575';
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