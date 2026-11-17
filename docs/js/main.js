/**
 * PixelPress Desktop Pro - Official Website JavaScript
 * Version: v2.1.0 Desktop Pro
 * Author: Aman Vishwakarma
 * Zero Emojis - Zero Em-Dashes
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavbarScroll();
  initComparisonSlider();
  initSavingsCalculator();
  initFaqAccordion();
});

/* --------------------------------------------------------------------------
   1. Navbar Scroll Backdrop Transition
   -------------------------------------------------------------------------- */
function initNavbarScroll() {
  const navbar = document.querySelector('header.navbar');
  if (!navbar) return;

  const handleScroll = () => {
    if (window.scrollY > 20) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  };

  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();
}

/* --------------------------------------------------------------------------
   2. Interactive Comparison Split Slider (Mouse and Touch Support)
   -------------------------------------------------------------------------- */
function initComparisonSlider() {
  const container = document.getElementById('splitSlider');
  const afterLayer = document.getElementById('splitAfterLayer');
  const handle = document.getElementById('splitHandle');
  if (!container || !afterLayer || !handle) return;

  let isDragging = false;

  const updateSplit = (clientX) => {
    const rect = container.getBoundingClientRect();
    let x = clientX - rect.left;
    if (x < 0) x = 0;
    if (x > rect.width) x = rect.width;

    const percentage = (x / rect.width) * 100;
    afterLayer.style.width = percentage + '%';
    handle.style.left = percentage + '%';
  };

  // Mouse Drag Events
  handle.addEventListener('mousedown', (e) => {
    isDragging = true;
    e.preventDefault();
  });

  window.addEventListener('mouseup', () => {
    isDragging = false;
  });

  window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    updateSplit(e.clientX);
  });

  // Jump to click point
  container.addEventListener('click', (e) => {
    updateSplit(e.clientX);
  });

  // Touch Drag Events
  handle.addEventListener('touchstart', (e) => {
    isDragging = true;
  }, { passive: true });

  window.addEventListener('touchend', () => {
    isDragging = false;
  });

  window.addEventListener('touchmove', (e) => {
    if (!isDragging || !e.touches[0]) return;
    updateSplit(e.touches[0].clientX);
  }, { passive: true });

  // Format Switcher Tabs
  const tabButtons = document.querySelectorAll('.inspector-tab-btn');
  const rawSizeEl = document.getElementById('statRawSize');
  const optSizeEl = document.getElementById('statOptSize');
  const ratioEl = document.getElementById('statRatio');
  const algoEl = document.getElementById('statAlgo');
  const sceneTitleEl = document.getElementById('sceneTitle');

  const sceneJpeg = document.querySelectorAll('.scene-content-jpeg');
  const scenePng = document.querySelectorAll('.scene-content-png');
  const sceneWebp = document.querySelectorAll('.scene-content-webp');

  const formatData = {
    jpeg: {
      title: 'Architectural Twilight Landscape (High Dynamic Range)',
      raw: '8.45 MB',
      opt: '1.42 MB',
      ratio: '83.2%',
      algo: 'Progressive DCT 4:2:0'
    },
    png: {
      title: 'Vector UI System and Alpha Transparency Channel',
      raw: '4.20 MB',
      opt: '780 KB',
      ratio: '81.4%',
      algo: '8-bit FastOctree RGBA'
    },
    webp: {
      title: 'Modern High-Contrast Editorial Graphics Banner',
      raw: '5.10 MB',
      opt: '640 KB',
      ratio: '87.5%',
      algo: 'Method-4 Predictive Coding'
    }
  };

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const fmt = btn.getAttribute('data-format');
      const data = formatData[fmt];
      if (!data) return;

      if (rawSizeEl) rawSizeEl.textContent = data.raw;
      if (optSizeEl) optSizeEl.textContent = data.opt;
      if (ratioEl) ratioEl.textContent = data.ratio;
      if (algoEl) algoEl.textContent = data.algo;
      if (sceneTitleEl) sceneTitleEl.textContent = data.title;

      // Toggle visual scenes
      const showScene = (nodes, visible) => {
        nodes.forEach(n => {
          n.style.display = visible ? 'block' : 'none';
        });
      };

      showScene(sceneJpeg, fmt === 'jpeg');
      showScene(scenePng, fmt === 'png');
      showScene(sceneWebp, fmt === 'webp');
    });
  });
}

