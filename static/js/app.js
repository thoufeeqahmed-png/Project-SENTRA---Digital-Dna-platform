/**
 * SYNTHEX // PROJECT DNA MATRIX // WORKSPACE CONTROLLER V2
 * Full 3D Holographic Helix Visualizer + 2D Architecture Canvas + 5-Phase Interactive Plan.
 */

// Define global app object early so inline onclick handlers always work
window.SynthexApp = {
  currentProject: null,
  dnaCanvas: null,
  dna3d: null,
  voiceEngine: null,
  switchToTab: function(tabId) {
    document.querySelectorAll(".tab-btn").forEach(t => {
      t.classList.toggle("active", t.dataset.target === tabId);
    });
    document.querySelectorAll(".tab-view").forEach(v => {
      v.classList.toggle("active", v.id === tabId);
    });
    if (tabId === "view-dna-canvas" && window.SynthexApp.dnaCanvas) {
      setTimeout(() => window.SynthexApp.dnaCanvas.handleResize(), 50);
    }
    if (tabId === "view-dna-3d" && window.SynthexApp.dna3d) {
      setTimeout(() => window.SynthexApp.dna3d.handleResize(), 50);
    }
  },
  analyzeProject: null,
  sendChatMessage: null,
  loadProject: null,
  openInspector: null
};

