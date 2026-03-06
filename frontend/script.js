/**
 * ============================================================
 *  ArthRakshak – National Budget Intelligence Platform
 *  script.js  |  Core Interactive Module
 *  Version: 1.0.0
 *  Scope: login.html · otp.html · dashboard.html
 * ============================================================
 */

'use strict';

/* ============================================================
   §1  UTILITY HELPERS
   ============================================================ */

/**
 * Safe querySelector — returns null instead of throwing.
 */
function qs(selector, context) {
  return (context || document).querySelector(selector);
}

/**
 * Safe querySelectorAll — returns an Array.
 */
function qsa(selector, context) {
  return Array.from((context || document).querySelectorAll(selector));
}

/**
 * Format a number as Indian currency string.
 * e.g. 472000 → "₹4,72,000"
 */
function formatINR(value) {
  return '₹' + Number(value).toLocaleString('en-IN');
}

/**
 * Format crore values with two decimal places.
 */
function formatCr(value) {
  return '₹' + Number(value).toFixed(2) + ' Cr';
}

/**
 * Clamp a number between min and max.
 */
function clamp(val, min, max) {
  return Math.min(Math.max(val, min), max);
}

/**
 * Throttle a function to run at most once per `wait` ms.
 */
function throttle(fn, wait) {
  let last = 0;
  return function (...args) {
    const now = Date.now();
    if (now - last >= wait) {
      last = now;
      fn.apply(this, args);
    }
  };
}

/**
 * Debounce a function — only runs after `wait` ms of silence.
 */
function debounce(fn, wait) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), wait);
  };
}

/**
 * Detect which page we are currently on.
 */
function detectPage() {
  const path = window.location.pathname.split('/').pop() || 'index.html';
  if (path.includes('login'))     return 'login';
  if (path.includes('otp'))       return 'otp';
  if (path.includes('dashboard')) return 'dashboard';
  return 'unknown';
}


/* ============================================================
   §2  ALERT / TOAST NOTIFICATION SYSTEM
   Supports both the auth-page toast (#toast) and
   the dashboard toast (#dashToast).
   ============================================================ */

const Alerts = (() => {
  const SVG = {
    info:    '<svg viewBox="0 0 24 24" fill="none" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    success: '<svg viewBox="0 0 24 24" fill="none" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>',
    warn:    '<svg viewBox="0 0 24 24" fill="none" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    error:   '<svg viewBox="0 0 24 24" fill="none" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
  };

  let _timer = null;

  /**
   * Show a toast on dashboard pages (#dashToast).
   * @param {string} message  - Text to display.
   * @param {'info'|'success'|'warn'|'error'} type
   * @param {number} duration - Milliseconds before auto-hide (default 3800).
   */
  function show(message, type, duration) {
    type     = type     || 'info';
    duration = duration || 3800;

    const toast = qs('#dashToast');
    if (!toast) { showAuth(message, type); return; }

    const typeMap = { info: 'dt-info', success: 'dt-success', warn: 'dt-warn', error: 'dt-warn' };
    toast.className = 'dash-toast ' + (typeMap[type] || 'dt-info');
    toast.innerHTML = (SVG[type] || SVG.info) + '<span>' + message + '</span>';
    toast.classList.add('show');

    clearTimeout(_timer);
    _timer = setTimeout(() => toast.classList.remove('show'), duration);
  }

  /**
   * Show a toast on auth pages (#toast).
   */
  function showAuth(message, type) {
    type = type || 'error';
    const toast = qs('#toast');
    if (!toast) return;

    const msgEl = qs('#toastMsg');
    if (msgEl) msgEl.textContent = message;

    toast.className = 'toast toast-' + type;
    toast.classList.add('show');

    clearTimeout(_timer);
    _timer = setTimeout(() => toast.classList.remove('show'), 4000);
  }

  /**
   * Hide any visible toast immediately.
   */
  function hide() {
    const d = qs('#dashToast');
    const a = qs('#toast');
    if (d) d.classList.remove('show');
    if (a) a.classList.remove('show');
  }

  return { show, showAuth, hide };
})();

// Make showToast available globally (backward-compat with inline onclick attributes).
function showToast(msg, type) { Alerts.show(msg, type); }


/* ============================================================
   §3  NAVIGATION MODULE
   Handles sidebar active-state, smooth-scroll, and
   inter-page routing links.
   ============================================================ */

const Navigation = (() => {

  /**
   * Bind all sidebar nav-items so clicking them:
   *  (a) marks the item active, and
   *  (b) smooth-scrolls to the target section on the same page,
   *      OR navigates to the correct page if on a different one.
   */
  function init() {
    qsa('.nav-item').forEach(function (item) {
      item.addEventListener('click', function (e) {
        const href = item.getAttribute('data-href');
        if (href && !window.location.pathname.includes(href.split('#')[0])) {
          window.location.href = href;
          return;
        }
        setActive(item);
      });
    });

    // Highlight nav item whose section is most visible while scrolling.
    const mainEl = qs('.main-content');
    if (mainEl) {
      mainEl.addEventListener('scroll', throttle(syncActiveOnScroll, 120));
    }
  }

  /**
   * Mark a single nav-item as active, deactivate others.
   */
  function setActive(activeItem) {
    qsa('.nav-item').forEach(function (n) { n.classList.remove('active'); });
    if (activeItem) activeItem.classList.add('active');
  }

  /**
   * Smooth-scroll to a named section anchor.
   * Called by onclick="scrollToSection('id')" in the HTML.
   */
  function scrollToSection(id) {
    const el = qs('#' + id);
    if (!el) return;
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Update active nav item by matching data-section attribute.
    const match = qs('.nav-item[data-section="' + id + '"]');
    if (match) setActive(match);
  }

  /**
   * During scroll, activate the nav-item whose section is
   * closest to the top of the viewport.
   */
  function syncActiveOnScroll() {
    const anchors = qsa('.main-content [id]');
    let closest = null;
    let closestDist = Infinity;

    anchors.forEach(function (el) {
      const dist = Math.abs(el.getBoundingClientRect().top - 80);
      if (dist < closestDist) { closestDist = dist; closest = el; }
    });

    if (closest) {
      const match = qs('.nav-item[data-section="' + closest.id + '"]');
      if (match) setActive(match);
    }
  }

  // Expose scrollToSection globally (used by onclick attributes).
  window.scrollToSection = scrollToSection;

  return { init, setActive, scrollToSection };
})();


/* ============================================================
   §4  CHART ENGINE
   Pure-canvas, no external libraries.
   Draws Bar, Line and Doughnut charts into <canvas> elements.
   ============================================================ */

