/**
 * ArthRakshak — Frontend API Client (api.js)
 * ============================================
 * Connects every HTML page to the Flask backend at localhost:5050.
 * If the backend is offline, silently falls back to local data.js data.
 *
 * LOAD ORDER in every HTML page (after data.js / script.js):
 *   <script src="data.js"></script>   ← already there
 *   <script src="api.js"></script>    ← ADD THIS
 *
 * USAGE EXAMPLES:
 *   AR.getStats()            → { total_schemes, avg_utilization, avg_risk, … }
 *   AR.getRisk()             → { schemes: [{score, level, key_factor, …}], … }
 *   AR.getAnomalies()        → { anomalies: [{id, severity, amount_cr, …}], … }
 *   AR.chat("high risk?")    → { text, intent }
 *   AR.getMap()              → { geojson, center, overview_url }
 *   AR.simulate({…})         → { projected, deltas, insights }
 *   AR.schemeMapsUrl(s)      → "https://maps.google.com/…"
 *   AR.openMaps(s)           → opens Google Maps in new tab
 *   AR.renderStatusBadge('id') → shows green/red API status pill
 */

const AR = (() => {

    // ── Configuration ─────────────────────────────────────────────────
    const BASE = 'http://localhost:5050/api';
    let _alive = null;   // null=unknown, true/false after first ping
  
    // ── Internal fetch helpers ────────────────────────────────────────
    async function _ping() {
      if (_alive !== null) return _alive;
      try {
        const r = await fetch(BASE + '/health', { signal: AbortSignal.timeout(1800) });
        _alive = r.ok;
      } catch { _alive = false; }
      if (!_alive) console.warn('[AR API] Backend offline → using local data fallback');
      return _alive;
    }
  
    async function _get(path, params = {}) {
      if (!await _ping()) return null;
      const url = new URL(BASE + path);
      Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
      try {
        const r = await fetch(url.toString());
        const j = await r.json();
        return j.success ? j.data : null;
      } catch { return null; }
    }
  
    async function _post(path, body = {}) {
      if (!await _ping()) return null;
      try {
        const r = await fetch(BASE + path, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        const j = await r.json();
        return j.success ? j.data : null;
      } catch { return null; }
    }
  
    // ── User helpers ──────────────────────────────────────────────────
    function _user() {
      try { return JSON.parse(sessionStorage.getItem('ar_user')); } catch { return null; }
    }
    function _dept() { return (_user() || {}).dept || 'Finance Ministry'; }
    function _localSchemes() {
      const u = _user();
      return (u && typeof getSchemes === 'function') ? getSchemes(u) : [];
    }
  
    // ══════════════════════════════════════════════════════════════════
    //  DATA API METHODS
    // ══════════════════════════════════════════════════════════════════
  
    /** Dashboard stats — tries backend first, falls back to local compute */
    async function getStats() {
      const d = await _get('/stats', { dept: _dept() });
      if (d) return d;
      const sc = _localSchemes();
      if (!sc.length) return {};
      const avg = a => Math.round(a.reduce((s, v) => s + v, 0) / a.length);
      const secs = {};
      sc.forEach(s => { secs[s.sector] = (secs[s.sector] || 0) + 1; });
      return {
        total_schemes:   sc.length,
        avg_utilization: avg(sc.map(s => s.utilization || 0)),
        avg_risk:        avg(sc.map(s => s.riskScore || 0)),
        high_risk_count: sc.filter(s => (s.riskScore || 0) >= 55).length,
        low_util_count:  sc.filter(s => (s.utilization || 0) < 30).length,
        sector_dist:     secs,
        dept:            _dept(),
        source:          'local',
      };
    }
  
    /** Risk scores — backend gives full AI scoring; fallback uses riskScore from data.js */
    async function getRisk() {
      const d = await _get('/risk', { dept: _dept() });
      if (d) return d;
      const sc = _localSchemes();
      const scored = sc.map(s => ({
        scheme_id:      s.id,
        scheme_name:    s.name,
        sector:         s.sector,
        score:          s.riskScore || 0,
        level:          (s.riskScore || 0) < 30 ? 'low' : (s.riskScore || 0) < 55 ? 'med' : (s.riskScore || 0) < 75 ? 'high' : 'crit',
        key_factor:     (s.riskScore || 0) >= 55 ? 'Elevated risk pattern' : 'Within normal parameters',
        recommendation: (s.riskScore || 0) < 30 ? '✅ Routine Monitor' :
                        (s.riskScore || 0) < 55 ? '📋 Quarterly Audit' :
                        (s.riskScore || 0) < 75 ? '🔍 Investigate Now' : '🚨 Freeze & Escalate',
      })).sort((a, b) => b.score - a.score);
      const dist = { low: 0, med: 0, high: 0, crit: 0 };
      scored.forEach(s => { dist[s.level] = (dist[s.level] || 0) + 1; });
      return {
        total_schemes: sc.length,
        average_score: scored.length ? Math.round(scored.reduce((a, s) => a + s.score, 0) / scored.length) : 0,
        distribution:  dist,
        schemes:       scored,
        source:        'local',
      };
    }
  
    /** Anomaly detection — backend has full ML engine; fallback generates from riskScore */
    async function getAnomalies() {
      const d = await _get('/anomalies', { dept: _dept() });
      if (d) return d;
      const sc = _localSchemes();
      const TYPES    = ['Overpayment','Ghost Beneficiary','Underutilization','Duplicate Entry','Disbursement Delay','Unauthorized Transfer'];
      const STATUSES = ['Under Investigation','Flagged','Resolved','Escalated to CAG'];
      const list = [];
      sc.forEach((s, i) => {
        if ((s.riskScore || 0) > 25) {
          const cnt = Math.floor((s.riskScore || 0) / 30);
          for (let j = 0; j < cnt; j++) {
            const sev = (s.riskScore || 0) > 65 ? 'critical' : (s.riskScore || 0) > 45 ? 'high' : 'medium';
            list.push({
              id:           `ANM-2025-${String(i * 10 + j + 100).padStart(4, '0')}`,
              scheme_id:    s.id,
              scheme_name:  s.name,
              sector:       s.sector,
              anomaly_type: TYPES[(i + j) % TYPES.length],
              severity:     sev,
              amount_cr:    parseFloat((Math.random() * 50 + 1).toFixed(1)),
              status:       STATUSES[(i + j) % STATUSES.length],
              detected_at:  new Date().toISOString(),
            });
          }
        }
      });
      const dist = { critical: 0, high: 0, medium: 0, low: 0 };
      list.forEach(a => { dist[a.severity] = (dist[a.severity] || 0) + 1; });
      return {
        total_anomalies:  list.length,
        distribution:     dist,
        total_at_risk_cr: list.reduce((s, a) => s + a.amount_cr, 0).toFixed(1),
        anomalies:        list,
        source:           'local',
      };
    }
  
    /** AI chat — backend returns full NLP response; offline returns a notice */
    async function chat(message) {
      const u = _user();
      const d = await _post('/chat', { message, user: u });
      if (d) return d;
      return {
        text:   `[Offline] Backend not reachable. Start the Flask server for full AI responses.\n\nRun: <code>python backend/main.py</code>`,
        intent: 'offline',
      };
    }
  
    /** GeoJSON map data for a department */
    async function getMap() {
      const d = await _get('/map', { dept: _dept() });
      if (d) return d;
      const sc = _localSchemes();
      return {
        scheme_count: sc.length,
        center: { lat: 20.5937, lng: 78.9629 },
        overview_url: `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(_dept() + ' India')}`,
        geojson: { type: 'FeatureCollection', features: sc.map(s => ({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [78.9629, 20.5937] },
          properties: { name: s.name, sector: s.sector, maps_url: schemeMapsUrl(s) },
        }))},
        source: 'local',
      };
    }
  
    /** Budget simulation — requires backend */
    async function simulate(params = {}) {
      const d = await _post('/simulate', { dept: _dept(), ...params });
      if (d) return d;
      return { error: 'Simulation requires the Flask backend. Run: python backend/main.py' };
    }
  
    /** Reallocation recommendations — requires backend */
    async function getRecommendations() {
      return await _get('/recommendations', { dept: _dept() });
    }
  
    // ══════════════════════════════════════════════════════════════════
    //  GOOGLE MAPS HELPERS
    //  These work 100% offline — no backend needed
    // ══════════════════════════════════════════════════════════════════
  
    /**
     * Build correct Google Maps URL for ANY scheme type:
     *   - National schemes  → "PM-KISAN, India"       (filters out 'National')
     *   - State schemes     → "Scheme, Maharashtra"
     *   - District schemes  → "Scheme, Shivajinagar, Pune, Maharashtra"
     *   - Rural schemes     → same as district
     *
     * This is the SINGLE source of truth for all Maps URLs in the app.
     * All HTML pages use this via data.js (schemeMapsUrl is also exported there).
     */
    function schemeMapsUrl(s) {
      if (!s) return 'https://www.google.com/maps/search/?api=1&query=India';
      // Build location — filter out 'National' and 'Pan India' since they're not real places
      var loc = [s.town, s.district, s.state]
        .filter(function(x) { return x && x !== 'National' && x !== 'Pan India' && x !== 'undefined'; })
        .join(', ');
      var query = loc ? (s.name + ', ' + loc) : s.name;
      return 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(query);
    }
  
    /** Open a scheme's location in Google Maps (new tab) */
    function openMaps(s) {
      window.open(schemeMapsUrl(s), '_blank', 'noopener');
    }
  
    /** Build a Maps URL from a free-text location */
    function mapsFromLocation(location) {
      return 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(location);
    }
  
    /**
     * Render a full "🗺️ View on Google Maps" button as HTML string.
     * Use inside innerHTML/template literals.
     */
    function mapsButton(s, label) {
      label = label || '🗺️ View on Google Maps';
      return '<a href="' + schemeMapsUrl(s) + '" target="_blank" rel="noopener" ' +
        'style="display:inline-flex;align-items:center;gap:6px;padding:8px 14px;' +
        'background:#ddeeff;color:#002147;border-radius:6px;font-size:12px;font-weight:700;' +
        'text-decoration:none;border:1px solid #b8d0ee">' + label + '</a>';
    }
  
    /**
     * Render a compact 📍 icon link for table rows.
     * Use inside innerHTML/template literals.
     */
    function mapsIcon(s) {
      return '<a href="' + schemeMapsUrl(s) + '" target="_blank" rel="noopener" ' +
        'title="View ' + (s.name || '') + ' on Google Maps" ' +
        'style="display:inline-flex;align-items:center;justify-content:center;' +
        'width:28px;height:28px;background:#ddeeff;border-radius:5px;' +
        'color:#002147;font-size:14px;text-decoration:none;border:1px solid #b8d0ee">📍</a>';
    }
  
    // ══════════════════════════════════════════════════════════════════
    //  PDF DOWNLOAD (via backend — falls back to alert if offline)
    // ══════════════════════════════════════════════════════════════════
  
    async function downloadSchemePDF(schemeId) {
      if (!await _ping()) {
        alert('PDF via backend requires Flask server.\n\nRun: python backend/main.py\n\nOr use the "📄 Download PDF" button on the scheme card (uses jsPDF, no server needed).');
        return;
      }
      const u = _user();
      const r = await fetch(BASE + '/pdf/scheme', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scheme_id: schemeId, user: u }),
      });
      if (!r.ok) { alert('PDF generation failed on server.'); return; }
      _saveBlob(await r.blob(), `Scheme_${schemeId}.pdf`);
    }
  
    async function downloadDeptPDF(reportType, period) {
      reportType = reportType || 'full';
      period     = period     || 'FY 2025-26';
      if (!await _ping()) {
        alert('PDF reports via backend require Flask server.\n\nRun: python backend/main.py');
        return;
      }
      const u = _user();
      const r = await fetch(BASE + '/pdf/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dept: _dept(), user: u, report_type: reportType, period }),
      });
      if (!r.ok) { alert('PDF generation failed on server.'); return; }
      _saveBlob(await r.blob(), `ArthRakshak_${reportType}_${new Date().toISOString().slice(0,10)}.pdf`);
    }
  
    function _saveBlob(blob, filename) {
      const url = URL.createObjectURL(blob);
      const a   = document.createElement('a');
      a.href = url; a.download = filename;
      document.body.appendChild(a); a.click();
      setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(url); }, 1000);
    }
  
    // ══════════════════════════════════════════════════════════════════
    //  STATUS BADGE (shows live API green/red pill)
    // ══════════════════════════════════════════════════════════════════
  
    /**
     * Renders a connection status pill into an element.
     * Usage: <span id="api-status"></span>  then  AR.renderStatusBadge('api-status')
     */
    async function renderStatusBadge(containerId) {
      const el = document.getElementById(containerId);
      if (!el) return;
      el.innerHTML = '<span style="font-size:11px;color:#94a3b8">⏳ Checking…</span>';
      const alive = await _ping();
      el.innerHTML = alive
        ? '<span style="font-size:11px;background:#e0f5ea;color:#1a7a4a;padding:3px 9px;border-radius:10px;font-weight:600;display:inline-block">🟢 API Connected</span>'
        : '<span style="font-size:11px;background:#fde8e6;color:#c0392b;padding:3px 9px;border-radius:10px;font-weight:600;display:inline-block">🔴 Offline (local data)</span>';
    }
  
    // ══════════════════════════════════════════════════════════════════
    //  PUBLIC API
    // ══════════════════════════════════════════════════════════════════
    return {
      // Data (async — auto-fallback)
      getStats, getRisk, getAnomalies, chat, getMap, simulate, getRecommendations,
      // Google Maps (sync — no backend needed)
      schemeMapsUrl, openMaps, mapsFromLocation, mapsButton, mapsIcon,
      // PDF download (async — backend needed)
      downloadSchemePDF, downloadDeptPDF,
      // Status
      renderStatusBadge,
      ping: _ping,
      // Expose user helpers
      getUser: _user,
      getDept: _dept,
    };
  })();