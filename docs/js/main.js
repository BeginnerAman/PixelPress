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
   2. Interactive Comparison Split Slider (Modern Pointer Events API)
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

  // Modern Pointer Events (Works identically for Mouse, Touch, and Stylus)
  handle.addEventListener('pointerdown', (e) => {
    isDragging = true;
    handle.setPointerCapture(e.pointerId);
    e.preventDefault();
  });

  handle.addEventListener('pointermove', (e) => {
    if (!isDragging) return;
    updateSplit(e.clientX);
    e.preventDefault();
  });

  const stopDrag = (e) => {
    if (!isDragging) return;
    isDragging = false;
    try {
      handle.releasePointerCapture(e.pointerId);
    } catch (err) {
      // Ignored
    }
  };

  handle.addEventListener('pointerup', stopDrag);
  handle.addEventListener('pointercancel', stopDrag);

  // Allow clicking on container to jump split position (ignore clicks on handle)
  container.addEventListener('pointerdown', (e) => {
    if (e.target === handle || handle.contains(e.target)) return;
    updateSplit(e.clientX);
  });

  // Format Switcher Tabs with Real Images
  const tabButtons = document.querySelectorAll('.inspector-tab-btn');
  const rawSizeEl = document.getElementById('statRawSize');
  const optSizeEl = document.getElementById('statOptSize');
  const ratioEl = document.getElementById('statRatio');
  const algoEl = document.getElementById('statAlgo');
  const sceneTitleEl = document.getElementById('sceneTitle');

  const imgOrig = document.getElementById('inspectImgOrig');
  const imgOpt = document.getElementById('inspectImgOpt');

  const formatData = {
    jpeg: {
      title: 'Architectural Twilight Landscape (High Dynamic Range Photography)',
      raw: '702 KB',
      opt: '206 KB',
      ratio: '70.7%',
      algo: 'Progressive DCT 4:2:0',
      origSrc: 'images/inspect-photo-orig.jpg',
      optSrc: 'images/inspect-photo-opt.jpg'
    },
    png: {
      title: 'Vector UI Dashboard System and Alpha Transparency Channel',
      raw: '13 KB',
      opt: '6 KB',
      ratio: '53.8%',
      algo: '8-bit FastOctree RGBA',
      origSrc: 'images/inspect-ui-orig.png',
      optSrc: 'images/inspect-ui-opt.png'
    },
    webp: {
      title: 'Modern High-Contrast Editorial Graphics Banner',
      raw: '39 KB',
      opt: '15 KB',
      ratio: '61.5%',
      algo: 'Method-4 Predictive Coding',
      origSrc: 'images/inspect-banner-orig.webp',
      optSrc: 'images/inspect-banner-opt.webp'
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

      if (imgOrig && data.origSrc) imgOrig.src = data.origSrc;
      if (imgOpt && data.optSrc) imgOpt.src = data.optSrc;

      // Reset split to center 50%
      afterLayer.style.width = '50%';
      handle.style.left = '50%';
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
   4. Smooth FAQ Accordion (Hardware-Accelerated Zero-Lag)
   -------------------------------------------------------------------------- */
function initFaqAccordion() {
  const faqItems = document.querySelectorAll('.faq-item');

  faqItems.forEach(item => {
    const questionBtn = item.querySelector('.faq-question');
    if (!questionBtn) return;

    questionBtn.addEventListener('click', () => {
      const isAlreadyActive = item.classList.contains('active');

      // Toggle this item smoothly
      if (isAlreadyActive) {
        item.classList.remove('active');
      } else {
        // Close others cleanly
        faqItems.forEach(other => {
          if (other !== item) other.classList.remove('active');
        });
        item.classList.add('active');
      }
    });
  });
}