const Charts = (() => {

  // ── Demo datasets ────────────────────────────────────────

  const BUDGET_FLOW = {
    labels:   ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan'],
    allocated:[120,  145,  132,  165,  158,  172,  190,  185,  210,  198],
    spent:    [ 98,  112,  109,  138,  129,  148,  161,  152,  180,  167],
  };

  const RISK_SCORES = {
    labels: ['Jodhpur', 'Patna', 'Jaipur', 'Lucknow', 'Bhopal', 'Pune', 'Chennai'],
    scores: [92, 84, 71, 65, 52, 28, 14],
  };

  const SPENDING_TRENDS = {
    labels:  ['Q1 FY23', 'Q2 FY23', 'Q3 FY23', 'Q4 FY23',
              'Q1 FY24', 'Q2 FY24', 'Q3 FY24', 'Q4 FY24',
              'Q1 FY25', 'Q2 FY25'],
    rural:   [28, 34, 29, 42, 38, 45, 41, 55, 49, 58],
    health:  [18, 22, 24, 30, 27, 33, 31, 40, 36, 42],
    infra:   [42, 50, 47, 62, 58, 68, 65, 78, 72, 85],
  };

  const REPORT_SUMMARY = {
    labels: ['On Track', 'Delayed', 'Suspended', 'Completed', 'Under Review'],
    values: [142, 48, 12, 36, 10],
    colors: ['#2E8B57', '#d97706', '#c0392b', '#1F3A5F', '#9aa4b3'],
  };

  // ── Shared canvas utilities ──────────────────────────────

  function clearCanvas(ctx, canvas) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }

  function setCanvasSize(canvas) {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width  = rect.width  * dpr;
    canvas.height = rect.height * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    return { ctx, w: rect.width, h: rect.height };
  }

  // ── Bar Chart ────────────────────────────────────────────

  /**
   * Draw a grouped bar chart.
   * @param {HTMLCanvasElement} canvas
   * @param {{ labels, allocated, spent }} data
   */
  function drawBarChart(canvas, data) {
    const { ctx, w, h } = setCanvasSize(canvas);
    const pad = { top: 28, right: 20, bottom: 48, left: 52 };
    const chartW = w - pad.left - pad.right;
    const chartH = h - pad.top  - pad.bottom;

    const maxVal = Math.max(...data.allocated) * 1.15;
    const n      = data.labels.length;
    const groupW = chartW / n;
    const barW   = groupW * 0.32;
    const gap    = groupW * 0.06;

    // Background grid lines
    ctx.strokeStyle = '#e2e6ed';
    ctx.lineWidth   = 0.8;
    const steps = 5;
    for (let i = 0; i <= steps; i++) {
      const y = pad.top + chartH - (i / steps) * chartH;
      ctx.beginPath();
      ctx.moveTo(pad.left, y);
      ctx.lineTo(pad.left + chartW, y);
      ctx.stroke();

      ctx.fillStyle = '#9aa4b3';
      ctx.font      = '10px "Source Sans 3", sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(Math.round((i / steps) * maxVal), pad.left - 6, y + 3.5);
    }

    // Bars
    data.labels.forEach(function (label, i) {
      const x        = pad.left + i * groupW + groupW * 0.1;
      const allocH   = (data.allocated[i] / maxVal) * chartH;
      const spentH   = (data.spent[i]     / maxVal) * chartH;

      // Allocated bar
      ctx.fillStyle = '#1F3A5F';
      ctx.beginPath();
      ctx.roundRect(x, pad.top + chartH - allocH, barW, allocH, [3, 3, 0, 0]);
      ctx.fill();

      // Spent bar
      ctx.fillStyle = '#2E8B57';
      ctx.beginPath();
      ctx.roundRect(x + barW + gap, pad.top + chartH - spentH, barW, spentH, [3, 3, 0, 0]);
      ctx.fill();

      // X-axis labels
      ctx.fillStyle = '#6b7585';
      ctx.font      = '10px "Source Sans 3", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(label, x + barW + gap / 2, pad.top + chartH + 14);
    });

    // Axis line
    ctx.strokeStyle = '#c8cfd9';
    ctx.lineWidth   = 1;
    ctx.beginPath();
    ctx.moveTo(pad.left, pad.top + chartH);
    ctx.lineTo(pad.left + chartW, pad.top + chartH);
    ctx.stroke();

    // Legend
    const legendY = h - 12;
    _drawLegendDot(ctx, pad.left,         legendY, '#1F3A5F', 'Allocated (₹ Cr)');
    _drawLegendDot(ctx, pad.left + 130,   legendY, '#2E8B57', 'Spent (₹ Cr)');
  }

  // ── Line Chart ───────────────────────────────────────────

  /**
   * Draw a multi-line trend chart.
   * @param {HTMLCanvasElement} canvas
   * @param {{ labels, rural, health, infra }} data
   */
  function drawLineChart(canvas, data) {
    const { ctx, w, h } = setCanvasSize(canvas);
    const pad = { top: 28, right: 20, bottom: 48, left: 44 };
    const chartW = w - pad.left - pad.right;
    const chartH = h - pad.top  - pad.bottom;

    const allVals = [...data.rural, ...data.health, ...data.infra];
    const maxVal  = Math.max(...allVals) * 1.2;
    const n       = data.labels.length;

    function xPos(i) { return pad.left + (i / (n - 1)) * chartW; }
    function yPos(v) { return pad.top  + chartH - (v / maxVal) * chartH; }

    // Grid lines
    ctx.strokeStyle = '#e2e6ed';
    ctx.lineWidth   = 0.8;
    for (let i = 0; i <= 5; i++) {
      const y = pad.top + (i / 5) * chartH;
      ctx.beginPath();
      ctx.moveTo(pad.left, y);
      ctx.lineTo(pad.left + chartW, y);
      ctx.stroke();
      ctx.fillStyle = '#9aa4b3';
      ctx.font      = '10px "Source Sans 3", sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(Math.round(((5 - i) / 5) * maxVal), pad.left - 6, y + 3.5);
    }

    // Draw lines with fill areas
    const series = [
      { key: 'rural',  color: '#2E8B57', label: 'Rural Dev' },
      { key: 'health', color: '#d97706', label: 'Health' },
      { key: 'infra',  color: '#1F3A5F', label: 'Infrastructure' },
    ];

    series.forEach(function (s) {
      const vals = data[s.key];

      // Fill area
      ctx.beginPath();
      ctx.moveTo(xPos(0), pad.top + chartH);
      vals.forEach(function (v, i) { ctx.lineTo(xPos(i), yPos(v)); });
      ctx.lineTo(xPos(n - 1), pad.top + chartH);
      ctx.closePath();
      ctx.fillStyle = s.color + '18';
      ctx.fill();

      // Line
      ctx.beginPath();
      ctx.strokeStyle = s.color;
      ctx.lineWidth   = 2;
      ctx.lineJoin    = 'round';
      vals.forEach(function (v, i) {
        i === 0 ? ctx.moveTo(xPos(i), yPos(v)) : ctx.lineTo(xPos(i), yPos(v));
      });
      ctx.stroke();

      // Dots
      vals.forEach(function (v, i) {
        ctx.beginPath();
        ctx.arc(xPos(i), yPos(v), 3, 0, Math.PI * 2);
        ctx.fillStyle = s.color;
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth   = 1.5;
        ctx.stroke();
      });
    });

    // X-axis labels (every other to avoid overlap)
    ctx.fillStyle = '#6b7585';
    ctx.font      = '9px "Source Sans 3", sans-serif';
    ctx.textAlign = 'center';
    data.labels.forEach(function (label, i) {
      if (i % 2 === 0) ctx.fillText(label, xPos(i), pad.top + chartH + 14);
    });

    // Axis line
    ctx.strokeStyle = '#c8cfd9';
    ctx.lineWidth   = 1;
    ctx.beginPath();
    ctx.moveTo(pad.left, pad.top + chartH);
    ctx.lineTo(pad.left + chartW, pad.top + chartH);
    ctx.stroke();

    // Legend
    const legendY = h - 12;
    let lx = pad.left;
    series.forEach(function (s) {
      _drawLegendDot(ctx, lx, legendY, s.color, s.label);
      lx += 120;
    });
  }

  // ── Doughnut Chart ───────────────────────────────────────

  /**
   * Draw a doughnut / pie chart for report summary.
   * @param {HTMLCanvasElement} canvas
   * @param {{ labels, values, colors }} data
   */
  function drawDoughnutChart(canvas, data) {
    const { ctx, w, h } = setCanvasSize(canvas);
    const cx     = w * 0.38;
    const cy     = h / 2;
    const radius = Math.min(cx, cy) * 0.72;
    const inner  = radius * 0.55;
    const total  = data.values.reduce(function (a, b) { return a + b; }, 0);
    let start    = -Math.PI / 2;

    data.values.forEach(function (val, i) {
      const slice = (val / total) * 2 * Math.PI;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, radius, start, start + slice);
      ctx.closePath();
      ctx.fillStyle = data.colors[i];
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth   = 2;
      ctx.stroke();
      start += slice;
    });

    // Inner white circle (donut hole)
    ctx.beginPath();
    ctx.arc(cx, cy, inner, 0, Math.PI * 2);
    ctx.fillStyle = '#ffffff';
    ctx.fill();

    // Center label
    ctx.fillStyle = '#1F3A5F';
    ctx.font      = 'bold 22px "EB Garamond", serif';
    ctx.textAlign = 'center';
    ctx.fillText(total, cx, cy + 2);
    ctx.font      = '10px "Source Sans 3", sans-serif';
    ctx.fillStyle = '#9aa4b3';
    ctx.fillText('Total Schemes', cx, cy + 16);

    // Legend (right side)
    const legendX = w * 0.62;
    const lineH   = Math.min(26, (h - 20) / data.labels.length);
    const startY  = cy - ((data.labels.length - 1) * lineH) / 2;

    data.labels.forEach(function (label, i) {
      const ly = startY + i * lineH;
      ctx.fillStyle = data.colors[i];
      ctx.beginPath();
      ctx.roundRect(legendX, ly - 6, 10, 10, 2);
      ctx.fill();

      ctx.fillStyle   = '#252e3d';
      ctx.font        = '11px "Source Sans 3", sans-serif';
      ctx.textAlign   = 'left';
      ctx.fillText(label, legendX + 15, ly + 2);

      ctx.fillStyle   = '#9aa4b3';
      ctx.font        = '10px "Source Sans 3", sans-serif';
      ctx.textAlign   = 'right';
      ctx.fillText(data.values[i], w - 12, ly + 2);
    });
  }

  // ── Risk Bar Chart ───────────────────────────────────────

  /**
   * Draw a horizontal bar chart for risk scores.
   * @param {HTMLCanvasElement} canvas
   * @param {{ labels, scores }} data
   */
  function drawRiskBars(canvas, data) {
    const { ctx, w, h } = setCanvasSize(canvas);
    const pad     = { top: 12, right: 50, bottom: 12, left: 100 };
    const chartW  = w - pad.left - pad.right;
    const chartH  = h - pad.top  - pad.bottom;
    const n       = data.labels.length;
    const barH    = Math.min(18, (chartH / n) * 0.55);
    const rowH    = chartH / n;

    data.labels.forEach(function (label, i) {
      const score = data.scores[i];
      const y     = pad.top + i * rowH + (rowH - barH) / 2;
      const bw    = (score / 100) * chartW;

      // Determine color by score threshold
      const color = score >= 75 ? '#c0392b' : score >= 50 ? '#d97706' : '#2E8B57';

      // Track (empty bar)
      ctx.fillStyle = '#f0f2f6';
      ctx.beginPath();
      ctx.roundRect(pad.left, y, chartW, barH, barH / 2);
      ctx.fill();

      // Filled portion
      const grad = ctx.createLinearGradient(pad.left, 0, pad.left + bw, 0);
      grad.addColorStop(0, color);
      grad.addColorStop(1, color + 'cc');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.roundRect(pad.left, y, bw, barH, barH / 2);
      ctx.fill();

      // District label (left)
      ctx.fillStyle   = '#252e3d';
      ctx.font        = '11px "Source Sans 3", sans-serif';
      ctx.textAlign   = 'right';
      ctx.fillText(label, pad.left - 8, y + barH / 2 + 3.5);

      // Score label (right)
      ctx.fillStyle   = color;
      ctx.font        = 'bold 11px "Source Sans 3", sans-serif';
      ctx.textAlign   = 'left';
      ctx.fillText(score, pad.left + chartW + 6, y + barH / 2 + 3.5);
    });
  }

  // ── Legend helper ────────────────────────────────────────

  function _drawLegendDot(ctx, x, y, color, label) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x + 5, y - 3, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#6b7585';
    ctx.font      = '10px "Source Sans 3", sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(label, x + 14, y);
  }

  // ── Init — mount charts into containers ─────────────────

  /**
   * Find chart containers on the current page and draw into them.
   * Expects <canvas> elements with data-chart="budget|line|doughnut|risk".
   */
  function init() {
    // Make roundRect available in older browsers.
    _polyfillRoundRect();

    qsa('canvas[data-chart]').forEach(function (canvas) {
      const type = canvas.getAttribute('data-chart');
      const draw = function () {
        switch (type) {
          case 'budget':   drawBarChart(canvas,      BUDGET_FLOW);     break;
          case 'line':     drawLineChart(canvas,     SPENDING_TRENDS); break;
          case 'doughnut': drawDoughnutChart(canvas, REPORT_SUMMARY);  break;
          case 'risk':     drawRiskBars(canvas,      RISK_SCORES);     break;
        }
      };
      draw();
      window.addEventListener('resize', debounce(draw, 200));
    });
  }

  /**
   * Polyfill for CanvasRenderingContext2D.roundRect (Chrome < 99, Firefox < 112).
   */
  function _polyfillRoundRect() {
    if (CanvasRenderingContext2D.prototype.roundRect) return;
    CanvasRenderingContext2D.prototype.roundRect = function (x, y, w, h, r) {
      const radius = Array.isArray(r) ? r[0] : (r || 0);
      this.moveTo(x + radius, y);
      this.arcTo(x + w, y,     x + w, y + h, radius);
      this.arcTo(x + w, y + h, x,     y + h, radius);
      this.arcTo(x,     y + h, x,     y,     radius);
      this.arcTo(x,     y,     x + w, y,     radius);
      this.closePath();
      return this;
    };
  }

  return { init, drawBarChart, drawLineChart, drawDoughnutChart, drawRiskBars, BUDGET_FLOW, RISK_SCORES, SPENDING_TRENDS, REPORT_SUMMARY };
})();


