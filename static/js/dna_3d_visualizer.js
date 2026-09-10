/**
 * SYNTHEX // 3D DIGITAL DNA HELIX & NEURAL CODONS VISUALIZER
 * Full 3D Perspective Projection, Orbit Controls, Interactive 3D Codons, and Particle Field.
 * Zero external dependencies - 100% offline resilient and high performance.
 */

class DNA3DVisualizer {
  constructor(canvasElement, onNodeSelect) {
    this.canvas = canvasElement;
    this.ctx = canvasElement.getContext('2d');
    this.onNodeSelect = onNodeSelect || (() => {});

    this.nodes = [];
    this.selectedNodeId = null;
    this.hoveredNodeId = null;

    // 3D Camera & Orientation
    this.rotX = 0.25;      // Pitch
    this.rotY = 0.0;       // Yaw
    this.zoom = 1.0;
    this.distance = 700;   // Focal distance
    this.autoRotate = true;
    this.autoRotateSpeed = 0.008;

    // Mouse Interaction
    this.isDragging = false;
    this.lastMouseX = 0;
    this.lastMouseY = 0;

    // 3D Floating Particle Cloud
    this.particles = [];
    this.initParticles(160);

    // Projected 3D objects for hit testing
    this.projectedNodes = [];

    // Helix Configuration
    this.helixRadius = 140;
    this.helixHeight = 600;
    this.helixRungs = 60;
    this.twistCount = 3.5;

    this.setupEvents();
    this.handleResize();
    this.startLoop();
  }

  initParticles(count) {
    this.particles = [];
    for (let i = 0; i < count; i++) {
      this.particles.push({
        x: (Math.random() - 0.5) * 800,
        y: (Math.random() - 0.5) * 800,
        z: (Math.random() - 0.5) * 800,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        vz: (Math.random() - 0.5) * 0.4,
        size: Math.random() * 2 + 1,
        color: Math.random() > 0.5 ? '#00f0ff' : (Math.random() > 0.5 ? '#10b981' : '#ec4899')
      });
    }
  }

  setData(dnaData) {
    if (!dnaData) return;
    const rawNodes = dnaData.nodes || [];
    this.nodes = rawNodes.map((n, idx) => {
      // Map each architectural component to a position along the 3D DNA helix
      const t = (idx / Math.max(rawNodes.length - 1, 1)) * (Math.PI * 2 * this.twistCount) - Math.PI * this.twistCount;
      const y = ((idx / Math.max(rawNodes.length - 1, 1)) - 0.5) * (this.helixHeight * 0.85);
      const isStrandA = idx % 2 === 0;
      const angle = isStrandA ? t : t + Math.PI;

      return {
        ...n,
        codonX: Math.cos(angle) * (this.helixRadius + 30),
        codonY: y,
        codonZ: Math.sin(angle) * (this.helixRadius + 30),
        radius: 28,
        strand: isStrandA ? 'A' : 'B'
      };
    });
  }

  handleResize() {
    const parent = this.canvas.parentElement;
    if (!parent) return;
    const dpr = window.devicePixelRatio || 1;
    this.width = parent.clientWidth || 800;
    this.height = parent.clientHeight || 600;
    this.canvas.width = this.width * dpr;
    this.canvas.height = this.height * dpr;
    this.ctx.resetTransform ? this.ctx.resetTransform() : this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    this.ctx.scale(dpr, dpr);
  }

  setupEvents() {
    window.addEventListener('resize', () => this.handleResize());

    this.canvas.addEventListener('mousedown', (e) => {
      const hit = this.hitTest(e.offsetX, e.offsetY);
      if (hit) {
        this.selectedNodeId = hit.id;
        this.onNodeSelect(hit);
        return;
      }
      this.isDragging = true;
      this.lastMouseX = e.clientX;
      this.lastMouseY = e.clientY;
    });

    window.addEventListener('mousemove', (e) => {
      if (this.isDragging) {
        const dx = e.clientX - this.lastMouseX;
        const dy = e.clientY - this.lastMouseY;
        this.rotY += dx * 0.007;
        this.rotX += dy * 0.007;
        this.rotX = Math.max(-Math.PI / 2.2, Math.min(Math.PI / 2.2, this.rotX));
        this.lastMouseX = e.clientX;
        this.lastMouseY = e.clientY;
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

    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
      this.zoom = Math.max(0.4, Math.min(2.5, this.zoom * zoomFactor));
    }, { passive: false });
  }

  toggleAutoRotate() {
    this.autoRotate = !this.autoRotate;
    return this.autoRotate;
  }

  resetView() {
    this.rotX = 0.25;
    this.rotY = 0.0;
    this.zoom = 1.0;
  }

  // 3D Point Projection
  project(x, y, z) {
    // 1. Rotation around Y axis (Yaw)
    const cosY = Math.cos(this.rotY);
    const sinY = Math.sin(this.rotY);
    const x1 = x * cosY + z * sinY;
    const y1 = y;
    const z1 = -x * sinY + z * cosY;

    // 2. Rotation around X axis (Pitch)
    const cosX = Math.cos(this.rotX);
    const sinX = Math.sin(this.rotX);
    const x2 = x1;
    const y2 = y1 * cosX - z1 * sinX;
    const z2 = y1 * sinX + z1 * cosX;

    // 3. Perspective Projection
    const distance = this.distance / this.zoom;
    const fov = 450;
    const scale = fov / (distance + z2);

    return {
      x: this.width / 2 + x2 * scale,
      y: this.height / 2 + y2 * scale,
      z: z2,
      scale: scale,
      visible: z2 > -distance
    };
  }

  hitTest(sx, sy) {
    for (let i = this.projectedNodes.length - 1; i >= 0; i--) {
      const pn = this.projectedNodes[i];
      const dx = sx - pn.proj.x;
      const dy = sy - pn.proj.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist <= pn.radius * pn.proj.scale) {
        return pn.node;
      }
    }
    return null;
  }