document.addEventListener("DOMContentLoaded", () => {
  // Settings in LocalStorage
  let settings = {
    apiKey: localStorage.getItem("dna_api_key") || "",
    provider: localStorage.getItem("dna_provider") || "gemini",
    voiceOut: localStorage.getItem("dna_voice_out") !== "false"
  };

  // DOM Elements
  const canvas3dEl = document.getElementById("dna-3d-canvas-element");
  const canvas2dEl = document.getElementById("dna-canvas-element");
  const ideaInput = document.getElementById("idea-input");
  const analyzeBtn = document.getElementById("btn-analyze");
  const voiceIdeaBtn = document.getElementById("btn-voice-idea");
  const projectListEl = document.getElementById("project-list");
  const activeTitleEl = document.getElementById("active-project-title");
  const activeCategoryEl = document.getElementById("active-project-category");

  // Inspector Drawer
  const inspectorEl = document.getElementById("node-inspector");
  const inspectorCloseBtn = document.getElementById("btn-close-inspector");
  const inspectorName = document.getElementById("inspector-node-name");
  const inspectorCategory = document.getElementById("inspector-node-category");
  const inspectorDesc = document.getElementById("inspector-node-desc");
  const inspectorInputs = document.getElementById("inspector-inputs");
  const inspectorOutputs = document.getElementById("inspector-outputs");
  const inspectorTech = document.getElementById("inspector-technologies");

  // Chat Elements
  const chatHistoryEl = document.getElementById("chat-history");
  const chatInput = document.getElementById("chat-input");
  const chatSendBtn = document.getElementById("btn-send-chat");
  const chatVoiceBtn = document.getElementById("btn-voice-chat");
  const waveCanvasEl = document.getElementById("voice-wave-canvas");
  const toggleVoiceOutBtn = document.getElementById("btn-toggle-voice-out");

  // Settings Modal
  const settingsModal = document.getElementById("settings-modal");
  const btnOpenSettings = document.getElementById("btn-open-settings");
  const btnCloseSettings = document.getElementById("btn-close-settings");
  const btnSaveSettings = document.getElementById("btn-save-settings");
  const inputApiKey = document.getElementById("settings-api-key");
  const selectProvider = document.getElementById("settings-provider");

  // Export Buttons
  const btnExportJson = document.getElementById("btn-export-json");
  const btnExportMd = document.getElementById("btn-export-md");

  // 1. Initialize 3D Visualizer
  try {
    if (canvas3dEl && typeof DNA3DVisualizer !== 'undefined') {
      window.SynthexApp.dna3d = new DNA3DVisualizer(canvas3dEl, (selectedNode) => {
        openInspector(selectedNode);
      });

      document.getElementById("btn-3d-autorotate")?.addEventListener("click", () => {
        const isSpinning = window.SynthexApp.dna3d.toggleAutoRotate();
        const btn = document.getElementById("btn-3d-autorotate");
        if (btn) btn.innerHTML = `<span class="status-dot"></span> ${isSpinning ? 'Auto-Spin: ON' : 'Auto-Spin: OFF'}`;
      });

      document.getElementById("btn-3d-reset")?.addEventListener("click", () => {
        window.SynthexApp.dna3d.resetView();
      });
    }
  } catch (err) {
    console.warn("3D Visualizer init warning:", err);
  }

  // 2. Initialize 2D Architecture Canvas
  try {
    if (canvas2dEl && typeof DNACanvas !== 'undefined') {
      window.SynthexApp.dnaCanvas = new DNACanvas(canvas2dEl, (selectedNode) => {
        openInspector(selectedNode);
      });

      document.getElementById("btn-zoom-in")?.addEventListener("click", () => window.SynthexApp.dnaCanvas?.zoomIn());
      document.getElementById("btn-zoom-out")?.addEventListener("click", () => window.SynthexApp.dnaCanvas?.zoomOut());
      document.getElementById("btn-zoom-reset")?.addEventListener("click", () => window.SynthexApp.dnaCanvas?.resetZoom());
      document.getElementById("btn-zoom-fit")?.addEventListener("click", () => window.SynthexApp.dnaCanvas?.fitToScreen());
    }
  } catch (err) {
    console.warn("2D Canvas init warning:", err);
  }

  // 3. Initialize Voice Engine
  try {
    if (typeof VoiceInterface !== 'undefined') {
      window.SynthexApp.voiceEngine = new VoiceInterface({
        waveCanvas: waveCanvasEl,
        onTranscript: (text) => {
          if (document.activeElement === chatInput) {
            chatInput.value = text;
            sendChatMessage();
          } else {
            if (ideaInput) ideaInput.value = text;
            analyzeProject();
          }
        },
        onStatusChange: (status) => {
          if (voiceIdeaBtn) voiceIdeaBtn.classList.toggle("recording", status.isListening);
          if (chatVoiceBtn) chatVoiceBtn.classList.toggle("recording", status.isListening);
        }
      });
      window.SynthexApp.voiceEngine.voiceOutputEnabled = settings.voiceOut;
    }
  } catch (err) {
    console.warn("Voice Engine init warning:", err);
  }

  // Voice Toggle Button
  if (toggleVoiceOutBtn) {
    updateVoiceToggleIcon();
    toggleVoiceOutBtn.addEventListener("click", () => {
      settings.voiceOut = !settings.voiceOut;
      localStorage.setItem("dna_voice_out", settings.voiceOut);
      if (window.SynthexApp.voiceEngine) {
        window.SynthexApp.voiceEngine.voiceOutputEnabled = settings.voiceOut;
      }
      updateVoiceToggleIcon();
    });
  }

  function updateVoiceToggleIcon() {
    if (!toggleVoiceOutBtn) return;
    toggleVoiceOutBtn.innerHTML = settings.voiceOut
      ? `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg> Voice On`
      : `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line></svg> Muted`;
  }

  // Voice Input Buttons
  voiceIdeaBtn?.addEventListener("click", () => window.SynthexApp.voiceEngine?.toggleListening());
  chatVoiceBtn?.addEventListener("click", () => window.SynthexApp.voiceEngine?.toggleListening());

  // Tab Switching via Event Listeners
  document.querySelectorAll(".tab-btn").forEach(tab => {
    tab.addEventListener("click", () => {
      window.SynthexApp.switchToTab(tab.dataset.target);
    });
  });

  // Direct Jump to Build Plan from Header, Canvas Banner, & Node Inspector
  document.getElementById("btn-quick-view-plan")?.addEventListener("click", () => {
    window.SynthexApp.switchToTab("view-build-plan");
  });
  document.getElementById("btn-banner-open-plan")?.addEventListener("click", () => {
    window.SynthexApp.switchToTab("view-build-plan");
  });
  document.getElementById("btn-inspector-view-plan")?.addEventListener("click", () => {
    window.SynthexApp.switchToTab("view-build-plan");
  });
  document.getElementById("btn-download-plan-md")?.addEventListener("click", () => {
    if (!window.SynthexApp.currentProject) return alert("Select or synthesize a project first.");
    window.location.href = `/api/project/${window.SynthexApp.currentProject.id}/export/?format=markdown`;
  });

  // Project Idea Submit
  analyzeBtn?.addEventListener("click", () => analyzeProject());
  ideaInput?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") analyzeProject();
  });

  async function analyzeProject() {
    const text = ideaInput ? ideaInput.value.trim() : "";
    if (!text) return;

    if (analyzeBtn) {
      analyzeBtn.disabled = true;
      analyzeBtn.innerHTML = `<span class="status-dot"></span> Synthesizing DNA...`;
    }

    try {
      const resp = await fetch("/api/project/analyze/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          idea: text,
          api_key: settings.apiKey,
          provider: settings.provider
        })
      });

      const res = await resp.json();
      if (res.success && res.project) {
        if (ideaInput) ideaInput.value = "";
        loadProject(res.project);
        loadProjectHistory();
        // Robot Voice Announcement
        const introMsg = `[AI DROID IDENT: THOUFEEQ-01] Digital DNA and 5-Phase Engineering Build Plan synthesized for ${res.project.title}.`;
        window.SynthexApp.voiceEngine?.speak(introMsg);
      } else {
        alert(res.error || "Failed to synthesize project DNA.");
      }
    } catch (err) {
      console.error("Analysis error:", err);
      alert("Encountered connection error while synthesizing architecture.");
    } finally {
      if (analyzeBtn) {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = `Synthesize DNA`;
      }
    }
  }
  window.SynthexApp.analyzeProject = analyzeProject;

  // Load and Render Project
  function loadProject(project) {
    if (!project) return;
    window.SynthexApp.currentProject = project;

    // Update Header Meta
    if (activeTitleEl) activeTitleEl.textContent = project.title;
    if (activeCategoryEl) activeCategoryEl.textContent = project.category || "Architecture";

    // Set 3D Helix Visualizer Data
    if (window.SynthexApp.dna3d && project.dna_data) {
      window.SynthexApp.dna3d.setData(project.dna_data);
    }

    // Set 2D Canvas Data
    if (window.SynthexApp.dnaCanvas && project.dna_data) {
      window.SynthexApp.dnaCanvas.setData(project.dna_data);
    }

    // Populate Build Plan Tab (5-Phase Production Plan)
    renderBuildPlanTab(project);

    // Populate Feasibility Matrix Tab
    renderFeasibilityTab(project);

    // Populate Data Structures & Schema Tab
    renderDataStructuresTab(project);

    // Populate Risks Tab
    renderRisksTab(project);

    // Populate Chat messages
    renderChatMessages(project.messages || []);

    // Highlight active in sidebar
    document.querySelectorAll(".project-item").forEach(item => {
      item.classList.toggle("active", parseInt(item.dataset.id) === project.id);
    });
  }
  window.SynthexApp.loadProject = loadProject;

  function renderBuildPlanTab(p) {
    const timelineEl = document.getElementById("timeline-phases-container");
    if (!timelineEl) return;
    const plan = p.build_plan || [];

    timelineEl.innerHTML = plan.map((phase, pIdx) => {
      const deliverables = phase.deliverables || [];
      const cmds = phase.commands || "";
      return `
        <div class="timeline-phase">
          <div class="phase-header">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="phase-title">${phase.phase}</span>
              <span class="tag tag-cyan" style="font-size: 10px;">${phase.status || 'Active Phase'}</span>
            </div>
            <div class="phase-duration">${phase.duration}</div>
          </div>
          <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 12px; line-height: 1.5;">${phase.focus}</p>
          
          <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px;">
            Actionable Engineering Deliverables (${deliverables.length})
          </div>
          <div style="display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px;">
            ${deliverables.map((d, dIdx) => `
              <label class="task-checkbox-item" id="task-item-${pIdx}-${dIdx}">
                <input type="checkbox" class="task-cb" data-phase="${pIdx}" data-task="${dIdx}">
                <span style="font-size: 12px; color: var(--text-primary);">${d}</span>
              </label>
            `).join("")}
          </div>

          ${cmds ? `
            <div class="code-scaffold-box">
              <div class="code-scaffold-header">
                <span>Phase Scaffolding & Setup Commands</span>
                <span style="cursor: pointer; color: var(--accent-cyan);" onclick="navigator.clipboard.writeText(this.parentElement.nextElementSibling.textContent); this.textContent='Copied!'; setTimeout(()=>this.textContent='Copy', 1500);">Copy</span>
              </div>
              <pre style="margin: 0; font-family: inherit; font-size: 11px; color: #38bdf8;"><code>${cmds}</code></pre>
            </div>
          ` : ''}
        </div>
      `;
    }).join("");

    // Setup interactive task checkboxes with real-time progress tracker
    const allCbs = document.querySelectorAll(".task-cb");
    function updateProgress() {
      const total = allCbs.length;
      let checkedCount = 0;
      allCbs.forEach(cb => {
        const item = cb.closest(".task-checkbox-item");
        if (cb.checked) {
          checkedCount++;
          item?.classList.add("completed");
        } else {
          item?.classList.remove("completed");
        }
      });
      const pct = total > 0 ? Math.round((checkedCount / total) * 100) : 0;
      const progressText = document.getElementById("checklist-progress-text");
      const progressBar = document.getElementById("checklist-progress-bar");
      if (progressText) progressText.textContent = `${checkedCount} of ${total} Completed (${pct}%)`;
      if (progressBar) progressBar.style.width = `${pct}%`;
    }

    allCbs.forEach(cb => {
      cb.addEventListener("change", updateProgress);
    });
    updateProgress();
  }

  function renderFeasibilityTab(p) {
    const scoreValEl = document.getElementById("feasibility-score-val");
    if (scoreValEl) scoreValEl.textContent = `${p.feasibility_score || 85}%`;

    const summaryEl = document.getElementById("feasibility-summary-text");
    if (summaryEl) summaryEl.textContent = p.feasibility_summary || "Calculated architectural feasibility breakdown.";

    const breakdown = p.feasibility_breakdown || {};
    const metricsContainer = document.getElementById("feasibility-metrics-list");
    if (metricsContainer) {
      metricsContainer.innerHTML = Object.entries(breakdown).map(([k, v]) => `
        <div class="metric-row">
          <div class="metric-header">
            <span style="text-transform: capitalize; color: var(--text-primary);">${k.replace(/_/g, " ")}</span>
            <span style="font-family: var(--font-mono); color: var(--accent-cyan);">${v}%</span>
          </div>
          <div class="progress-track">
            <div class="progress-bar" style="width: ${v}%"></div>
          </div>
        </div>
      `).join("");
    }

    // Tech Stack Badges
    const techEl = document.getElementById("feasibility-tech-stack");
    if (techEl && p.tech_stack) {
      const items = [
        ...(p.tech_stack.software || []),
        ...(p.tech_stack.hardware || []),
        ...(p.tech_stack.databases || [])
      ];
      techEl.innerHTML = items.map(t => `<span class="tag tag-cyan">${t}</span>`).join("");
    }
  }

  function renderDataStructuresTab(p) {
    const container = document.getElementById("data-structures-container");
    if (!container) return;
    const ds = (p.dna_data && p.dna_data.data_structures) || [];
    if (ds.length === 0) {
      container.innerHTML = `<p style="color: var(--text-muted);">Standard protocol serialization in use.</p>`;
      return;
    }
    container.innerHTML = ds.map(model => `
      <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 18px; margin-bottom: 14px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
          <span style="font-weight: 700; font-size: 14px; font-family: var(--font-mono); color: var(--accent-cyan);">${model.name}</span>
          <span class="tag">${model.type || "Schema"}</span>
        </div>
        <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
          <thead>
            <tr style="border-bottom: 1px solid var(--border-subtle); color: var(--text-muted); text-align: left;">
              <th style="padding: 6px 0;">Field</th>
              <th style="padding: 6px 0;">Type</th>
              <th style="padding: 6px 0;">Description</th>
            </tr>
          </thead>
          <tbody>
            ${(model.fields || []).map(f => `
              <tr style="border-bottom: 1px solid rgba(255,255,255,0.03);">
                <td style="padding: 6px 0; font-family: var(--font-mono); color: var(--text-primary);">${f.field}</td>
                <td style="padding: 6px 0; color: var(--accent-emerald); font-family: var(--font-mono); font-size: 11px;">${f.type}</td>
                <td style="padding: 6px 0; color: var(--text-secondary);">${f.description || ""}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `).join("");
  }

  function renderRisksTab(p) {
    const container = document.getElementById("risks-container");
    if (!container) return;
    const risks = p.risks_mitigations || [];
    container.innerHTML = risks.map(r => `
      <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 18px; margin-bottom: 14px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
          <span style="font-weight: 700; font-size: 13px; color: var(--text-primary);">${r.risk}</span>
          <span class="tag" style="background: rgba(244, 63, 94, 0.15); color: var(--accent-rose); border-color: rgba(244, 63, 94, 0.3);">${r.severity} Severity</span>
        </div>
        <p style="font-size: 12px; color: var(--text-secondary); margin-bottom: 10px;"><strong>Impact:</strong> ${r.impact || ""}</p>
        <div style="background: var(--bg-surface-elevated); padding: 10px; border-radius: var(--radius-sm); font-size: 12px; border-left: 3px solid var(--accent-emerald);">
          <strong style="color: var(--accent-emerald);">Mitigation Strategy:</strong> ${r.mitigation}
        </div>
      </div>
    `).join("");
  }

  // Node Inspector Drawer
  function openInspector(node) {
    if (!inspectorEl || !node) return;
    if (inspectorName) inspectorName.textContent = node.name || "Component";
    if (inspectorCategory) inspectorCategory.textContent = node.category || "Module";
    if (inspectorDesc) inspectorDesc.textContent = node.description || "Component architecture layer.";

    if (inspectorInputs) {
      inspectorInputs.innerHTML = (node.inputs || []).map(i => `<span class="tag">${i}</span>`).join("") || `<span class="tag">Standard Ingestion</span>`;
    }
    if (inspectorOutputs) {
      inspectorOutputs.innerHTML = (node.outputs || []).map(o => `<span class="tag">${o}</span>`).join("") || `<span class="tag">Processed Stream</span>`;
    }
    if (inspectorTech) {
      inspectorTech.innerHTML = (node.technologies || []).map(t => `<span class="tag tag-cyan">${t}</span>`).join("");
    }

    inspectorEl.classList.add("open");
  }
  window.SynthexApp.openInspector = openInspector;

  inspectorCloseBtn?.addEventListener("click", () => {
    inspectorEl?.classList.remove("open");
  });

  // Chat Interface
  chatSendBtn?.addEventListener("click", () => sendChatMessage());
  chatInput?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendChatMessage();
  });

  async function sendChatMessage() {
    const msg = chatInput ? chatInput.value.trim() : "";
    if (!msg) return;

    if (chatInput) chatInput.value = "";
    appendChatMessage("user", msg);

    try {
      const resp = await fetch("/api/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: msg,
          project_id: window.SynthexApp.currentProject ? window.SynthexApp.currentProject.id : null,
          api_key: settings.apiKey,
          provider: settings.provider
        })
      });
      const data = await resp.json();
      if (data.success && data.reply) {
        appendChatMessage("assistant", data.reply);
        window.SynthexApp.voiceEngine?.speak(data.reply);
      } else {
        appendChatMessage("assistant", "I encountered an error processing your query.");
      }
    } catch (e) {
      appendChatMessage("assistant", "Connection error. Please verify server status.");
    }
  }
  window.SynthexApp.sendChatMessage = sendChatMessage;

  function appendChatMessage(role, text) {
    if (!chatHistoryEl) return;
    const bubble = document.createElement("div");
    bubble.className = `message-bubble message-${role}`;
    bubble.innerHTML = `
      <div>${text}</div>
      <div class="message-meta">${role === "assistant" ? "Thoufeeq Ahmed AI Droid" : "You"}</div>
    `;
    chatHistoryEl.appendChild(bubble);
    chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
  }

  function renderChatMessages(messages) {
    if (!chatHistoryEl) return;
    chatHistoryEl.innerHTML = "";
    if (!messages || messages.length === 0) {
      appendChatMessage("assistant", "[AI DROID IDENT: THOUFEEQ-01] I am the AI assistant of Thoufeeq Ahmed. Neural architecture matrices and 3D digital DNA ready.");
      return;
    }
    messages.forEach(m => appendChatMessage(m.role, m.content));
  }

  // Project History List
  async function loadProjectHistory() {
    try {
      const resp = await fetch("/api/projects/");
      const data = await resp.json();
      if (projectListEl && data.projects) {
        projectListEl.innerHTML = data.projects.map(p => `
          <div class="project-item ${window.SynthexApp.currentProject && window.SynthexApp.currentProject.id === p.id ? 'active' : ''}" data-id="${p.id}" onclick="fetch('/api/project/${p.id}/').then(r=>r.json()).then(window.SynthexApp.loadProject)">
            <div class="project-item-title">${p.title}</div>
            <div class="project-item-meta">
              <span>${p.created_at}</span>
              <span class="score-tag">${p.feasibility_score}%</span>
            </div>
          </div>
        `).join("");
      }
    } catch (e) {
      console.warn("Could not load project history:", e);
    }
  }

  // Settings Modal Handlers
  btnOpenSettings?.addEventListener("click", () => {
    if (inputApiKey) inputApiKey.value = settings.apiKey;
    if (selectProvider) selectProvider.value = settings.provider;
    settingsModal?.classList.add("open");
  });

  btnCloseSettings?.addEventListener("click", () => {
    settingsModal?.classList.remove("open");
  });

  btnSaveSettings?.addEventListener("click", () => {
    settings.apiKey = inputApiKey ? inputApiKey.value.trim() : "";
    settings.provider = selectProvider ? selectProvider.value : "gemini";
    localStorage.setItem("dna_api_key", settings.apiKey);
    localStorage.setItem("dna_provider", settings.provider);
    settingsModal?.classList.remove("open");
  });

  // Export Handlers
  btnExportJson?.addEventListener("click", () => {
    if (!window.SynthexApp.currentProject) return alert("Select or synthesize a project first.");
    window.location.href = `/api/project/${window.SynthexApp.currentProject.id}/export/?format=json`;
  });

  btnExportMd?.addEventListener("click", () => {
    if (!window.SynthexApp.currentProject) return alert("Select or synthesize a project first.");
    window.location.href = `/api/project/${window.SynthexApp.currentProject.id}/export/?format=markdown`;
  });

  // Quick Action Chips in Chat
  document.querySelectorAll(".chip-prompt").forEach(chip => {
    chip.addEventListener("click", () => {
      if (chatInput) {
        chatInput.value = chip.dataset.prompt;
        sendChatMessage();
      }
    });
  });

  // Load Initial Project Immediately
  loadProjectHistory().then(async () => {
    try {
      const res = await fetch("/api/project/1/");
      const proj = await res.json();
      if (proj && proj.id) {
        loadProject(proj);
      }
    } catch (e) {
      console.warn("Could not fetch initial project 1:", e);
    }
  });
});