/* ============================================================
   §5  AI CHAT ASSISTANT
   Keyword-based intent routing with multiple response sets
   and animated typing indicator.
   ============================================================ */

const ChatAssistant = (() => {

  // ── Response library ─────────────────────────────────────

  const INTENTS = [
    {
      keywords: ['spend', 'spending', 'expenditure', 'utiliz', 'utilise', 'utilized'],
      responses: [
        'Total budget utilization across 248 active schemes stands at <strong>68.4%</strong> (₹3.23L Cr of ₹4.72L Cr allocated). Rural Development and Health Ministry show the highest spending velocity at 81% and 78% respectively.',
        'Q3 FY2024-25 spending surged 23% compared to the same period last year. Infrastructure schemes absorbed ₹85 Cr more than projected, primarily in highway expansion and urban ICT projects.',
        'Three schemes have exceeded their approved budget ceilings: Mid-Day Meal Scheme (+40% in Patna), PMGSY Phase III (+2% in Jodhpur), and Saubhagya Electrification (+5% in Bhopal). Audit flags have been raised.',
      ],
    },
    {
      keywords: ['anomal', 'fraud', 'suspicious', 'irregular', 'duplicate', 'ghost'],
      responses: [
        'ArthRakshak AI has flagged <strong>7 anomalies</strong> in the current cycle. The most critical: duplicate invoice submission of ₹3.2 Cr in Jodhpur (PMGSY) and ghost beneficiary payments affecting 1,240 inactive IDs in Lucknow (MGNREGS).',
        'Pattern recognition detected a blacklisted contractor re-awarded the Jal Jeevan Mission contract in Jaipur worth ₹6.45 Cr — this bypassed the standard procurement approval workflow.',
        'Mid-Day Meal Scheme in Patna has triggered an overspend alert at 140% of ceiling. The AI model assigns a 94% probability of administrative error rather than fraud — however, a full audit is recommended.',
      ],
    },
    {
      keywords: ['risk', 'score', 'danger', 'threat', 'critical', 'high risk'],
      responses: [
        'Current risk distribution: <strong>2 Critical</strong> districts (Jodhpur 92, Patna 84), <strong>3 High</strong> districts (Jaipur 71, Lucknow 65, Bhopal 52), and <strong>2 Low-risk</strong> districts (Pune 28, Chennai 14).',
        'Jodhpur carries the highest composite risk index at <strong>92/100</strong>. Contributing factors: duplicate invoices, single-contractor dependency, and delayed milestone reporting across 3 active schemes.',
        'Risk scores are recalculated every 6 hours based on expenditure anomalies, contractor compliance, beneficiary verification, and audit response times. Districts with scores above 75 are flagged for immediate review.',
      ],
    },
    {
      keywords: ['budget', 'allocat', 'fund', 'crore', 'rupee', 'outlay'],
      responses: [
        'Total FY2024-25 outlay stands at <strong>₹4.72 lakh crore</strong> across all schemes. The Finance Ministry holds the largest allocation at ₹1.2L Cr, followed by Rural Development at ₹98,000 Cr and Health at ₹76,000 Cr.',
        'Of the ₹1.49L Cr remaining budget, approximately ₹64,000 Cr is earmarked for Q4 infrastructure disbursements. The remaining ₹85,000 Cr is held in contingency reserves pending audit clearances.',
        'Budget reallocation recommendations: divert \u20B9220 Cr from Jodhpur\u2019s suspended schemes to under-funded health infrastructure in Chennai and Pune, which shows a projected 14% efficiency gain.',
      ],
    },
    {
      keywords: ['scheme', 'project', 'pmgsy', 'jal', 'mgnregs', 'awas', 'saubhagya', 'ayushman'],
      responses: [
        'Of 248 active schemes: <strong>142 are On Track</strong>, 48 are delayed, 12 suspended, 36 completed, and 10 under review. The average completion rate for FY2024-25 is 72%, which is 4 percentage points above last year.',
        'PMGSY Phase III is the highest-risk individual scheme with a risk score of 92. It has utilised ₹98.2 Cr of ₹120.5 Cr allocated (81.5%) but has multiple compliance violations under investigation.',
        'Jal Jeevan Mission shows strong execution in Tamil Nadu and Karnataka (96% on-time delivery) but significant contractor compliance issues in Rajasthan. National average completion rate: 71%.',
      ],
    },
    {
      keywords: ['district', 'state', 'region', 'rajasthan', 'bihar', 'maharashtra', 'gujarat'],
      responses: [
        'State-level summary — Rajasthan leads in anomaly count (3 critical, 1 high) followed by Bihar (2 critical). Tamil Nadu and Karnataka show the strongest financial governance indicators with risk scores below 20.',
        'Jodhpur and Jaipur districts account for 43% of all flagged anomalies in the current cycle despite representing only 9% of total active schemes — indicating a systemic contractor compliance issue.',
        'Maharashtra is the largest single-state allocation recipient at ₹68,200 Cr. Budget utilization in the state stands at 73%, slightly above national average, with Pune performing well on Smart Cities KPIs.',
      ],
    },
    {
      keywords: ['contractor', 'vendor', 'agency', 'awarded', 'procurement'],
      responses: [
        'Contractor performance index (CPI) national average: <strong>72/100</strong>. Top performer: L&T Infrastructure (CPI 94). Bottom performer: Bharat Roads Pvt. Ltd. (CPI 38) — currently under investigation for PMGSY anomalies.',
        'AquaTech Infrastructure has been flagged for a procurement integrity violation — re-awarded the JJM Jaipur contract despite appearing on the MCA debarment watchlist. A stop-work notice has been issued.',
        'Of 248 scheme contractors, 34 have at least one pending compliance issue. The top 3 recurring violation types: delayed milestone reporting (41%), inflated material costs (29%), and subcontracting without approval (18%).',
      ],
    },
    {
      keywords: ['report', 'generate', 'summary', 'pdf', 'export', 'download'],
      responses: [
        'I can prepare automated reports for: (1) District Risk Summary, (2) Scheme Performance Overview, (3) Anomaly Audit Trail, or (4) Budget Utilization by Department. Which format would you like me to generate?',
        'The last generated report covered FY2024-25 Q3 performance across 248 schemes. Key finding: ₹9.6 Cr at risk across 7 flagged anomalies. The report has been queued for Ministry review and is available for download.',
        'Report generation is available for individual schemes, district clusters, or national roll-ups. Standard reports are generated in PDF and CSV format. Click "Generate Gov Report" in the sidebar to begin.',
      ],
    },
    {
      keywords: ['reallocat', 'transfer', 'simul', 'redirect', 'divert'],
      responses: [
        'The Reallocation Simulator models fund transfers using historical absorption rates and risk-adjusted efficiency scores. Transfers from high-risk districts to low-risk, high-capacity recipients show an average 12–18% improvement in utilization.',
        'Recommended reallocation: ₹220 Cr from Jodhpur (suspended PMGSY funds) → Chennai health infrastructure. Projected efficiency gain: 17.3%. Ministry of Finance approval required before execution.',
        'Simulation parameters factor in: remaining budget ceiling, contractor capacity, seasonal absorption patterns, and district risk score. All simulations are advisory — actual reallocation requires official sanction.',
      ],
    },
  ];

  const FALLBACK_RESPONSES = [
    'I have analysed your query. Based on current financial intelligence data, I recommend reviewing the Scheme Explorer and Anomaly Detection panels for actionable insights specific to your query.',
    'That is a good question. The ArthRakshak intelligence engine is processing your request. For detailed analysis, please use the "Generate Gov Report" function or narrow your search using the district/scheme filters.',
    'I can assist with budget analysis, anomaly detection, risk assessment, contractor compliance, and financial reallocation scenarios. Could you provide more context about the scheme or district you are asking about?',
  ];

  let _fallbackIndex = 0;
  let _chatContainer = null;
  const AI_AVATAR_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/></svg>';

  /**
   * Match user input to an intent and return a response string.
   */
  function _resolveIntent(input) {
    const lower = input.toLowerCase();

    for (const intent of INTENTS) {
      for (const keyword of intent.keywords) {
        if (lower.includes(keyword)) {
          const pool = intent.responses;
          return pool[Math.floor(Math.random() * pool.length)];
        }
      }
    }

    // Fallback — rotate through generic responses.
    const reply = FALLBACK_RESPONSES[_fallbackIndex % FALLBACK_RESPONSES.length];
    _fallbackIndex++;
    return reply;
  }

  /**
   * Append a message bubble to the chat window.
   */
  function _appendBubble(container, html, role) {
    const wrap = document.createElement('div');
    wrap.className = 'chat-msg' + (role === 'user' ? ' user' : '');

    if (role === 'user') {
      wrap.innerHTML = '<div class="chat-avatar avatar-user">RK</div><div class="chat-bubble bubble-user">' + html + '</div>';
    } else {
      wrap.innerHTML = '<div class="chat-avatar avatar-ai">' + AI_AVATAR_SVG + '</div><div class="chat-bubble bubble-ai">' + html + '</div>';
    }

    container.appendChild(wrap);
    container.scrollTop = container.scrollHeight;
    return wrap;
  }

  /**
   * Show the animated typing indicator while "AI is thinking".
   */
  function _showTyping(container) {
    const wrap = document.createElement('div');
    wrap.className = 'chat-msg';
    wrap.innerHTML = '<div class="chat-avatar avatar-ai">' + AI_AVATAR_SVG + '</div><div class="chat-bubble bubble-ai"><div class="typing-dots"><span></span><span></span><span></span></div></div>';
    container.appendChild(wrap);
    container.scrollTop = container.scrollHeight;
    return wrap;
  }

  /**
   * Handle sending a message — called by button click or Enter key.
   */
  function send() {
    const inputEl  = qs('#chatInput');
    const container = qs('#chatMessages');
    if (!inputEl || !container) return;

    const message = inputEl.value.trim();
    if (!message) return;

    inputEl.value = '';
    _appendBubble(container, _escapeHTML(message), 'user');

    const typingEl = _showTyping(container);
    const delay    = 900 + Math.random() * 700;

    setTimeout(function () {
      container.removeChild(typingEl);
      const response = _resolveIntent(message);
      _appendBubble(container, response, 'ai');
    }, delay);
  }

  /**
   * Bind the chat input and send button for the given page.
   */
  function init() {
    const inputEl  = qs('#chatInput');
    const sendBtn  = qs('.chat-send');
    if (!inputEl) return;

    inputEl.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') send();
    });

    if (sendBtn) sendBtn.addEventListener('click', send);
  }

  function _escapeHTML(str) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  // Expose globally for inline onclick support.
  window.sendChat = send;

  return { init, send };
})();


