// --- PixelPress Desktop Pro - Core Client Engine ---

// ─── Session Security & Anti-CSRF Token ───
const AUTH_TOKEN = document.querySelector('meta[name="pixelpress-token"]')?.getAttribute('content') || '';
window.PIXELPRESS_TOKEN = AUTH_TOKEN;

function getAuthHeaders(extraHeaders = {}) {
  const headers = { ...extraHeaders };
  if (AUTH_TOKEN) {
    headers['X-PixelPress-Token'] = AUTH_TOKEN;
  }
  return headers;
}

function withAuthToken(url) {
  if (!AUTH_TOKEN) return url;
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}token=${encodeURIComponent(AUTH_TOKEN)}`;
}

function apiFetch(url, options = {}) {
  const opts = { ...options };
  opts.headers = getAuthHeaders(opts.headers || {});
  return fetch(url, opts);
}

// ─── Zero-Leak Object URL Registry (Lifecycle Management) ───
const activeObjectUrls = new Set();

function createManagedObjectURL(file) {
  const url = URL.createObjectURL(file);
  activeObjectUrls.add(url);
  return url;
}

function revokeAllManagedObjectURLs() {
  activeObjectUrls.forEach(url => {
    try {
      URL.revokeObjectURL(url);
    } catch (_) {}
  });
  activeObjectUrls.clear();
}

// ─── Settings Persistence Engine (localStorage) ───
const PREFS_KEY = 'pixelpress_pro_user_prefs';

function saveUserPreferences() {
  try {
    const prefs = {
      quality: qualitySlider ? qualitySlider.value : 85,
      output_format: document.querySelector('input[name="output_format"]:checked')?.value || 'same',
      resize_mode: resizeMode ? resizeMode.value : 'none',
      resize_value: document.getElementById('resize_value')?.value || 100,
      resize_width: document.getElementById('resize_width')?.value || '',
      resize_height: document.getElementById('resize_height')?.value || '',
      strip_metadata: document.getElementById('strip_metadata')?.checked ?? true,
      lossless: document.getElementById('lossless')?.checked ?? false,
      optimize: document.getElementById('optimize')?.checked ?? true,
    };
    localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
  } catch (_) {}
}

function loadUserPreferences() {
  try {
    const saved = localStorage.getItem(PREFS_KEY);
    if (!saved) return;
    const prefs = JSON.parse(saved);

    if (qualitySlider && prefs.quality !== undefined) {
      qualitySlider.value = prefs.quality;
      if (qualityDisplay) qualityDisplay.textContent = prefs.quality + '%';
      updateSliderBg(qualitySlider);
    }

    if (prefs.output_format) {
      document.querySelectorAll('.fmt-pill').forEach(btn => {
        const input = btn.querySelector('input');
        const match = input && input.value === prefs.output_format;
        btn.classList.toggle('active', match);
        if (input) input.checked = match;
      });
    }

    if (resizeMode && prefs.resize_mode) {
      resizeMode.value = prefs.resize_mode;
      resizeMode.dispatchEvent(new Event('change'));
      if (prefs.resize_value && document.getElementById('resize_value')) {
        document.getElementById('resize_value').value = prefs.resize_value;
      }
      if (prefs.resize_width && document.getElementById('resize_width')) {
        document.getElementById('resize_width').value = prefs.resize_width;
      }
      if (prefs.resize_height && document.getElementById('resize_height')) {
        document.getElementById('resize_height').value = prefs.resize_height;
      }
    }

    if (prefs.strip_metadata !== undefined && document.getElementById('strip_metadata')) {
      document.getElementById('strip_metadata').checked = prefs.strip_metadata;
    }
    if (prefs.lossless !== undefined && document.getElementById('lossless')) {
      document.getElementById('lossless').checked = prefs.lossless;
    }
    if (prefs.optimize !== undefined && document.getElementById('optimize')) {
      document.getElementById('optimize').checked = prefs.optimize;
    }
  } catch (_) {}
}

const state = {
  files: [],
  results: [],
  compressedFilenames: [],
  activeCompareIndex: null,
  compareMode: 'side', // 'side' or 'split'
};

// ─── UI References ───
const qualitySlider   = document.getElementById('quality');
const qualityDisplay  = document.getElementById('quality-display');
const resizeMode      = document.getElementById('resize_mode');
const resizeControls  = document.getElementById('resize-controls');
const resizeSingle    = document.getElementById('resize-single');
const resizeCustom    = document.getElementById('resize-custom');
const resizeLabel     = document.getElementById('resize-label');
const dropZone        = document.getElementById('drop-zone');
const fileInput       = document.getElementById('file-input');
const queueSection    = document.getElementById('queue-section');
const resultsSection  = document.getElementById('results-section');

// ─── Custom Window Titlebar & Dual-Engine Native Drag Controls ───
const titlebar = document.getElementById('custom-titlebar');
if (titlebar) {
  let isDragging = false;
  let lastScreenX = 0;
  let lastScreenY = 0;

  titlebar.addEventListener('mousedown', e => {
    // Only primary left button; ignore clicks on buttons, inputs or window controls
    if (e.button !== 0) return;
    if (e.target.closest('button') || e.target.closest('.window-controls') || e.target.closest('input')) return;

    isDragging = true;
    lastScreenX = e.screenX;
    lastScreenY = e.screenY;

    // Trigger native Win32 window drag immediately
    if (window.pywebview && window.pywebview.api && window.pywebview.api.drag) {
      window.pywebview.api.drag();
    } else {
      apiFetch('/window/drag', { method: 'POST' }).catch(() => {});
    }
  });

  window.addEventListener('mousemove', e => {
    if (!isDragging) return;
    if ((e.buttons & 1) === 0) {
      isDragging = false;
      return;
    }
    const dx = e.screenX - lastScreenX;
    const dy = e.screenY - lastScreenY;
    if (dx !== 0 || dy !== 0) {
      lastScreenX = e.screenX;
      lastScreenY = e.screenY;
      if (window.pywebview && window.pywebview.api && window.pywebview.api.move_by) {
        window.pywebview.api.move_by(dx, dy);
      } else {
        apiFetch('/window/move', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ dx, dy })
        }).catch(() => {});
      }
    }
  });

  window.addEventListener('mouseup', () => {
    isDragging = false;
  });

  // Double click on titlebar to toggle maximize / restore
  titlebar.addEventListener('dblclick', e => {
    if (e.target.closest('button') || e.target.closest('.window-controls') || e.target.closest('input')) return;
    windowToggleMaximize();
  });
}

function windowMinimize() {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.minimize) {
    window.pywebview.api.minimize();
  } else {
    apiFetch('/window/minimize', { method: 'POST' }).catch(() => {});
  }
}

async function windowToggleMaximize() {
  try {
    let data;
    if (window.pywebview && window.pywebview.api && window.pywebview.api.toggle_maximize) {
      data = await window.pywebview.api.toggle_maximize();
    } else {
      const resp = await apiFetch('/window/maximize', { method: 'POST' });
      data = await resp.json();
    }
    updateMaxIcon(data && data.maximized);
  } catch (_) {}
}

function updateMaxIcon(isMax) {
  const icon = document.getElementById('icon-max-state');
  if (icon) {
    const use = icon.querySelector('use');
    if (use) {
      use.setAttribute('href', isMax ? '#icon-restore' : '#icon-maximize');
    }
  }
}

function windowClose() {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.close) {
    window.pywebview.api.close();
  } else {
    apiFetch('/window/close', { method: 'POST' }).catch(() => {});
  }
}

function openOutputFolder() {
  apiFetch('/open-folder', { method: 'POST' }).catch(() => {});
  showToast('Opening output directory');
}

// ─── Slider Background Update ───
function updateSliderBg(slider) {
  const pct = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
  slider.style.background = `linear-gradient(to right, var(--accent) 0%, var(--accent) ${pct}%, var(--bg-input) ${pct}%)`;
}
if (qualitySlider) {
  qualitySlider.addEventListener('input', () => {
    qualityDisplay.textContent = qualitySlider.value + '%';
    updateSliderBg(qualitySlider);
  });
  qualitySlider.addEventListener('change', saveUserPreferences);
  updateSliderBg(qualitySlider);
}

// ─── Format Segment Toggle ───
document.querySelectorAll('.fmt-pill').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.fmt-pill').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const input = btn.querySelector('input');
    if (input) input.checked = true;
    saveUserPreferences();
  });
});

// ─── Resize Mode Selector ───
if (resizeMode) {
  resizeMode.addEventListener('change', () => {
    const val = resizeMode.value;
    if (val === 'none') {
      resizeControls.classList.add('hidden');
      saveUserPreferences();
      return;
    }
    resizeControls.classList.remove('hidden');
    if (val === 'custom') {
      resizeSingle.classList.add('hidden');
      resizeCustom.classList.remove('hidden');
    } else {
      resizeSingle.classList.remove('hidden');
      resizeCustom.classList.add('hidden');
      resizeLabel.textContent = val === 'percentage'
        ? 'Percentage (%)'
        : val === 'width' ? 'Target Width (px)' : 'Target Height (px)';
    }
    saveUserPreferences();
  });
}

// Auto-persist resize numeric fields and compression switches
['resize_value', 'resize_width', 'resize_height'].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('change', saveUserPreferences);
});
['strip_metadata', 'lossless', 'optimize'].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('change', saveUserPreferences);
});

// ─── Presets ───
function applyPreset(preset) {
  const presets = {
    web: {
      name: 'Web Ready',
      quality: 80,
      lossless: false,
      strip_metadata: true,
      optimize: true,
      output_format: 'webp',
    },
    social: {
      name: 'Social Media',
      quality: 85,
      lossless: false,
      strip_metadata: true,
      optimize: true,
      output_format: 'jpeg',
    },
    email: {
      name: 'Compact',
      quality: 62,
      lossless: false,
      strip_metadata: true,
      optimize: true,
      output_format: 'webp',
    },
    lossless: {
      name: 'Lossless',
      quality: 100,
      lossless: true,
      strip_metadata: false,
      optimize: true,
      output_format: 'png',
    },
    print: {
      name: 'Ultra Quality',
      quality: 94,
      lossless: false,
      strip_metadata: false,
      optimize: true,
      output_format: 'same',
    },
    max: {
      name: 'Max Squeeze',
      quality: 48,
      lossless: false,
      strip_metadata: true,
      optimize: true,
      output_format: 'webp',
    },
  };

  const p = presets[preset];
  if (!p) return;

  qualitySlider.value = p.quality;
  qualityDisplay.textContent = p.quality + '%';
  updateSliderBg(qualitySlider);

  document.getElementById('lossless').checked = p.lossless;
  document.getElementById('strip_metadata').checked = p.strip_metadata;
  document.getElementById('optimize').checked = p.optimize;

  document.querySelectorAll('.fmt-pill').forEach(btn => {
    const input = btn.querySelector('input');
    const match = input && input.value === p.output_format;
    btn.classList.toggle('active', match);
    if (input) input.checked = match;
  });

  saveUserPreferences();
  showToast(`Preset "${p.name}" loaded`);
}

// ─── Workspace State Machine (Smart Sidebar Locking) ───
function setWorkspaceView(view) {
  // view: 'empty' | 'queue' | 'results'
  state.currentView = view;

  const sidebar = document.getElementById('sidebar-panel');
  const lockBadge = document.getElementById('sidebar-lock-badge');

  if (view === 'empty') {
    dropZone.classList.remove('hidden');
    queueSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    if (sidebar) sidebar.classList.remove('settings-locked');
    if (lockBadge) lockBadge.classList.add('hidden');
  } else if (view === 'queue') {
    dropZone.classList.add('hidden');
    queueSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    if (sidebar) sidebar.classList.remove('settings-locked');
    if (lockBadge) lockBadge.classList.add('hidden');
  } else if (view === 'results') {
    dropZone.classList.add('hidden');
    queueSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');
    if (sidebar) sidebar.classList.add('settings-locked');
    if (lockBadge) lockBadge.classList.remove('hidden');
  }
}

// ─── Universal Drag and Drop Handlers (Window & Drop Zone) ───
['dragenter', 'dragover'].forEach(name => {
  window.addEventListener(name, e => {
    e.preventDefault();
    if (state.currentView === 'empty') {
      dropZone.classList.add('dragging');
    } else if (state.currentView === 'queue') {
      queueSection.classList.add('dragging-over');
    }
  });
});

['dragleave', 'drop'].forEach(name => {
  window.addEventListener(name, e => {
    e.preventDefault();
    dropZone.classList.remove('dragging');
    queueSection.classList.remove('dragging-over');
  });
});

window.addEventListener('drop', e => {
  e.preventDefault();
  const dropped = Array.from(e.dataTransfer?.files || []).filter(f => f.type.startsWith('image/'));
  if (dropped.length) {
    addFiles(dropped);
  }
});

fileInput.addEventListener('change', () => {
  addFiles(Array.from(fileInput.files));
  fileInput.value = '';
});

// ─── Clipboard Image Paste (Ctrl+V) ───
window.addEventListener('paste', e => {
  const items = e.clipboardData?.items;
  if (!items) return;

  const pastedFiles = [];
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      const blob = item.getAsFile();
      if (blob) {
        const ext = item.type.split('/')[1] || 'png';
        const renamed = new File([blob], `clipboard_image_${Date.now()}.${ext}`, { type: item.type });
        pastedFiles.push(renamed);
      }
    }
  }

  if (pastedFiles.length > 0) {
    addFiles(pastedFiles);
    showToast(`Pasted ${pastedFiles.length} image(s) from clipboard`);
  }
});

// ─── Batch File Staging (O(N) Fast Ingestion for 1,000+ Files) ───
function addFiles(newFiles) {
  const maxSize = 500 * 1024 * 1024; // 500MB per file
  let count = 0;

  // Use a fast Set of existing file signatures (name + size) for instant O(1) deduplication
  const existingSet = new Set(state.files.map(f => `${f.name}_${f.size}`));

  newFiles.forEach(file => {
    if (!file.type.startsWith('image/')) {
      showToast(`Unsupported: ${file.name}`, 'warn');
      return;
    }
    if (file.size > maxSize) {
      showToast(`File exceeds 500MB: ${file.name}`, 'warn');
      return;
    }
    const sig = `${file.name}_${file.size}`;
    if (existingSet.has(sig)) {
      return;
    }
    existingSet.add(sig);
    state.files.push(file);
    count++;
  });

  if (count > 0) {
    renderQueue();
  }
}

function renderQueue() {
  const list = document.getElementById('file-list');
  const countEl = document.getElementById('queue-count');

  // Revoke previous object URLs to prevent RAM leaks
  revokeAllManagedObjectURLs();

  if (state.files.length === 0) {
    setWorkspaceView('empty');
    return;
  }

  setWorkspaceView('queue');
  countEl.textContent = `${state.files.length} image${state.files.length > 1 ? 's' : ''}`;
  list.innerHTML = '';

  const frag = document.createDocumentFragment();
  const maxRender = 100;
  const renderList = state.files.slice(0, maxRender);

  renderList.forEach((file, idx) => {
    const row = document.createElement('div');
    row.className = 'queue-row';

    const thumb = document.createElement('img');
    thumb.className = 'queue-thumb';
    thumb.alt = file.name;
    // Managed Object URL: 0ms, zero RAM leak
    thumb.src = createManagedObjectURL(file);

    row.appendChild(thumb);

    const details = document.createElement('div');
    details.className = 'queue-details';
    details.innerHTML = `
      <div class="queue-name" title="${escHtml(file.name)}">${escHtml(file.name)}</div>
      <div class="queue-meta">${formatSize(file.size)}</div>
    `;
    row.appendChild(details);

    const removeBtn = document.createElement('button');
    removeBtn.className = 'queue-btn-remove';
    removeBtn.title = 'Remove';
    removeBtn.innerHTML = `<svg class="lucide-icon"><use href="#icon-x"/></svg>`;
    removeBtn.onclick = () => removeFile(idx);
    row.appendChild(removeBtn);

    frag.appendChild(row);
  });

  if (state.files.length > maxRender) {
    const moreCard = document.createElement('div');
    moreCard.className = 'queue-overflow-notice';
    moreCard.innerHTML = `
      <svg class="lucide-icon text-accent" style="width:16px; height:16px;"><use href="#icon-check"/></svg>
      <span>...plus <strong>${state.files.length - maxRender} more images</strong> loaded and ready for batch processing</span>
    `;
    frag.appendChild(moreCard);
  }

  list.appendChild(frag);
}

function removeFile(idx) {
  state.files.splice(idx, 1);
  renderQueue();
}

function clearQueue() {
  revokeAllManagedObjectURLs();
  state.files = [];
  state.results = [];
  state.compressedFilenames = [];
  setWorkspaceView('empty');
  apiFetch('/clear-workspace', { method: 'POST' }).catch(() => {});
  showToast('Workspace reset');
}

// ─── Industrial-Grade Chunked Streaming Compression Engine (1,000+ Unlimited Files) ───
let compressionAbortController = null;

async function startCompression() {
  if (state.files.length === 0) {
    showToast('Add images to compress', 'warn');
    return;
  }

  const btn = document.getElementById('compress-btn');
  btn.disabled = true;

  const settings = {
    quality: qualitySlider.value,
    optimize: document.getElementById('optimize').checked,
    lossless: document.getElementById('lossless').checked,
    strip_metadata: document.getElementById('strip_metadata').checked,
    output_format: document.querySelector('input[name="output_format"]:checked')?.value || 'same',
    resize_mode: resizeMode.value,
    resize_value: document.getElementById('resize_value')?.value || 100,
    resize_width: document.getElementById('resize_width')?.value || 0,
    resize_height: document.getElementById('resize_height')?.value || 0,
  };

  const overlay     = document.getElementById('progress-overlay');
  const progressBar = document.getElementById('progress-bar');
  const progressSub = document.getElementById('progress-sub');
  const progressPct = document.getElementById('progress-percentage');
  const cancelBtn   = document.getElementById('progress-cancel-btn');

  overlay.classList.remove('hidden');
  progressBar.style.width = '0%';
  progressPct.textContent = '0%';
  progressSub.textContent = `Preparing ${state.files.length} file(s)...`;

  const totalFiles = state.files.length;
  const CHUNK_SIZE = 8; // Optimal chunk for multi-core concurrency & strict <150MB RAM cap
  const totalChunks = Math.ceil(totalFiles / CHUNK_SIZE);
  let accumulatedResults = [];
  let isCancelled = false;

  const currentBatchId = 'batch_' + Date.now() + '_' + Math.random().toString(36).substr(2, 8);
  compressionAbortController = new AbortController();

  if (cancelBtn) {
    cancelBtn.onclick = () => {
      isCancelled = true;
      if (currentBatchId) {
        apiFetch(`/api/cancel-batch/${encodeURIComponent(currentBatchId)}`, { method: 'POST' }).catch(() => {});
      }
      if (compressionAbortController) compressionAbortController.abort();
      progressSub.textContent = 'Stopping queue...';
    };
  }

  try {
    for (let c = 0; c < totalChunks; c++) {
      if (isCancelled) break;

      const chunkStart = c * CHUNK_SIZE;
      const chunkFiles = state.files.slice(chunkStart, chunkStart + CHUNK_SIZE);

      progressSub.textContent = `Optimizing batch ${chunkStart + 1}-${Math.min(chunkStart + chunkFiles.length, totalFiles)} of ${totalFiles}...`;

      const formData = new FormData();
      formData.append('batch_id', currentBatchId);
      chunkFiles.forEach(f => formData.append('files', f));
      Object.entries(settings).forEach(([k, v]) => formData.append(k, v));

      const resp = await apiFetch('/compress', {
        method: 'POST',
        body: formData,
        signal: compressionAbortController.signal
      });

      const data = await resp.json();
      if (data.results && Array.isArray(data.results)) {
        accumulatedResults.push(...data.results.filter(r => !r.cancelled));
      }

      const completedCount = accumulatedResults.length;
      const progressPercent = Math.min(99, Math.round((completedCount / totalFiles) * 100));
      progressBar.style.width = `${progressPercent}%`;
      progressPct.textContent = `${progressPercent}%`;
      progressSub.textContent = `Optimized ${completedCount} of ${totalFiles} images (${progressPercent}%)...`;
    }

    if (isCancelled) {
      showToast(`Stopped: ${accumulatedResults.length} of ${totalFiles} images were saved`, 'warn');
    } else {
      progressBar.style.width = '100%';
      progressPct.textContent = '100%';
      progressSub.textContent = `Optimization complete! ${accumulatedResults.length} images processed.`;
      await sleep(260);
    }

    overlay.classList.add('hidden');

    if (accumulatedResults.length > 0) {
      renderResults(accumulatedResults);
      if (!isCancelled) {
        showToast(`Finished processing ${accumulatedResults.length} images`);
      }
    } else {
      showToast('No images were processed', 'warn');
    }

  } catch (err) {
    overlay.classList.add('hidden');
    if (err.name !== 'AbortError') {
      showToast('Processing error: ' + err.message, 'error');
    }
    if (accumulatedResults.length > 0) {
      renderResults(accumulatedResults);
    }
  } finally {
    btn.disabled = false;
    compressionAbortController = null;
  }
}

// ─── Render Results with Smart Header Actions ───
function renderResults(results) {
  setWorkspaceView('results');
  const list = document.getElementById('results-list');
  list.innerHTML = '';

  state.results = results;
  const successful = results.filter(r => r.success);
  state.compressedFilenames = successful.map(r => r.compressed_filename);

  // Dynamic Header Actions (New Batch + Single Save / ZIP + Open Folder)
  const headerActions = document.getElementById('results-header-actions');
  const newBatchBtn = `
    <button class="btn-secondary" onclick="clearQueue()" title="Compress another batch">
      <svg class="lucide-icon"><use href="#icon-refresh"/></svg>
      <span>New Batch</span>
    </button>
  `;
  if (successful.length === 1) {
    const single = successful[0];
    headerActions.innerHTML = `
      ${newBatchBtn}
      <button class="btn-secondary" onclick="openOutputFolder()" title="Open folder in File Explorer">
        <svg class="lucide-icon"><use href="#icon-folder"/></svg>
        <span>Open Folder</span>
      </button>
      <button class="btn-primary-green" onclick="saveSingleFile('${encodeURIComponent(single.compressed_filename)}', '${encodeURIComponent(single.original_name)}')">
        <svg class="lucide-icon"><use href="#icon-download"/></svg>
        <span>Save Image</span>
      </button>
    `;
  } else {
    headerActions.innerHTML = `
      ${newBatchBtn}
      <button class="btn-secondary" onclick="openOutputFolder()" title="Open folder in File Explorer">
        <svg class="lucide-icon"><use href="#icon-folder"/></svg>
        <span>Open Folder</span>
      </button>
      <button class="btn-secondary" id="download-all-btn" onclick="downloadAll()" title="Download as single compressed ZIP">
        <svg class="lucide-icon"><use href="#icon-archive"/></svg>
        <span>Download ZIP</span>
      </button>
      <button class="btn-primary-green" id="save-all-folder-btn" onclick="saveAllToFolder()" title="Save all images directly to folder (Ctrl+S)">
        <svg class="lucide-icon"><use href="#icon-download"/></svg>
        <span>Save to Folder</span>
      </button>
    `;
  }

  let totalOrig = 0, totalComp = 0, successCount = 0;
  results.forEach(r => {
    if (r.success) {
      totalOrig += r.original_size;
      totalComp += r.compressed_size;
      successCount++;
    }
  });

  const totalSavedBytes = Math.max(0, totalOrig - totalComp);
  const totalSavings = totalOrig > 0 ? ((1 - totalComp / totalOrig) * 100).toFixed(1) : 0;

  document.getElementById('sum-files').textContent = successCount;
  document.getElementById('sum-original').textContent = formatSize(totalOrig);
  document.getElementById('sum-compressed').textContent = formatSize(totalComp);
  document.getElementById('sum-savings').textContent = `${totalSavings}% (-${formatSize(totalSavedBytes)})`;

  results.forEach((r, idx) => {
    const card = document.createElement('div');
    card.className = 'result-card';

    if (r.error) {
      card.innerHTML = `
        <div class="result-card-left">
          <svg class="lucide-icon text-muted" style="color:var(--red); width:32px; height:32px;"><use href="#icon-alert"/></svg>
          <div class="result-card-info">
            <div class="result-card-title">${escHtml(r.filename || 'File')}</div>
            <div class="stat-pill" style="color:var(--red)">${escHtml(r.error)}</div>
          </div>
        </div>
      `;
      list.appendChild(card);
      return;
    }

    const savings = r.savings_percent;
    const badgeCls = savings >= 15 ? 'good' : savings >= 0 ? 'neutral' : 'bad';
    const arrow = savings >= 0 ? '↓' : '↑';

    card.innerHTML = `
      <div class="result-card-left">
        <img class="result-card-thumb" src="${withAuthToken('/thumb/' + encodeURIComponent(r.compressed_filename))}" alt="${escHtml(r.original_name)}" loading="lazy">
        <div class="result-card-info">
          <div class="result-card-title" title="${escHtml(r.original_name)}">${escHtml(r.original_name)}</div>
          <div class="result-card-sizes">
            <span class="size-orig">${r.original_size_fmt}</span>
            <span class="size-arrow">➔</span>
            <span class="size-comp">${r.compressed_size_fmt}</span>
            <span class="savings-chip ${badgeCls}">
              ${arrow} ${Math.abs(savings)}% saved
            </span>
          </div>
        </div>
      </div>
      <div class="result-card-right">
        <div class="result-meta-pill" title="Output resolution and encoding time">
          <span>${r.output_width} × ${r.output_height}px</span>
          <span class="meta-dot">·</span>
          <span>${r.time_taken}s</span>
        </div>
        <div class="result-actions">
          <button class="btn-card-action btn-action-compare" onclick="openCompareModal(${idx})" title="Compare Before / After">
            <svg class="lucide-icon"><use href="#icon-eye"/></svg>
            <span>Compare</span>
          </button>
          <button class="btn-card-action btn-action-save" onclick="saveSingleFile('${encodeURIComponent(r.compressed_filename)}', '${encodeURIComponent(r.original_name)}')" title="Save this optimized image">
            <svg class="lucide-icon"><use href="#icon-download"/></svg>
            <span>Save</span>
          </button>
        </div>
      </div>
    `;

    list.appendChild(card);
  });
}

// ─── Save Single Image via Native Desktop API ───
async function saveSingleFile(encodedFilename, encodedOriginalName) {
  const filename = decodeURIComponent(encodedFilename);
  const originalName = decodeURIComponent(encodedOriginalName);
  try {
    const resp = await apiFetch('/api/save-file', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename, original_name: originalName })
    });
    const data = await resp.json();
    if (data.status === 'ok') {
      showToast(`Saved: ${data.filename}`);
    } else if (data.status === 'cancelled') {
      // User cancelled dialog
    } else if (data.error) {
      showToast('Save failed: ' + data.error, 'error');
    }
  } catch (err) {
    showToast('Save error: ' + err.message, 'error');
  }
}

// ─── Save All Images Directly to Selected Folder (Native Folder Dialog) ───
async function saveAllToFolder() {
  if (!state.compressedFilenames.length) return;
  const btn = document.getElementById('save-all-folder-btn');
  if (btn) btn.disabled = true;

  try {
    const resp = await apiFetch('/api/save-all-folder', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filenames: state.compressedFilenames }),
    });

    const data = await resp.json();
    if (data.status === 'ok') {
      showToast(`Saved ${data.saved_count} images to folder: ${data.folder}`);
    } else if (data.status === 'cancelled') {
      // User cancelled dialog
    } else if (data.error) {
      showToast('Save error: ' + data.error, 'error');
    }
  } catch (err) {
    showToast('Save failed: ' + err.message, 'error');
  } finally {
    if (btn) btn.disabled = false;
  }
}

// ─── Download All (ZIP) via Native Desktop API ───
async function downloadAll() {
  if (!state.compressedFilenames.length) return;
  const btn = document.getElementById('download-all-btn');
  if (btn) btn.disabled = true;

  try {
    const resp = await apiFetch('/api/save-zip', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filenames: state.compressedFilenames }),
    });

    const data = await resp.json();
    if (data.status === 'ok') {
      showToast(`Saved ZIP: ${data.filename}`);
    } else if (data.status === 'cancelled') {
      // User cancelled dialog
    } else if (data.error) {
      showToast('ZIP error: ' + data.error, 'error');
    }
  } catch (err) {
    showToast('Download failed: ' + err.message, 'error');
  } finally {
    if (btn) btn.disabled = false;
  }
}

// ─── Dual-Mode Inspection Modal (Side-by-Side & Split Slider) ───
const compareModal     = document.getElementById('compare-modal');
const compareStageSide = document.getElementById('compare-stage-side');
const compareStageSplit = document.getElementById('compare-stage-split');
const compareTitle     = document.getElementById('compare-filename');
const sideOrigImg      = document.getElementById('side-orig-img');
const sideCompImg      = document.getElementById('side-comp-img');
const sideOrigSpecs    = document.getElementById('side-orig-specs');
const sideCompSpecs    = document.getElementById('side-comp-specs');
const compareOrigImg   = document.getElementById('compare-orig-img');
const compareCompImg   = document.getElementById('compare-comp-img');
const compareOverlay   = document.getElementById('compare-overlay-layer');
const compareHandle    = document.getElementById('compare-handle');

// ─── Deep Pixel Inspection Zoom & Pan Engine (1:1 & 200% Peeping) ───
let currentZoom = 1.0;
let panX = 0;
let panY = 0;
let zoomMode = 'fit'; // 'fit' | '100' | '200' | 'custom'
let isPanning = false;
let panStartX = 0;
let panStartY = 0;
let initialPanX = 0;
let initialPanY = 0;

function setZoomMode(mode) {
  zoomMode = mode;
  if (mode === 'fit') {
    currentZoom = 1.0;
    panX = 0;
    panY = 0;
  } else if (mode === '100') {
    currentZoom = 1.0;
  } else if (mode === '200') {
    currentZoom = 2.0;
  }
  updateZoomUI();
}

function zoomChange(delta) {
  zoomMode = 'custom';
  currentZoom = Math.max(0.25, Math.min(4.0, Math.round((currentZoom + delta) * 100) / 100));
  updateZoomUI();
}

function updateZoomUI() {
  const display = document.getElementById('zoom-level-display');
  if (display) {
    display.textContent = `${Math.round(currentZoom * 100)}%`;
  }
  const btnFit = document.getElementById('btn-zoom-fit');
  const btn100 = document.getElementById('btn-zoom-100');
  const btn200 = document.getElementById('btn-zoom-200');

  if (btnFit) btnFit.classList.toggle('active', zoomMode === 'fit');
  if (btn100) btn100.classList.toggle('active', zoomMode === '100' || (zoomMode === 'custom' && Math.abs(currentZoom - 1.0) < 0.01));
  if (btn200) btn200.classList.toggle('active', zoomMode === '200' || (zoomMode === 'custom' && Math.abs(currentZoom - 2.0) < 0.01));

  applyZoomTransform();
}

function applyZoomTransform() {
  const targets = document.querySelectorAll('.zoom-target');
  const transformStr = (zoomMode === 'fit' && panX === 0 && panY === 0)
    ? 'none'
    : `translate(${panX}px, ${panY}px) scale(${currentZoom})`;

  targets.forEach(el => {
    el.style.transform = transformStr;
  });
}

function resetZoom() {
  currentZoom = 1.0;
  panX = 0;
  panY = 0;
  zoomMode = 'fit';
  updateZoomUI();
}

window.setZoomMode = setZoomMode;
window.zoomChange = zoomChange;
window.resetZoom = resetZoom;

// Viewport Zoom & Pan Event Listeners
function initZoomPanEngine() {
  const viewports = document.querySelectorAll('.zoomable-viewport');

  viewports.forEach(vp => {
    vp.addEventListener('wheel', e => {
      e.preventDefault();
      const delta = e.deltaY < 0 ? 0.25 : -0.25;
      zoomChange(delta);
    }, { passive: false });

    vp.addEventListener('contextmenu', e => {
      if (currentZoom > 1.0 || panX !== 0 || panY !== 0) {
        e.preventDefault();
      }
    });

    vp.addEventListener('mousedown', e => {
      if (e.target.closest('#compare-handle') || e.target.closest('button')) return;

      if (state.compareMode === 'split' && e.button === 0 && !e.shiftKey && currentZoom <= 1.0 && panX === 0 && panY === 0) {
        return; // Normal split handle drag
      }

      if (e.button === 0 || e.button === 1 || e.button === 2) {
        e.preventDefault();
        isPanning = true;
        panStartX = e.clientX;
        panStartY = e.clientY;
        initialPanX = panX;
        initialPanY = panY;
        document.querySelectorAll('.zoomable-viewport').forEach(v => v.classList.add('panning'));
      }
    });
  });

  window.addEventListener('mousemove', e => {
    if (!isPanning) return;
    e.preventDefault();
    const dx = e.clientX - panStartX;
    const dy = e.clientY - panStartY;
    panX = initialPanX + dx;
    panY = initialPanY + dy;
    applyZoomTransform();
  });

  window.addEventListener('mouseup', () => {
    if (isPanning) {
      isPanning = false;
      document.querySelectorAll('.zoomable-viewport').forEach(v => v.classList.remove('panning'));
    }
  });
}

// Split Handle ARIA Keyboard Navigation
if (compareHandle) {
  compareHandle.addEventListener('keydown', e => {
    let currentPct = 50;
    const handleLeft = compareHandle.style.left;
    if (handleLeft && handleLeft.endsWith('%')) {
      currentPct = parseFloat(handleLeft);
    }
    if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') {
      e.preventDefault();
      setSplitPosition(currentPct - 2);
    } else if (e.key === 'ArrowRight' || e.key === 'ArrowUp') {
      e.preventDefault();
      setSplitPosition(currentPct + 2);
    } else if (e.key === 'Home') {
      e.preventDefault();
      setSplitPosition(0);
    } else if (e.key === 'End') {
      e.preventDefault();
      setSplitPosition(100);
    }
  });
}

function switchCompareMode(mode) {
  state.compareMode = mode;
  const btnSide = document.getElementById('btn-mode-side');
  const btnSplit = document.getElementById('btn-mode-split');
  const footerHint = document.getElementById('compare-footer-hint');

  if (mode === 'side') {
    btnSide.classList.add('active');
    btnSplit.classList.remove('active');
    compareStageSide.classList.remove('hidden');
    compareStageSplit.classList.add('hidden');
    footerHint.textContent = 'Viewing side-by-side comparison with retained pixel clarity (Space to switch)';
  } else {
    btnSide.classList.remove('active');
    btnSplit.classList.add('active');
    compareStageSide.classList.add('hidden');
    compareStageSplit.classList.remove('hidden');
    footerHint.textContent = 'Drag the center handle left or right to inspect pixel quality (Space to switch)';
    setSplitPosition(50);
  }
}

function openCompareModal(index) {
  const item = state.results[index];
  if (!item || !item.success) return;

  state.activeCompareIndex = index;
  compareTitle.textContent = item.original_name;

  const origUrl = withAuthToken(`/original/${encodeURIComponent(item.input_filename)}`);
  const compUrl = withAuthToken(`/preview/${encodeURIComponent(item.compressed_filename)}`);

  // Side-by-side targets
  sideOrigImg.src = origUrl;
  sideCompImg.src = compUrl;
  sideOrigSpecs.textContent = `${item.original_width} × ${item.original_height}px · ${item.original_size_fmt}`;
  sideCompSpecs.textContent = `${item.output_width} × ${item.output_height}px · ${item.compressed_size_fmt} (${item.savings_percent}% Saved)`;

  // Split slider targets
  compareOrigImg.src = origUrl;
  compareCompImg.src = compUrl;

  resetZoom();
  setSplitPosition(50);
  switchCompareMode(state.compareMode || 'side');
  compareModal.classList.remove('hidden');
}

function closeCompareModal() {
  compareModal.classList.add('hidden');
  resetZoom();
  sideOrigImg.src = '';
  sideCompImg.src = '';
  compareOrigImg.src = '';
  compareCompImg.src = '';
  state.activeCompareIndex = null;
}

let isDraggingCompare = false;
let splitStageRect = null;
let splitRafId = null;

function setSplitPosition(pct) {
  const bounded = Math.max(0, Math.min(100, pct));
  if (compareOverlay) {
    compareOverlay.style.clipPath = `inset(0 0 0 ${bounded}%)`;
  }
  if (compareHandle) {
    compareHandle.style.left = `${bounded}%`;
    compareHandle.setAttribute('aria-valuenow', Math.round(bounded));
  }

  // Symmetric smart fade for badges so line never cuts through them:
  const badgeOrig = document.getElementById('split-badge-orig');
  const badgeComp = document.getElementById('split-badge-comp');
  if (badgeOrig) {
    // Fade out original badge when handle approaches left (< 20%)
    badgeOrig.style.opacity = bounded < 20 ? Math.max(0, (bounded - 5) / 15) : 1;
  }
  if (badgeComp) {
    // Fade out compressed badge when handle approaches right (> 80%)
    badgeComp.style.opacity = bounded > 80 ? Math.max(0, (95 - bounded) / 15) : 1;
  }
}

function handleCompareDrag(clientX) {
  if (!splitStageRect || splitStageRect.width <= 0) {
    if (compareStageSplit) splitStageRect = compareStageSplit.getBoundingClientRect();
    if (!splitStageRect || splitStageRect.width <= 0) return;
  }
  const x = clientX - splitStageRect.left;
  const pct = (x / splitStageRect.width) * 100;

  if (splitRafId) cancelAnimationFrame(splitRafId);
  splitRafId = requestAnimationFrame(() => setSplitPosition(pct));
}

// Mouse & Touch events for comparison slider (Featherweight, 120fps optimized)
if (compareStageSplit) {
  const startDrag = (clientX) => {
    isDraggingCompare = true;
    splitStageRect = compareStageSplit.getBoundingClientRect();
    handleCompareDrag(clientX);
  };

  compareStageSplit.addEventListener('mousedown', e => {
    if (e.button !== 0 || e.shiftKey || (currentZoom > 1.0 && isPanning)) return;
    startDrag(e.clientX);
  });
  window.addEventListener('mousemove', e => {
    if (isDraggingCompare) {
      e.preventDefault();
      handleCompareDrag(e.clientX);
    }
  });
  window.addEventListener('mouseup', () => {
    isDraggingCompare = false;
    splitStageRect = null;
  });

  // Touch events
  compareStageSplit.addEventListener('touchstart', e => {
    if (e.touches.length > 0) {
      startDrag(e.touches[0].clientX);
    }
  }, { passive: true });
  window.addEventListener('touchmove', e => {
    if (isDraggingCompare && e.touches.length > 0) {
      handleCompareDrag(e.touches[0].clientX);
    }
  }, { passive: true });
  window.addEventListener('touchend', () => {
    isDraggingCompare = false;
    splitStageRect = null;
  });
}

// ─── Pro Desktop Keyboard Shortcuts (Ctrl+O, Ctrl+S, Ctrl+V, Esc, Delete, Enter) ───
window.addEventListener('keydown', e => {
  // If user is focused inside a text input/textarea, ignore custom shortcuts
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) {
    if (e.key === 'Escape') {
      document.activeElement.blur();
    }
    return;
  }

  // Ctrl + O: Direct Open File Dialog
  if ((e.ctrlKey || e.metaKey) && (e.key === 'o' || e.key === 'O')) {
    e.preventDefault();
    if (fileInput) fileInput.click();
    return;
  }

  // Ctrl + S: Save All Images to Folder or Single Image
  if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S')) {
    e.preventDefault();
    if (state.currentView === 'results') {
      const successful = state.results.filter(r => r.success);
      if (successful.length === 1) {
        saveSingleFile(encodeURIComponent(successful[0].compressed_filename), encodeURIComponent(successful[0].original_name));
      } else if (successful.length > 1) {
        saveAllToFolder();
      }
    } else {
      showToast('No active compression results to save', 'warn');
    }
    return;
  }

  // Space: Toggle compare mode between side-by-side and split slider
  if (e.code === 'Space' || e.key === ' ') {
    if (compareModal && !compareModal.classList.contains('hidden')) {
      e.preventDefault();
      switchCompareMode(state.compareMode === 'side' ? 'split' : 'side');
      return;
    }
  }

  // Escape: Close active modals
  if (e.key === 'Escape') {
    if (compareModal && !compareModal.classList.contains('hidden')) {
      closeCompareModal();
      return;
    }
  }

  // Delete: Remove last item from batch queue
  if (e.key === 'Delete') {
    if (state.currentView === 'queue' && state.files.length > 0) {
      removeFile(state.files.length - 1);
      showToast('Removed item from queue');
    }
  }

  // Enter: Trigger compression if in queue view
  if (e.key === 'Enter' && state.currentView === 'queue' && state.files.length > 0) {
    const btn = document.getElementById('compress-btn');
    if (btn && !btn.disabled) {
      startCompression();
    }
  }
});

// ─── Helpers ───
function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

function escHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

let toastTimer;
function showToast(msg, type = 'info') {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    document.body.appendChild(toast);
  }

  const iconName = type === 'error' ? '#icon-alert' : '#icon-check';
  const iconColor = type === 'error' ? 'var(--red)' : '#10b981';
  toast.innerHTML = `<svg class="lucide-icon" style="color:${iconColor}; width:16px; height:16px; flex-shrink:0;"><use href="${iconName}"/></svg><span style="display:inline-block; line-height:1.2;">${escHtml(msg)}</span>`;
  toast.className = 'show';

  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.className = '';
  }, 2600);
}

// Periodic cleanup ping
setInterval(() => {
  apiFetch('/cleanup', { method: 'POST' }).catch(() => {});
}, 30 * 60 * 1000);

// ─── World-Class Dynamic Glassmorphism Tooltip Engine ───
(function initTooltipEngine() {
  const tooltipEl = document.createElement('div');
  tooltipEl.id = 'app-tooltip';
  tooltipEl.className = 'app-tooltip';
  document.body.appendChild(tooltipEl);

  let activeTarget = null;
  let showTimer = null;

  function parseTooltipContent(text) {
    if (!text) return '';
    let safe = escHtml(text);
    return safe.replace(/\((Ctrl\+[A-Za-z]|Enter|Esc|Delete|Space|Win\+[A-Za-z])\)/gi, '<kbd class="tooltip-kbd">$1</kbd>');
  }

  function showTooltip(el) {
    const rawText = el.getAttribute('data-tooltip') || el.getAttribute('title');
    if (!rawText) return;

    // Suppress native browser tooltip permanently across DOM
    if (el.hasAttribute('title')) {
      el.setAttribute('data-tooltip', rawText);
      el.removeAttribute('title');
    }

    activeTarget = el;
    tooltipEl.innerHTML = parseTooltipContent(rawText);

    const rect = el.getBoundingClientRect();
    const margin = 8;
    let top = rect.top - margin;
    let left = rect.left + rect.width / 2;

    if (rect.top < 38) {
      top = rect.bottom + margin;
      tooltipEl.classList.add('placement-bottom');
    } else {
      tooltipEl.classList.remove('placement-bottom');
    }

    tooltipEl.style.top = `${Math.round(top)}px`;
    tooltipEl.style.left = `${Math.round(left)}px`;

    clearTimeout(showTimer);
    showTimer = setTimeout(() => {
      if (activeTarget === el) {
        const tipRect = tooltipEl.getBoundingClientRect();
        const winWidth = window.innerWidth;
        if (tipRect.left < 10) {
          left = 10 + tipRect.width / 2;
          tooltipEl.style.left = `${Math.round(left)}px`;
        } else if (tipRect.right > winWidth - 10) {
          left = winWidth - 10 - tipRect.width / 2;
          tooltipEl.style.left = `${Math.round(left)}px`;
        }
        tooltipEl.classList.add('visible');
      }
    }, 100);
  }

  function hideTooltip() {
    clearTimeout(showTimer);
    activeTarget = null;
    tooltipEl.classList.remove('visible');
  }

  document.addEventListener('mouseover', e => {
    const target = e.target.closest('[title], [data-tooltip]');
    if (target) {
      showTooltip(target);
    }
  }, true);

  document.addEventListener('mouseout', e => {
    const target = e.target.closest('[title], [data-tooltip]');
    if (target) {
      hideTooltip();
    }
  }, true);

  document.addEventListener('mousedown', () => {
    hideTooltip();
  }, true);

  window.addEventListener('scroll', () => {
    hideTooltip();
  }, true);
})();

// ─── Phase 3 Workstation Bootstrap ───
document.addEventListener('DOMContentLoaded', () => {
  initZoomPanEngine();
  loadUserPreferences();
});
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  initZoomPanEngine();
  loadUserPreferences();
}