/* --------------------------------------------------------------------------
   3. Interactive Storage and Bandwidth Savings Calculator
   -------------------------------------------------------------------------- */
function initSavingsCalculator() {
  const rangeInput = document.getElementById('calcRange');
  const countReadout = document.getElementById('calcCountReadout');
  const diskSavedEl = document.getElementById('calcDiskSaved');
  const bandwidthSavedEl = document.getElementById('calcBandwidthSaved');
  const timeSavedEl = document.getElementById('calcTimeSaved');
  const costSavedEl = document.getElementById('calcCostSaved');

  if (!rangeInput || !countReadout) return;

  const calculate = () => {
    const monthlyCount = parseInt(rangeInput.value, 10);
    countReadout.textContent = monthlyCount.toLocaleString() + ' images / mo';

    // Model:
    // Average image payload: 3.5 MB
    // Average reduction yield: 75% -> saves 2.625 MB per asset
    const avgSavingsMB = 2.625;
    const yearlyImages = monthlyCount * 12;
    const totalSavingsMB = yearlyImages * avgSavingsMB;
    const totalSavingsGB = totalSavingsMB / 1024;

    // 1. Local SSD Space Saved
    if (diskSavedEl) {
      if (totalSavingsGB >= 1000) {
        diskSavedEl.textContent = (totalSavingsGB / 1024).toFixed(1) + ' TB / yr';
      } else {
        diskSavedEl.textContent = totalSavingsGB.toFixed(1) + ' GB / yr';
      }
    }

    // 2. Cloud and CDN Bandwidth Saved (Assume 8 views per asset)
    if (bandwidthSavedEl) {
      const bandwidthGB = totalSavingsGB * 8;
      if (bandwidthGB >= 1000) {
        bandwidthSavedEl.textContent = (bandwidthGB / 1024).toFixed(1) + ' TB / yr';
      } else {
        bandwidthSavedEl.textContent = bandwidthGB.toFixed(1) + ' GB / yr';
      }
    }

    // 3. Upload Time Saved (25 Mbps connection -> ~3.12 MB/s)
    if (timeSavedEl) {
      const uploadSeconds = totalSavingsMB / 3.12;
      const uploadHours = uploadSeconds / 3600;
      timeSavedEl.textContent = uploadHours.toFixed(1) + ' Hrs / yr';
    }

    // 4. TinyPNG API Cost Saved ($0.009 per image after 500 free monthly)
    if (costSavedEl) {
      const paidImagesPerMonth = Math.max(0, monthlyCount - 500);
      const yearlyCost = paidImagesPerMonth * 0.009 * 12;
      costSavedEl.textContent = '$' + Math.round(yearlyCost).toLocaleString() + ' / yr';
    }
  };

  rangeInput.addEventListener('input', calculate);
  calculate();
}

/* --------------------------------------------------------------------------
   4. Smooth FAQ Accordion
   -------------------------------------------------------------------------- */
function initFaqAccordion() {
  const faqItems = document.querySelectorAll('.faq-item');

  faqItems.forEach(item => {
    const questionBtn = item.querySelector('.faq-question');
    if (!questionBtn) return;

    questionBtn.addEventListener('click', () => {
      const isActive = item.classList.contains('active');

      // Close other accordion items
      faqItems.forEach(otherItem => {
        otherItem.classList.remove('active');
      });

      // Toggle current item
      if (!isActive) {
        item.classList.add('active');
      }
    });
  });
}