/* ============================================================
   §6  FILE UPLOAD HANDLER
   Handles CSV file input on the anomaly / upload pages.
   ============================================================ */

const FileUpload = (() => {

  /**
   * Bind all file inputs with data-upload="csv" or id="csvUpload".
   */
  function init() {
    qsa('input[type="file"][data-upload], input#csvUpload, input#fileUpload').forEach(_bindInput);

    // Drag-and-drop zones.
    qsa('.upload-zone').forEach(_bindDropZone);
  }

  function _bindInput(inputEl) {
    inputEl.addEventListener('change', function () {
      const file = inputEl.files && inputEl.files[0];
      if (!file) return;
      _processFile(file, inputEl);
    });
  }

  function _bindDropZone(zone) {
    zone.addEventListener('dragover', function (e) {
      e.preventDefault();
      zone.classList.add('drag-over');
    });
    zone.addEventListener('dragleave', function () {
      zone.classList.remove('drag-over');
    });
    zone.addEventListener('drop', function (e) {
      e.preventDefault();
      zone.classList.remove('drag-over');
      const file = e.dataTransfer.files[0];
      if (file) _processFile(file, null, zone);
    });
  }

  function _processFile(file, inputEl, zone) {
    const statusEl = qs('#uploadStatus') || qs('.upload-status');
    const isCSV    = file.name.toLowerCase().endsWith('.csv') || file.type === 'text/csv';

    if (!isCSV) {
      _setStatus(statusEl, 'error', 'Invalid file type. Please upload a .csv file.');
      Alerts.show('Invalid file type. Please upload a CSV.', 'warn');
      return;
    }

    // Show loading state.
    _setStatus(statusEl, 'loading', 'Reading file "' + file.name + '"…');

    const reader = new FileReader();
    reader.onload = function (e) {
      const lines = e.target.result.split('\n').filter(function (l) { return l.trim(); });
      const rows  = lines.length - 1; // minus header row

      setTimeout(function () {
        _setStatus(statusEl, 'success',
          'Dataset uploaded successfully. ' +
          '<strong>' + rows + ' records</strong> from "' + file.name + '" loaded into the anomaly detection engine.');

        Alerts.show('Dataset uploaded successfully. AI analysis starting…', 'success');

        // Trigger a mock AI analysis alert after a delay.
        setTimeout(function () {
          Alerts.show('AI analysis completed. ' + Math.max(1, Math.floor(rows * 0.04)) + ' potential anomalies identified.', 'warn', 5000);
        }, 2800);

        // Preview first few rows if a preview container exists.
        _renderPreview(lines);
      }, 800);
    };
    reader.onerror = function () {
      _setStatus(statusEl, 'error', 'Failed to read file. Please try again.');
      Alerts.show('File read error. Please try again.', 'error');
    };
    reader.readAsText(file);
  }

  function _setStatus(el, state, message) {
    if (!el) return;
    el.className = 'upload-status upload-status--' + state;
    el.innerHTML = message;
    el.style.display = 'block';
  }

  function _renderPreview(lines) {
    const container = qs('#csvPreview');
    if (!container || lines.length < 2) return;

    const headers = lines[0].split(',');
    const rows    = lines.slice(1, 6); // Preview max 5 data rows

    let html = '<table class="data-table"><thead><tr>';
    headers.forEach(function (h) { html += '<th>' + h.trim() + '</th>'; });
    html += '</tr></thead><tbody>';
    rows.forEach(function (row) {
      html += '<tr>';
      row.split(',').forEach(function (cell) { html += '<td>' + cell.trim() + '</td>'; });
      html += '</tr>';
    });
    html += '</tbody></table>';

    container.innerHTML = html;
    container.style.display = 'block';
  }

  return { init };
})();


