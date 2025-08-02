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
    console.log('HA Visualiser Panel: Connected callback started');
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
    const graphContainer = this.querySelector('#graphContainer');
    graphContainer.innerHTML = '<div class="loading">Loading graph...</div>';
    
    try {
      const graphData = await this.hass.callWS({
        type: 'ha_visualiser/get_neighborhood',
        entity_id: entityId
      });
      
      this.renderGraph(graphData);
    } catch (error) {
      console.error('Failed to load graph:', error);
      graphContainer.innerHTML = `
        <div class="error">
          <div>
            <h3>Error Loading Graph</h3>
            <p>Failed to load entity relationships.<br/>
            Check the console for details.</p>
          </div>
        </div>
      `;
    }
  }

  renderGraph(graphData) {
    const graphContainer = this.querySelector('#graphContainer');
    graphContainer.innerHTML = '';
    
    // For now, show a simple representation
    // TODO: Integrate vis.js here
    const nodes = graphData.nodes || [];
    const edges = graphData.edges || [];
    
    graphContainer.innerHTML = `
      <div style="padding: 20px; height: 100%; overflow: auto;">
        <h3>Graph Data (Development View)</h3>
        <p><strong>Center Entity:</strong> ${graphData.center_node}</p>
        <p><strong>Nodes:</strong> ${nodes.length}</p>
        <p><strong>Edges:</strong> ${edges.length}</p>
        
        <h4>Entities:</h4>
        <ul>
          ${nodes.map(node => `
            <li>
              <strong>${node.label}</strong> (${node.id})
              <br/>Domain: ${node.domain}
              ${node.area ? '<br/>Area: ' + node.area : ''}
              ${node.state ? '<br/>State: ' + node.state : ''}
            </li>
          `).join('')}
        </ul>
        
        <h4>Relationships:</h4>
        <ul>
          ${edges.map(edge => `
            <li>${edge.from_node} → ${edge.to_node} (${edge.label})</li>
          `).join('')}
        </ul>
      </div>
    `;
  }

  set hass(hass) {
    this._hass = hass;
  }

  get hass() {
    return this._hass;
  }
}

customElements.define('ha-visualiser-panel', HaVisualiserPanel);