  startLoop() {
    const loop = () => {
      if (this.autoRotate && !this.isDragging) {
        this.rotY += this.autoRotateSpeed;
      }
      this.updateParticles();
      this.render();
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  updateParticles() {
    this.particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      p.z += p.vz;
      if (p.x > 400) p.x = -400;
      if (p.x < -400) p.x = 400;
      if (p.y > 400) p.y = -400;
      if (p.y < -400) p.y = 400;
      if (p.z > 400) p.z = -400;
      if (p.z < -400) p.z = 400;
    });
  }

  render() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.width, this.height);

    // Deep sci-fi radial background
    const bgGrad = ctx.createRadialGradient(
      this.width / 2, this.height / 2, 50,
      this.width / 2, this.height / 2, Math.max(this.width, this.height) * 0.7
    );
    bgGrad.addColorStop(0, '#0a1324');
    bgGrad.addColorStop(0.6, '#060a12');
    bgGrad.addColorStop(1, '#020408');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, this.width, this.height);

    // Render 3D Background Particles
    this.renderParticles(ctx);

    // Render 3D Double Helix Backbone & Hydrogen Bonds
    this.renderHelix(ctx);

    // Render 3D Architectural Component Codons
    this.renderCodonNodes(ctx);
  }

  renderParticles(ctx) {
    this.particles.forEach(p => {
      const proj = this.project(p.x, p.y, p.z);
      if (!proj.visible) return;

      const alpha = Math.max(0.1, Math.min(0.8, 1 - (proj.z / 600)));
      ctx.beginPath();
      ctx.arc(proj.x, proj.y, p.size * proj.scale, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = alpha * 0.6;
      ctx.fill();
      ctx.globalAlpha = 1.0;
    });
  }

  renderHelix(ctx) {
    const rungs = this.helixRungs;
    const height = this.helixHeight;
    const radius = this.helixRadius;
    const twist = this.twistCount;

    let prevA = null;
    let prevB = null;

    // Collect 3D rung segments to depth-sort them
    const renderList = [];

    for (let i = 0; i <= rungs; i++) {
      const ratio = i / rungs;
      const angle = ratio * Math.PI * 2 * twist;
      const y = (ratio - 0.5) * height;

      const ax = Math.cos(angle) * radius;
      const ay = y;
      const az = Math.sin(angle) * radius;

      const bx = Math.cos(angle + Math.PI) * radius;
      const by = y;
      const bz = Math.sin(angle + Math.PI) * radius;

      const projA = this.project(ax, ay, az);
      const projB = this.project(bx, by, bz);

      if (projA.visible && projB.visible) {
        const avgZ = (projA.z + projB.z) / 2;
        renderList.push({
          type: 'rung',
          z: avgZ,
          a: projA,
          b: projB,
          ratio: ratio
        });
      }

      if (prevA && prevB && projA.visible && projB.visible) {
        renderList.push({
          type: 'strandA',
          z: (prevA.z + projA.z) / 2,
          p1: prevA,
          p2: projA
        });
        renderList.push({
          type: 'strandB',
          z: (prevB.z + projB.z) / 2,
          p1: prevB,
          p2: projB
        });
      }

      prevA = projA;
      prevB = projB;
    }

    // Depth sort back to front
    renderList.sort((a, b) => b.z - a.z);

    renderList.forEach(item => {
      if (item.type === 'rung') {
        // Base pair connecting bar
        ctx.beginPath();
        ctx.moveTo(item.a.x, item.a.y);
        ctx.lineTo(item.b.x, item.b.y);
        ctx.strokeStyle = item.ratio > 0.5 ? 'rgba(0, 240, 255, 0.45)' : 'rgba(16, 185, 129, 0.45)';
        ctx.lineWidth = Math.max(1, 2.5 * item.a.scale);
        ctx.stroke();

        // Glowing nucleotide midpoint
        const midX = (item.a.x + item.b.x) / 2;
        const midY = (item.a.y + item.b.y) / 2;
        ctx.beginPath();
        ctx.arc(midX, midY, 3 * item.a.scale, 0, Math.PI * 2);
        ctx.fillStyle = '#f59e0b';
        ctx.fill();

      } else if (item.type === 'strandA') {
        ctx.beginPath();
        ctx.moveTo(item.p1.x, item.p1.y);
        ctx.lineTo(item.p2.x, item.p2.y);
        ctx.strokeStyle = '#00f0ff';
        ctx.lineWidth = Math.max(1.5, 3.5 * item.p1.scale);
        ctx.shadowColor = '#00f0ff';
        ctx.shadowBlur = 8 * item.p1.scale;
        ctx.stroke();
        ctx.shadowBlur = 0;

      } else if (item.type === 'strandB') {
        ctx.beginPath();
        ctx.moveTo(item.p1.x, item.p1.y);
        ctx.lineTo(item.p2.x, item.p2.y);
        ctx.strokeStyle = '#ec4899';
        ctx.lineWidth = Math.max(1.5, 3.5 * item.p1.scale);
        ctx.shadowColor = '#ec4899';
        ctx.shadowBlur = 8 * item.p1.scale;
        ctx.stroke();
        ctx.shadowBlur = 0;
      }
    });
  }

  renderCodonNodes(ctx) {
    this.projectedNodes = [];

    // Category colors
    const categoryColors = {
      "Client / UI": "#38bdf8",
      "API Gateway": "#a78bfa",
      "Core Logic": "#60a5fa",
      "AI / ML Core": "#34d399",
      "Storage / Database": "#fbbf24",
      "Hardware / Sensor": "#f87171",
      "Service / Cache": "#2dd4bf"
    };

    // Calculate projected 3D coordinates for each component codon
    const sortedCodons = this.nodes.map(n => {
      const proj = this.project(n.codonX, n.codonY, n.codonZ);
      return { node: n, proj: proj, radius: n.radius };
    }).filter(item => item.proj.visible);

    // Depth sort codons
    sortedCodons.sort((a, b) => b.proj.z - a.proj.z);
    this.projectedNodes = sortedCodons;

    sortedCodons.forEach(item => {
      const n = item.node;
      const p = item.proj;
      const isSelected = n.id === this.selectedNodeId;
      const isHovered = n.id === this.hoveredNodeId;
      const color = categoryColors[n.category] || "#00f0ff";
      const r = item.radius * p.scale;

      ctx.save();

      // Connector from helix axis to codon sphere
      ctx.beginPath();
      const axisProj = this.project(0, n.codonY, 0);
      ctx.moveTo(axisProj.x, axisProj.y);
      ctx.lineTo(p.x, p.y);
      ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
      ctx.lineWidth = 1;
      ctx.setLineDash([2, 4]);
      ctx.stroke();
      ctx.setLineDash([]);

      // Outer Aura / Glow
      if (isSelected || isHovered) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, r * 1.5, 0, Math.PI * 2);
        ctx.fillStyle = isSelected ? "rgba(0, 240, 255, 0.25)" : "rgba(16, 185, 129, 0.25)";
        ctx.fill();
      }

      // 3D Codon Sphere with radial gradient shading
      const sphereGrad = ctx.createRadialGradient(
        p.x - r * 0.3, p.y - r * 0.3, r * 0.1,
        p.x, p.y, r
      );
      sphereGrad.addColorStop(0, '#ffffff');
      sphereGrad.addColorStop(0.3, color);
      sphereGrad.addColorStop(0.8, '#0f172a');
      sphereGrad.addColorStop(1, '#020617');

      ctx.beginPath();
      ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
      ctx.fillStyle = sphereGrad;
      ctx.shadowColor = color;
      ctx.shadowBlur = (isSelected ? 20 : (isHovered ? 12 : 6)) * p.scale;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Outer Ring
      ctx.beginPath();
      ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
      ctx.strokeStyle = isSelected ? '#00f0ff' : color;
      ctx.lineWidth = isSelected ? 3 : 1.5;
      ctx.stroke();

      // Label Tag
      const fontSize = Math.max(10, Math.round(12 * p.scale));
      ctx.font = `600 ${fontSize}px Inter, sans-serif`;
      ctx.fillStyle = '#f8fafc';
      ctx.textAlign = 'center';
      ctx.fillText(n.name, p.x, p.y + r + fontSize + 2);

      // Category Pill below label
      ctx.font = `bold ${Math.max(8, Math.round(9 * p.scale))}px Inter, sans-serif`;
      ctx.fillStyle = color;
      ctx.fillText((n.category || 'Component').toUpperCase(), p.x, p.y + r + fontSize * 2 + 3);

      ctx.restore();
    });
  }
}

window.DNA3DVisualizer = DNA3DVisualizer;