/* ============================================================
   §7  REALLOCATION SIMULATOR
   Calculates remaining budget, new risk score, efficiency
   gain, and generates a detailed simulation breakdown.
   ============================================================ */

const Simulator = (() => {

  // District financial profiles used by the simulation engine.
  const DISTRICT_DATA = {
    'Jodhpur, Rajasthan':     { allocated: 320.5, spent: 298.2, risk: 92, capacity: 0.45 },
    'Patna, Bihar':           { allocated: 180.0, spent: 162.5, risk: 84, capacity: 0.50 },
    'Jaipur, Rajasthan':      { allocated: 240.0, spent: 168.3, risk: 71, capacity: 0.62 },
    'Lucknow, Uttar Pradesh': { allocated: 195.0, spent: 152.7, risk: 65, capacity: 0.68 },
    'Bhopal, Madhya Pradesh': { allocated: 160.0, spent: 118.4, risk: 52, capacity: 0.72 },
    'Pune, Maharashtra':      { allocated: 280.0, spent: 165.0, risk: 28, capacity: 0.88 },
    'Chennai, Tamil Nadu':    { allocated: 310.0, spent: 178.0, risk: 14, capacity: 0.94 },
    'Ahmedabad, Gujarat':     { allocated: 220.0, spent: 145.0, risk: 22, capacity: 0.90 },
    'Hyderabad, Telangana':   { allocated: 190.0, spent: 128.0, risk: 18, capacity: 0.91 },
    'Bengaluru, Karnataka':   { allocated: 265.0, spent: 172.0, risk: 16, capacity: 0.93 },
    'Kolkata, West Bengal':   { allocated: 175.0, spent: 118.0, risk: 31, capacity: 0.82 },
  };

  /**
   * Run the reallocation simulation with the given parameters.
   * Called by the "Simulate Reallocation" button.
   */
  function run() {
    const srcEl  = qs('#simSource');
    const dstEl  = qs('#simDest');
    const amtEl  = qs('#simAmount');
    const resEl  = qs('#simResult');
    const txtEl  = qs('#simResultText');

    if (!srcEl || !dstEl || !amtEl) return;

    const src = srcEl.value;
    const dst = dstEl.value;
    const amt = parseFloat(amtEl.value);

    if (!src || !dst || isNaN(amt) || amt <= 0) {
      Alerts.show('Please fill in Source District, Destination District and Amount.', 'warn');
      return;
    }

    if (src === dst) {
      Alerts.show('Source and destination districts must be different.', 'warn');
      return;
    }

    const srcData = DISTRICT_DATA[src] || { allocated: 200, spent: 160, risk: 70, capacity: 0.6 };
    const dstData = DISTRICT_DATA[dst] || { allocated: 200, spent: 100, risk: 25, capacity: 0.88 };

    // Calculate remaining budget in source after transfer.
    const srcRemaining   = srcData.allocated - srcData.spent - amt;
    const srcRemainingPct = clamp(((srcData.allocated - srcData.spent - amt) / srcData.allocated) * 100, 0, 100);

    // Estimate new risk for source (lower spend → slightly lower risk, but risk is also systemic).
    const srcNewRisk = clamp(Math.round(srcData.risk * 0.88 - (amt / srcData.allocated) * 12), 10, 98);

    // Estimate absorption at destination.
    const dstAbsorbed    = Math.round(amt * dstData.capacity);
    const dstEfficiency  = (dstAbsorbed / amt * 100).toFixed(1);

    // Projected overall efficiency gain.
    const efficiencyGain = ((dstData.capacity - 0.6) * (amt / 500) * 20 + 4).toFixed(1);

    // Ministry approval threshold (flag if > ₹50 Cr).
    const requiresApproval = amt > 50;
    const approvalText = requiresApproval
      ? '<span style="color:var(--amber);font-weight:700;">⚠ Ministry of Finance approval required for transfers above ₹50 Cr.</span>'
      : '<span style="color:var(--green-dark);font-weight:700;">✓ Transfer within district authority limits — no Ministry approval required.</span>';

    const feasible = srcRemaining >= 0;

    if (!feasible) {
      Alerts.show('Insufficient remaining budget in source district for this transfer.', 'warn');
      if (txtEl) txtEl.innerHTML = '<span style="color:var(--red);font-weight:700;">✗ Transfer not feasible — source district remaining budget is ₹' + (srcData.allocated - srcData.spent).toFixed(2) + ' Cr, which is less than the requested ₹' + amt.toFixed(2) + ' Cr.</span>';
      if (resEl) resEl.classList.add('show');
      return;
    }

    if (txtEl) {
      txtEl.innerHTML =
        '<strong>Transfer Summary</strong><br>' +
        '• Amount: <strong>₹' + amt.toFixed(2) + ' Cr</strong> from ' + src.split(',')[0] + ' → ' + dst.split(',')[0] + '<br>' +
        '• Source remaining budget post-transfer: <strong>₹' + srcRemaining.toFixed(2) + ' Cr</strong> (' + srcRemainingPct.toFixed(1) + '%)<br>' +
        '• Source risk score after transfer: <strong>' + srcNewRisk + '/100</strong> (was ' + srcData.risk + ')<br>' +
        '• Destination absorption estimate: <strong>₹' + dstAbsorbed + ' Cr</strong> (' + dstEfficiency + '% efficiency)<br>' +
        '• Projected national efficiency gain: <strong>+' + efficiencyGain + '%</strong><br><br>' +
        approvalText;
    }

    if (resEl) resEl.classList.add('show');

    Alerts.show('Simulation generated. Review results in the simulator panel.', 'success');

    // Update risk bar in the risk panel if it exists.
    _updateRiskDisplay(src, srcNewRisk);
  }

  /**
   * Visually update the risk bar for the source district after simulation.
   */
  function _updateRiskDisplay(districtName, newScore) {
    const shortName = districtName.split(',')[0];
    qsa('.risk-district').forEach(function (el) {
      if (el.textContent.includes(shortName)) {
        const row     = el.closest('.risk-row');
        if (!row) return;
        const bar     = qs('.risk-bar-fill', row);
        const pctEl   = qs('.risk-pct', row);
        if (bar) {
          bar.style.width = newScore + '%';
          bar.className   = 'risk-bar-fill ' + (newScore >= 75 ? 'rb-fill-red' : newScore >= 50 ? 'rb-fill-amber' : 'rb-fill-green');
        }
        if (pctEl) {
          pctEl.textContent = newScore;
          pctEl.style.color = newScore >= 75 ? 'var(--red)' : newScore >= 50 ? 'var(--amber)' : 'var(--green-dark)';
        }
      }
    });
  }

  /**
   * Reset the simulation form and hide results.
   */
  function reset() {
    const fields = ['#simSource', '#simDest', '#simAmount'];
    fields.forEach(function (sel) {
      const el = qs(sel);
      if (el) el.value = '';
    });
    const resEl = qs('#simResult');
    if (resEl) resEl.classList.remove('show');
  }

  // Expose globally for onclick attributes.
  window.runSimulation = run;
  window.resetSimulation = reset;

  return { run, reset };
})();


