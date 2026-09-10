/**
 * PROJECT DNA MATRIX - INTERACTIVE ARCHITECTURE CANVAS
 * High-performance node-and-edge visualizer with zoom, pan, data flow pulses, and selection.
 */

class DNACanvas {
  constructor(canvasElement, onNodeSelect) {
    this.canvas = canvasElement;
    this.ctx = canvasElement.getContext('2d');
    this.onNodeSelect = onNodeSelect || (() => {});

    this.nodes = [];
    this.edges = [];
    this.selectedNodeId = null;
    this.hoveredNodeId = null;

    // Viewport Transform
    this.scale = 1.0;
    this.panX = 50;
    this.panY = 50;
    this.isDragging = false;
    this.dragStartX = 0;
    this.dragStartY = 0;

    // Animation loop & particles
    this.pulseOffset = 0;
    this.animationFrameId = null;

    // Category Color Palette (Curated Engineering Palette)
    this.categoryStyles = {
      "Client / UI": { bg: "#0284c7", border: "#38bdf8", glow: "rgba(56, 189, 248, 0.4)" },
      "API Gateway": { bg: "#7c3aed", border: "#a78bfa", glow: "rgba(167, 139, 250, 0.4)" },
      "Core Logic": { bg: "#2563eb", border: "#60a5fa", glow: "rgba(96, 165, 250, 0.4)" },
      "AI / ML Core": { bg: "#059669", border: "#34d399", glow: "rgba(52, 211, 153, 0.4)" },
      "Storage / Database": { bg: "#d97706", border: "#fbbf24", glow: "rgba(251, 191, 36, 0.4)" },
      "Hardware / Sensor": { bg: "#dc2626", border: "#f87171", glow: "rgba(248, 113, 113, 0.4)" },
      "Service / Cache": { bg: "#0d9488", border: "#2dd4bf", glow: "rgba(45, 212, 191, 0.4)" },
      "Default": { bg: "#475569", border: "#94a3b8", glow: "rgba(148, 163, 184, 0.4)" }
    };

    this.setupEvents();
    this.handleResize();
    this.startAnimation();
  }

  setData(dnaData) {
    if (!dnaData) return;
    this.nodes = (dnaData.nodes || []).map(n => ({
      ...n,
      width: 190,
      height: 90,
      x: (n.position && n.position.x) ? n.position.x : 120,
      y: (n.position && n.position.y) ? n.position.y : 140
    }));
    this.edges = dnaData.edges || [];
    this.selectedNodeId = null;
    this.fitToScreen();
  }

  handleResize() {
    const parent = this.canvas.parentElement;
    if (!parent) return;
    const dpr = window.devicePixelRatio || 1;
    this.width = parent.clientWidth;
    this.height = parent.clientHeight;
    this.canvas.width = this.width * dpr;
    this.canvas.height = this.height * dpr;
    this.ctx.resetTransform ? this.ctx.resetTransform() : this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    this.ctx.scale(dpr, dpr);
  }