/* ============================================================
   §8  SCHEME TABLE — DATA, FILTERING, DETAIL PANEL
   Lifted from inline dashboard script and modularised.
   ============================================================ */

const SchemeTable = (() => {

  const DATA = [
    { id:'SCH-001', name:'PMGSY Phase III – Road Construction',    dept:'Rural Development',      state:'Rajasthan',      district:'Jodhpur',    allocated:120.5, spent:98.2,  contractor:'Bharat Roads Pvt. Ltd.',    addr:'Plot 12, Industrial Area, Jodhpur, RJ 342001',      status:'Active',       risk:'Critical' },
    { id:'SCH-002', name:'Jal Jeevan Mission – Water Supply',      dept:'Jal Shakti',             state:'Rajasthan',      district:'Jaipur',     allocated:85.0,  spent:61.3,  contractor:'AquaTech Infrastructure',    addr:'Sector 9, Malviya Nagar, Jaipur, RJ 302017',        status:'Active',       risk:'High'     },
    { id:'SCH-003', name:'PM Awas Yojana – Urban Housing',         dept:'Housing & Urban Affairs',state:'Maharashtra',    district:'Pune',       allocated:200.0, spent:132.5, contractor:'Sunrise Constructions Ltd.', addr:'Hinjewadi Phase 2, Pune, MH 411057',                status:'Active',       risk:'Medium'   },
    { id:'SCH-004', name:'MGNREGS – Rural Employment',             dept:'Rural Development',      state:'Uttar Pradesh',  district:'Lucknow',    allocated:45.0,  spent:38.7,  contractor:'State Implementation Cell',  addr:'Vidhan Sabha Marg, Lucknow, UP 226001',             status:'Under Review', risk:'High'     },
    { id:'SCH-005', name:'Mid-Day Meal Scheme',                    dept:'Education Department',   state:'Bihar',          district:'Patna',      allocated:30.0,  spent:42.1,  contractor:'Bihar State Food Corp.',     addr:'Gandhi Maidan, Patna, BR 800001',                   status:'Suspended',    risk:'Critical' },
    { id:'SCH-006', name:'Smart Cities Mission – ICT',             dept:'Urban Development',      state:'Karnataka',      district:'Bengaluru',  allocated:150.0, spent:89.0,  contractor:'TechCity Solutions Ltd.',    addr:'Koramangala, Bengaluru, KA 560034',                 status:'Active',       risk:'Low'      },
    { id:'SCH-007', name:'Digital India – Village Connectivity',   dept:'MeitY',                  state:'Gujarat',        district:'Ahmedabad',  allocated:60.0,  spent:34.2,  contractor:'Reliance Jio Infocomm',      addr:'Naroda, Ahmedabad, GJ 382330',                      status:'Active',       risk:'Medium'   },
    { id:'SCH-008', name:'Saubhagya – Rural Electrification',      dept:'Power Ministry',         state:'Madhya Pradesh', district:'Bhopal',     allocated:95.0,  spent:77.4,  contractor:'MP Power Generating Co.',    addr:'Shakti Bhawan, Bhopal, MP 462004',                  status:'Active',       risk:'Medium'   },
    { id:'SCH-009', name:'Ayushman Bharat – Health Infra',         dept:'Health Ministry',        state:'Tamil Nadu',     district:'Chennai',    allocated:180.0, spent:112.0, contractor:'Apollo Healthcare Infra',    addr:'Greams Road, Chennai, TN 600006',                   status:'Active',       risk:'Low'      },
    { id:'SCH-010', name:'National Highway Expansion NH-48',       dept:'Road Transport',         state:'Maharashtra',    district:'Pune',       allocated:340.0, spent:198.5, contractor:'L&T Infrastructure Ltd.',    addr:'Baner, Pune, MH 411045',                            status:'Active',       risk:'Low'      },
  ];

  const RISK_CLASS   = { Critical:'rb-critical', High:'rb-high', Medium:'rb-medium', Low:'rb-low' };
  const STATUS_CLASS = { Active:'sp-green', 'Under Review':'sp-amber', Suspended:'sp-red', Completed:'sp-navy' };

  function _escapeAttr(str) { return str.replace(/'/g, '&#39;').replace(/"/g, '&quot;'); }

  function render(data) {
    const tbody   = qs('#schemeTableBody');
    const countEl = qs('#schemeCount');
    if (!tbody) return;

    tbody.innerHTML = '';
    if (countEl) countEl.textContent = data.length;

    if (data.length === 0) {
      tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;padding:24px;color:var(--gray-400);">No schemes match the current filters.</td></tr>';
      return;
    }

    data.forEach(function (s) {
      const tr = document.createElement('tr');
      tr.innerHTML =
        '<td class="scheme-name-cell" title="' + _escapeAttr(s.name) + '">' + s.name + '</td>' +
        '<td>' + s.dept + '</td>' +
        '<td>' + s.state + '</td>' +
        '<td>' + s.district + '</td>' +
        '<td class="text-right text-mono">₹' + s.allocated.toFixed(1) + '</td>' +
        '<td class="text-right text-mono">₹' + s.spent.toFixed(1) + '</td>' +
        '<td>' + s.contractor.split(' ').slice(0, 2).join(' ') + '…</td>' +
        '<td><span class="status-pill ' + (STATUS_CLASS[s.status] || 'sp-gray') + '">' + s.status + '</span></td>' +
        '<td><span class="risk-badge ' + (RISK_CLASS[s.risk] || 'rb-low') + '">' + s.risk + '</span></td>';

      tr.addEventListener('click', function () {
        qsa('#schemeTableBody tr').forEach(function (r) { r.classList.remove('selected'); });
        tr.classList.add('selected');
        _renderDetail(s);
      });

      tbody.appendChild(tr);
    });
  }

  function _renderDetail(s) {
    const container = qs('#detailContent');
    if (!container) return;

    const pct      = Math.round(s.spent / s.allocated * 100);
    const barColor = pct > 100 ? 'var(--red)' : pct > 80 ? 'var(--amber)' : 'var(--green)';
    const barW     = Math.min(pct, 100);

    container.innerHTML =
      '<div class="detail-body">' +
        '<div>' +
          '<div class="detail-scheme-title">' + s.name + '</div>' +
          '<span class="detail-id-tag">' + s.id + '</span>' +
        '</div>' +
        '<div class="detail-meta-grid">' +
          '<div><div class="detail-meta-label">Department</div><div class="detail-meta-value">' + s.dept + '</div></div>' +
          '<div><div class="detail-meta-label">Status</div><div class="detail-meta-value"><span class="status-pill ' + (STATUS_CLASS[s.status] || 'sp-gray') + '">' + s.status + '</span></div></div>' +
          '<div><div class="detail-meta-label">State</div><div class="detail-meta-value">' + s.state + '</div></div>' +
          '<div><div class="detail-meta-label">District</div><div class="detail-meta-value">' + s.district + '</div></div>' +
        '</div>' +
        '<div class="budget-vis">' +
          '<div class="budget-vis-row"><span class="budget-vis-label">Budget Utilization</span><span class="budget-vis-pct" style="color:' + barColor + '">' + pct + '%</span></div>' +
          '<div class="budget-bar-outer"><div class="budget-bar-inner" style="width:' + barW + '%;background:linear-gradient(90deg,' + barColor + ',' + barColor + 'cc)"></div></div>' +
          '<div class="budget-numbers"><span>Spent: ₹' + s.spent.toFixed(2) + ' Cr</span><span>Allocated: ₹' + s.allocated.toFixed(2) + ' Cr</span></div>' +
        '</div>' +
        '<div class="contractor-box">' +
          '<div class="contractor-box-label">Assigned Contractor</div>' +
          '<div class="contractor-box-name">' + s.contractor + '</div>' +
          '<div class="contractor-box-addr">' + s.addr + '</div>' +
        '</div>' +
        '<div style="display:flex;align-items:center;justify-content:space-between;">' +
          '<span style="font-size:11.5px;color:var(--gray-500);font-weight:600;">Risk Level:</span>' +
          '<span class="risk-badge ' + (RISK_CLASS[s.risk] || 'rb-low') + '" style="font-size:12px;">' + s.risk + '</span>' +
        '</div>' +
        '<div class="detail-actions">' +
          '<button class="detail-btn db-navy"   onclick="Alerts.show(\'Opening map for ' + _escapeAttr(s.district) + '…\',\'info\')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/></svg>View on Map</button>' +
          '<button class="detail-btn db-red"    onclick="Alerts.show(\'Running anomaly scan on ' + s.id + '…\',\'warn\')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>Detect Anomaly</button>' +
          '<button class="detail-btn db-amber"  onclick="Alerts.show(\'Calculating risk for ' + s.id + '…\',\'warn\')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/></svg>Risk Score</button>' +
          '<button class="detail-btn db-green"  onclick="Alerts.show(\'Generating report for ' + s.id + '…\',\'info\')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>Report</button>' +
          '<button class="detail-btn db-outline" style="grid-column:1/-1;" onclick="Alerts.show(\'Opening reallocation simulator for ' + s.id + '…\',\'info\')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/></svg>Simulate Reallocation</button>' +
        '</div>' +
      '</div>';
  }

  function applyFilters() {
    const state = (qs('#filterState')  || {}).value || '';
    const dist  = (qs('#filterDistrict') || {}).value || '';
    const dept  = (qs('#filterDept')   || {}).value || '';
    const risk  = (qs('#filterRisk')   || {}).value || '';

    const filtered = DATA.filter(function (s) {
      return (!state || s.state    === state) &&
             (!dist  || s.district === dist)  &&
             (!dept  || s.dept     === dept)  &&
             (!risk  || s.risk     === risk);
    });

    render(filtered);
  }

  function resetFilters() {
    ['#filterState', '#filterDistrict', '#filterDept', '#filterRisk'].forEach(function (sel) {
      const el = qs(sel);
      if (el) el.value = '';
    });
    render(DATA);
  }

  function initSearch() {
    const searchEl = qs('#globalSearch');
    if (!searchEl) return;

    searchEl.addEventListener('input', debounce(function () {
      const q = searchEl.value.toLowerCase().trim();
      if (!q) { render(DATA); return; }
      const filtered = DATA.filter(function (s) {
        return s.name.toLowerCase().includes(q)       ||
               s.contractor.toLowerCase().includes(q) ||
               s.district.toLowerCase().includes(q)   ||
               s.state.toLowerCase().includes(q)      ||
               s.dept.toLowerCase().includes(q)       ||
               s.id.toLowerCase().includes(q);
      });
      render(filtered);
    }, 180));
  }

  function init() {
    render(DATA);
    initSearch();
  }

  // Expose globals for inline onclick attributes.
  window.applyFilters  = applyFilters;
  window.resetFilters  = resetFilters;

  return { init, render, applyFilters, resetFilters, DATA };
})();


/* ============================================================
   §9  LIVE CLOCK
   Updates the date/time display in the nav bar and page header.
   ============================================================ */

const Clock = (() => {

  function update() {
    const now     = new Date();
    const timeStr = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const dateStr = now.toLocaleDateString('en-IN', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' });

    const clockEl = qs('#clockDisplay');
    if (clockEl) clockEl.textContent = dateStr + '  ' + timeStr;

    const dateEl = qs('#dateDisplay');
    if (dateEl && !dateEl._manuallySet) {
      dateEl.textContent = now.toLocaleDateString('en-IN', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' });
      dateEl._manuallySet = true; // Only set once (doesn't need second-level updates).
    }
  }

  function init() {
    update();
    setInterval(update, 1000);
  }

  return { init };
})();


/* ============================================================
   §10  OVERVIEW CARDS — ANIMATED COUNTER
   Numbers count up from 0 to their target value on page load.
   ============================================================ */

const OverviewCounters = (() => {

  function animateCounter(el, target, duration, prefix, suffix) {
    prefix   = prefix   || '';
    suffix   = suffix   || '';
    duration = duration || 1200;

    const start    = Date.now();
    const isFloat  = target % 1 !== 0;

    function step() {
      const progress = Math.min((Date.now() - start) / duration, 1);
      const ease     = 1 - Math.pow(1 - progress, 3); // cubic ease-out
      const current  = isFloat ? (target * ease).toFixed(1) : Math.round(target * ease);
      el.textContent = prefix + current + suffix;
      if (progress < 1) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
  }

  function init() {
    qsa('.oc-value[data-target]').forEach(function (el) {
      const target = parseFloat(el.getAttribute('data-target'));
      const prefix = el.getAttribute('data-prefix') || '';
      const suffix = el.getAttribute('data-suffix') || '';
      animateCounter(el, target, 1400, prefix, suffix);
    });
  }

  return { init };
})();


/* ============================================================
   §11  FORM VALIDATION  (login.html & otp.html)
   Centralised validation so all pages use the same logic.
   ============================================================ */

const FormValidation = (() => {

  function markError(id) {
    const el = qs('#' + id);
    if (!el) return;
    el.classList.add('error');
    const clear = function () { el.classList.remove('error'); };
    el.addEventListener('input', clear, { once: true });
    el.addEventListener('change', clear, { once: true });
  }

  function validateLogin() {
    const fields = [
      { id: 'officerId', label: 'Officer ID'    },
      { id: 'fullName',  label: 'Full Name'      },
      { id: 'dob',       label: 'Date of Birth'  },
      { id: 'department',label: 'Department'     },
      { id: 'password',  label: 'Password'       },
    ];

    let firstError = null;
    fields.forEach(function (f) {
      const el = qs('#' + f.id);
      if (el && !el.value.trim()) {
        markError(f.id);
        if (!firstError) firstError = f.label;
      }
    });

    if (firstError) {
      Alerts.showAuth('Please complete: ' + firstError + ' and all required fields.', 'error');
      return false;
    }

    const captcha = qs('#captchaCheck');
    if (captcha && !captcha.checked) {
      const box = qs('#captchaBox');
      if (box) { box.style.borderColor = '#c0392b'; setTimeout(function () { box.style.borderColor = ''; }, 2500); }
      Alerts.showAuth('Please confirm the authorized access declaration.', 'error');
      return false;
    }

    return true;
  }

  function handleLogin() {
    if (!validateLogin()) return;
    window.location.href = 'otp.html';
  }

  function toggleCaptcha() {
    const cb  = qs('#captchaCheck');
    const box = qs('#captchaBox');
    if (!cb || !box) return;
    cb.checked = !cb.checked;
    box.classList.toggle('checked', cb.checked);
  }

  function syncCaptcha() {
    const cb  = qs('#captchaCheck');
    const box = qs('#captchaBox');
    if (!cb || !box) return;
    box.classList.toggle('checked', cb.checked);
  }

  // Expose globals for inline onclick attributes on auth pages.
  window.handleLogin   = handleLogin;
  window.toggleCaptcha = toggleCaptcha;
  window.syncCaptcha   = syncCaptcha;

  return { validateLogin, handleLogin };
})();


/* ============================================================
   §12  OTP MODULE  (otp.html)
   Handles 6-box OTP input, countdown timer, and verify logic.
   ============================================================ */

const OTPModule = (() => {

  const BOX_IDS = ['o1', 'o2', 'o3', 'o4', 'o5', 'o6'];
  let _timerInterval = null;
  let _timeLeft      = 60;
  let _attempts      = 3;

  function getBoxes() {
    return BOX_IDS.map(function (id) { return qs('#' + id); }).filter(Boolean);
  }

  function getOTP() {
    return getBoxes().map(function (b) { return b.value; }).join('');
  }

  function clearAll() {
    getBoxes().forEach(function (b) { b.value = ''; b.classList.remove('filled', 'error-box'); });
  }

  function shakeBoxes() {
    getBoxes().forEach(function (b) {
      b.classList.add('error-box');
      b.style.transform = 'translateX(-4px)';
      setTimeout(function () { b.style.transform = 'translateX(4px)'; }, 80);
      setTimeout(function () { b.style.transform = ''; }, 160);
    });
  }

  function startTimer() {
    clearInterval(_timerInterval);
    _timeLeft = 60;
    const display = qs('#timerDisplay');
    const resend  = qs('#resendBtn');

    _timerInterval = setInterval(function () {
      _timeLeft--;
      if (display) {
        display.textContent = _timeLeft + 's';
        display.className   = 'timer' + (_timeLeft <= 10 ? '' : ' safe');
      }
      if (_timeLeft <= 0) {
        clearInterval(_timerInterval);
        if (display) { display.textContent = 'Expired'; display.className = 'timer'; }
        if (resend)  resend.disabled = false;
      }
    }, 1000);
  }

  function verify() {
    const otp = getOTP();

    if (otp.length < 6) {
      shakeBoxes();
      Alerts.showAuth('Please enter all 6 digits of the OTP.', 'error');
      const nextEmpty = getBoxes().findIndex(function (b) { return !b.value; });
      if (nextEmpty >= 0) getBoxes()[nextEmpty].focus();
      return;
    }

    if (_timeLeft <= 0) {
      shakeBoxes();
      Alerts.showAuth('OTP has expired. Please request a new one.', 'error');
      return;
    }

    _attempts--;
    const attemptsEl = qs('#attemptsLeft');
    if (attemptsEl) attemptsEl.textContent = _attempts + ' attempt' + (_attempts !== 1 ? 's' : '') + ' remaining';

    // In production this would verify against a server-issued OTP.
    // For the demo, any 6-digit entry succeeds.
    clearInterval(_timerInterval);
    const overlay = qs('#successOverlay');
    if (overlay) overlay.classList.add('show');
    setTimeout(function () { window.location.href = 'dashboard.html'; }, 2200);
  }

  function resend() {
    clearAll();
    _attempts = 3;
    const attemptsEl = qs('#attemptsLeft');
    if (attemptsEl) attemptsEl.textContent = '3 attempts remaining';
    const resend = qs('#resendBtn');
    if (resend) resend.disabled = true;
    startTimer();
    Alerts.showAuth('A new OTP has been sent to your registered email.', 'success');
    const firstBox = qs('#o1');
    if (firstBox) firstBox.focus();
  }

  function initBoxes() {
    const boxes = getBoxes();
    boxes.forEach(function (box, i) {
      box.addEventListener('input', function (e) {
        const val = e.target.value.replace(/\D/g, '');
        box.value = val;
        if (val) {
          box.classList.add('filled');
          if (i < boxes.length - 1) boxes[i + 1].focus();
        } else {
          box.classList.remove('filled');
        }
      });

      box.addEventListener('keydown', function (e) {
        if (e.key === 'Backspace' && !box.value && i > 0) {
          boxes[i - 1].focus();
          boxes[i - 1].value = '';
          boxes[i - 1].classList.remove('filled');
        }
        if (e.key === 'ArrowLeft'  && i > 0)              boxes[i - 1].focus();
        if (e.key === 'ArrowRight' && i < boxes.length - 1) boxes[i + 1].focus();
      });

      box.addEventListener('paste', function (e) {
        e.preventDefault();
        const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
        pasted.split('').forEach(function (ch, j) {
          if (boxes[j]) { boxes[j].value = ch; boxes[j].classList.add('filled'); }
        });
        const next = Math.min(pasted.length, boxes.length - 1);
        boxes[next].focus();
      });
    });

    if (boxes[0]) boxes[0].focus();
  }

  function init() {
    initBoxes();
    startTimer();
  }

  // Expose globals for inline onclick attributes.
  window.verifyOTP  = verify;
  window.resendOTP  = resend;

  return { init, verify, resend };
})();


/* ============================================================
   §13  SCHEDULED ALERTS
   Periodic background notifications to simulate real-time
   monitoring events in the dashboard.
   ============================================================ */

const ScheduledAlerts = (() => {

  const MESSAGES = [
    { msg: 'AI analysis completed — 2 new patterns detected in Rajasthan data.', type: 'warn',    delay: 8000  },
    { msg: 'Simulation generated for Jodhpur → Chennai reallocation scenario.', type: 'success', delay: 20000 },
    { msg: 'Budget utilization report for FY2024-25 Q3 is ready for download.', type: 'info',    delay: 35000 },
    { msg: 'AI analysis completed — MGNREGS beneficiary database cross-check finished.', type: 'success', delay: 52000 },
    { msg: 'High-risk alert: Expenditure spike detected in Patna Mid-Day Meal Scheme.', type: 'warn', delay: 70000 },
    { msg: 'Contractor compliance score updated for 34 active scheme vendors.', type: 'info',    delay: 90000 },
  ];

  function init() {
    MESSAGES.forEach(function (item) {
      setTimeout(function () { Alerts.show(item.msg, item.type); }, item.delay);
    });
  }

  return { init };
})();


/* ============================================================
   §14  PAGE BOOTSTRAP
   Detect current page and initialise only the relevant modules.
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  const page = detectPage();

  // Modules that run on every page.
  Clock.init();

  switch (page) {

    case 'login':
      // FormValidation globals are exposed in the module definition.
      break;

    case 'otp':
      OTPModule.init();
      break;

    case 'dashboard':
      Navigation.init();
      SchemeTable.init();
      ChatAssistant.init();
      FileUpload.init();
      Charts.init();
      OverviewCounters.init();
      ScheduledAlerts.init();
      break;

    default:
      // Unknown or index page — init common modules only.
      Navigation.init();
      Charts.init();
      ChatAssistant.init();
      FileUpload.init();
      break;
  }

  // Always expose Alerts globally so inline onclick="Alerts.show(...)" works.
  window.Alerts = Alerts;
});