  setupEvents() {
    window.addEventListener('resize', () => this.handleResize());

    // Mouse drag pan
    this.canvas.addEventListener('mousedown', (e) => {
      const hit = this.hitTest(e.offsetX, e.offsetY);
      if (hit) {
        this.selectedNodeId = hit.id;
        this.onNodeSelect(hit);
        return;
      }
      this.isDragging = true;
      this.dragStartX = e.clientX - this.panX;
      this.dragStartY = e.clientY - this.panY;
    });

    window.addEventListener('mousemove', (e) => {
      if (this.isDragging) {
        this.panX = e.clientX - this.dragStartX;
        this.panY = e.clientY - this.dragStartY;
      } else {
        const rect = this.canvas.getBoundingClientRect();
        if (
          e.clientX >= rect.left && e.clientX <= rect.right &&
          e.clientY >= rect.top && e.clientY <= rect.bottom
        ) {
          const hit = this.hitTest(e.clientX - rect.left, e.clientY - rect.top);
          this.hoveredNodeId = hit ? hit.id : null;
          this.canvas.style.cursor = hit ? 'pointer' : (this.isDragging ? 'grabbing' : 'grab');
        }
      }
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
    });

    // Zoom on wheel
    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = 1.08;
      const mouseX = e.offsetX;
      const mouseY = e.offsetY;

      let newScale = e.deltaY < 0 ? this.scale * zoomFactor : this.scale / zoomFactor;
      newScale = Math.min(Math.max(0.3, newScale), 2.5);

      this.panX = mouseX - (mouseX - this.panX) * (newScale / this.scale);
      this.panY = mouseY - (mouseY - this.panY) * (newScale / this.scale);
      this.scale = newScale;
      this.updateZoomDisplay();
    }, { passive: false });
  }

  zoomIn() {
    this.scale = Math.min(2.5, this.scale * 1.2);
    this.updateZoomDisplay();
  }

  zoomOut() {
    this.scale = Math.max(0.3, this.scale / 1.2);
    this.updateZoomDisplay();
  }

  resetZoom() {
    this.scale = 1.0;
    this.panX = 60;
    this.panY = 60;
    this.updateZoomDisplay();
  }

  fitToScreen() {
    if (this.nodes.length === 0) return;
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    this.nodes.forEach(n => {
      minX = Math.min(minX, n.x);
      minY = Math.min(minY, n.y);
      maxX = Math.max(maxX, n.x + n.width);
      maxY = Math.max(maxY, n.y + n.height);
    });

    const graphWidth = maxX - minX + 120;
    const graphHeight = maxY - minY + 120;
    const scaleX = (this.width || 800) / graphWidth;
    const scaleY = (this.height || 600) / graphHeight;
    this.scale = Math.min(Math.max(Math.min(scaleX, scaleY), 0.5), 1.2);

    this.panX = ((this.width || 800) - (maxX + minX) * this.scale) / 2;
    this.panY = ((this.height || 600) - (maxY + minY) * this.scale) / 2;
    this.updateZoomDisplay();
  }

  updateZoomDisplay() {
    const el = document.getElementById('canvas-zoom-text');
    if (el) el.textContent = `${Math.round(this.scale * 100)}%`;
  }

  screenToWorld(sx, sy) {
    return {
      x: (sx - this.panX) / this.scale,
      y: (sy - this.panY) / this.scale
    };
  }

  hitTest(sx, sy) {
    const { x, y } = this.screenToWorld(sx, sy);
    for (let i = this.nodes.length - 1; i >= 0; i--) {
      const n = this.nodes[i];
      if (x >= n.x && x <= n.x + n.width && y >= n.y && y <= n.y + n.height) {
        return n;
      }
    }
    return null;
  }

  startAnimation() {
    const renderLoop = () => {
      this.pulseOffset = (this.pulseOffset + 0.015) % 1;
      this.draw();
      this.animationFrameId = requestAnimationFrame(renderLoop);
    };
    this.animationFrameId = requestAnimationFrame(renderLoop);
  }

  draw() {
    const ctx = this.ctx;
    ctx.save();
    ctx.clearRect(0, 0, this.width, this.height);

    // Grid Background
    this.drawGrid(ctx);

    // Apply Camera Transform
    ctx.translate(this.panX, this.panY);
    ctx.scale(this.scale, this.scale);

    // Draw Edges
    this.drawEdges(ctx);

    // Draw Nodes
    this.drawNodes(ctx);

    ctx.restore();
  }

  drawGrid(ctx) {
    const gridSize = 32 * this.scale;
    const offsetX = this.panX % gridSize;
    const offsetY = this.panY % gridSize;

    ctx.strokeStyle = "rgba(255, 255, 255, 0.035)";
    ctx.lineWidth = 1;

    ctx.beginPath();
    for (let x = offsetX; x < this.width; x += gridSize) {
      ctx.moveTo(x, 0);
      ctx.lineTo(x, this.height);
    }
    for (let y = offsetY; y < this.height; y += gridSize) {
      ctx.moveTo(0, y);
      ctx.lineTo(this.width, y);
    }
    ctx.stroke();
  }

  drawEdges(ctx) {
    const nodeMap = new Map();
    this.nodes.forEach(n => nodeMap.set(n.id, n));

    this.edges.forEach(edge => {
      const source = nodeMap.get(edge.from);
      const target = nodeMap.get(edge.to);
      if (!source || !target) return;

      const sx = source.x + source.width;
      const sy = source.y + source.height / 2;
      const tx = target.x;
      const ty = target.y + target.height / 2;

      const dx = tx - sx;
      const cx1 = sx + Math.max(dx * 0.45, 40);
      const cy1 = sy;
      const cx2 = tx - Math.max(dx * 0.45, 40);
      const cy2 = ty;

      // Base Edge Line
      ctx.beginPath();
      ctx.moveTo(sx, sy);
      ctx.bezierCurveTo(cx1, cy1, cx2, cy2, tx, ty);
      ctx.strokeStyle = edge.animated ? "rgba(0, 240, 255, 0.35)" : "rgba(100, 116, 139, 0.35)";
      ctx.lineWidth = 2;
      ctx.stroke();

      // Flow Particles along bezier
      if (edge.animated !== false) {
        for (let i = 0; i < 2; i++) {
          const t = (this.pulseOffset + i * 0.5) % 1;
          const pt = this.getBezierPoint(sx, sy, cx1, cy1, cx2, cy2, tx, ty, t);
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, 3, 0, Math.PI * 2);
          ctx.fillStyle = "#00f0ff";
          ctx.shadowColor = "#00f0ff";
          ctx.shadowBlur = 8;
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      }

      // Edge Label
      if (edge.label) {
        const mid = this.getBezierPoint(sx, sy, cx1, cy1, cx2, cy2, tx, ty, 0.5);
        ctx.font = "10px JetBrains Mono, monospace";
        ctx.fillStyle = "#94a3b8";
        ctx.textAlign = "center";
        ctx.fillText(edge.label, mid.x, mid.y - 7);
      }
    });
  }

  getBezierPoint(x0, y0, x1, y1, x2, y2, x3, y3, t) {
    const cX = 3 * (x1 - x0);
    const bX = 3 * (x2 - x1) - cX;
    const aX = x3 - x0 - cX - bX;

    const cY = 3 * (y1 - y0);
    const bY = 3 * (y2 - y1) - cY;
    const aY = y3 - y0 - cY - bY;

    const x = ((aX * t + bX) * t + cX) * t + x0;
    const y = ((aY * t + bY) * t + cY) * t + y0;
    return { x, y };
  }

  drawNodes(ctx) {
    this.nodes.forEach(node => {
      const isSelected = node.id === this.selectedNodeId;
      const isHovered = node.id === this.hoveredNodeId;
      const style = this.categoryStyles[node.category] || this.categoryStyles["Default"];

      // Card Background
      ctx.save();
      if (isSelected) {
        ctx.shadowColor = "#00f0ff";
        ctx.shadowBlur = 18;
      } else if (isHovered) {
        ctx.shadowColor = style.border;
        ctx.shadowBlur = 10;
      }

      ctx.fillStyle = "#0f172a";
      ctx.strokeStyle = isSelected ? "#00f0ff" : (isHovered ? style.border : "rgba(51, 65, 85, 0.8)");
      ctx.lineWidth = isSelected ? 2.5 : 1.5;

      this.roundRect(ctx, node.x, node.y, node.width, node.height, 8);
      ctx.fill();
      ctx.stroke();
      ctx.restore();

      // Top Category Header Pill
      ctx.fillStyle = style.bg;
      ctx.beginPath();
      this.roundRect(ctx, node.x + 8, node.y + 8, node.width - 16, 18, 4);
      ctx.fill();

      // Category text
      ctx.fillStyle = "#ffffff";
      ctx.font = "bold 9px Inter, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText((node.category || "Component").toUpperCase(), node.x + node.width / 2, node.y + 20);

      // Node Name
      ctx.fillStyle = "#f8fafc";
      ctx.font = "600 12px Inter, sans-serif";
      ctx.textAlign = "left";
      const nameText = this.truncateText(node.name || "Node", 22);
      ctx.fillText(nameText, node.x + 12, node.y + 46);

      // Layer / Technology Snippet
      ctx.fillStyle = "#94a3b8";
      ctx.font = "10px JetBrains Mono, monospace";
      const techSnippet = (node.technologies && node.technologies[0]) ? node.technologies[0] : (node.layer || "Module");
      ctx.fillText(this.truncateText(techSnippet, 24), node.x + 12, node.y + 64);

      // Port dots (Input / Output)
      ctx.fillStyle = "#00f0ff";
      ctx.beginPath();
      ctx.arc(node.x, node.y + node.height / 2, 4, 0, Math.PI * 2);
      ctx.fill();

      ctx.beginPath();
      ctx.arc(node.x + node.width, node.y + node.height / 2, 4, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  roundRect(ctx, x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
  }

  truncateText(text, maxChars) {
    if (!text) return "";
    return text.length > maxChars ? text.substring(0, maxChars - 2) + "..." : text;
  }
}

window.DNACanvas = DNACanvas;
