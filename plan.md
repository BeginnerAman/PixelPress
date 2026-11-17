# PIXELPRESS DESKTOP PRO — MASTER RE-ENGINEERING & UPGRADE PLAN

> **Document Version:** 1.0.0  
> **Status:** Approved / Execution Ready  
> **Target OS:** Windows 10 / Windows 11 (64-bit)  
> **Auditor & Lead Architect:** Senior Full-Stack Auditor & DeepMind Agent  
> **Author & Maintainer:** Aman Vishwakarma (@BeginnerAman)  

---

## 1. VISION & CORE OBJECTIVES

PixelPress Desktop Pro ko ek aesthetic web-wrapper prototype se transform karke ek **genuine, production-grade, enterprise-ready Windows image optimization workstation** banana hai. 

### Key Transformation Pillars:
1. **Security & Zero-Trust Localhost:** Localhost Flask server ko unauthenticated state se protect karke random crypto-session token (`X-PixelPress-Token`), strict path sandboxing, aur anti-traversal validation lagana.
2. **True Desktop Performance (Zero I/O Waste):** Quadruple disk write penalty ko eliminate karna, dynamic multi-core CPU scaling (unlocking 8-16+ cores), aur memory leaks (`URL.revokeObjectURL`) band karna.
3. **Pro-Grade Image Integrity:** Professional photographers ke standards ke mutabiq ICC Color Profile retention, CMYK clean conversion, Animated GIF/WebP multi-frame preservation, aur Decompression Bomb crash protection integrate karna.
4. **World-Class Ergonomics & UX:** Comparison modal mein **1:1 (100%) Pixel-Peeping Zoom & Pan**, missing `Space` shortcut wiring, `localStorage` settings persistence, responsive CSS layout, aur full WCAG AA accessibility implement karna.
5. **Engineering Rigor & Reality Alignment:** Monolithic code ka modular refactoring, 100% truthful documentation (zero marketing lies like "O(1) memory"), complete `pytest` test suite, aur automated GitHub Actions CI/CD pipeline setup.

---

## 2. ARCHITECTURAL GAP ANALYSIS & REMEDIATION STRATEGY

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CURRENT STATE vs. TARGET STATE                        │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ CURRENT (Flawed / Vulnerable)        │ TARGET (Production-Grade Workstation)│
├──────────────────────────────────────┼──────────────────────────────────────┤
│ Unauthenticated localhost port 5000  │ Dynamic port + High-entropy token    │
│ Arbitrary explorer invocation path   │ Strict path sandboxing to output dir │
│ 4x SSD disk writes per batch image   │ Streamlined direct I/O pipeline      │
│ Hard-capped at 4 worker threads      │ Dynamic CPU core scaling (up to 16)  │
│ Zero URL.revokeObjectURL (RAM leak)  │ Systematic URL lifecycle tracking    │
│ Animated GIF/WebP crushed to 1 frame │ Full multi-frame preservation engine │
│ ICC profiles stripped on compression │ Color profiles & metadata preserved  │
│ Decompression bomb crash on >89MP    │ Configured safe pixel ceiling (200MP)│
│ Comparison modal lacks zoom/pan      │ Interactive 1:1 & 200% Zoom + Pan    │
│ Missing Space key & no persistence   │ Fully wired shortcuts & localStorage │
│ Monolithic 987-line app.py           │ Modular service architecture         │
│ Zero tests, POSIX gunicorn in reqs   │ Full pytest test suite & clean reqs  │
│ Fake O(1) memory & sub-200ms claims  │ 100% verified engineering benchmarks │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 3. MASTER ARCHITECTURE SPECIFICATION

### 3.1 Security Subsystem
* **Session Auth Handshake:** `launcher.py` launch ke waqt `secrets.token_urlsafe(32)` generate karega aur use Flask runtime config aur HTML template render context mein inject karega.
* **Header Interceptor:** Frontend ke har fetch request mein `X-PixelPress-Token` header attached hoga.
* **Route Gatekeeper:** Flask middleware verify karega ki har `/api/*`, `/compress`, `/download/*`, `/window/*` request valid token ke saath aayi ho. Unauthenticated requests ko turant `403 Forbidden` return hoga.
* **Path Sanitization:** File operations `os.path.commonpath` ya strict prefix checking se verify honge taaki koi bhi `..\\` directory traversal na ho sake.

### 3.2 Processing & Compression Engine
* **Pillow Engine Hardening:**
  * `Image.MAX_IMAGE_PIXELS = 250_000_000` set hoga with graceful error handling.
  * `icc_profile = img.info.get('icc_profile')` preserve hoga for JPEG & PNG.
  * CMYK images ko standard sRGB profile transform se convert kiya jayega using `ImageCms` ya high-fidelity fallback taaki neon inversion na ho.
  * Multi-frame images (GIF/WebP) ke frames iterate karke `save_all=True`, `duration=img.info.get('duration')`, `loop=img.info.get('loop', 0)` ke saath save honge.
* **True Worker Pool Scaling:**
  ```python
  worker_count = max(2, min(os.cpu_count() or 4, 16))
  ```
  Isse quad-core laptops par 4 threads, 8-core CPUs par 8 threads, aur Threadrippers par 16 threads efficiently utilise honge.
* **Cancellation Signal Protocol:**
  Batch job ke saath ek unique `batch_id` track hoga. User agar cancel karta hai, to backend par `cancellation_tokens[batch_id] = True` flag set hoga. Worker pool agle file ko pick karne se pehle is token ko check karega, jisse remaining files turant skip ho jayengi!

### 3.3 Frontend & Workstation UX
* **1:1 & 200% Deep Pixel Inspection Canvas:**
  * Mouse wheel se zoom in / zoom out (0.5x to 4x).
  * Mouse drag / touch drag se pan inside viewport.
  * Reset zoom button + 1:1 (100% actual pixel) toggle button.
* **Shortcuts & Input Wiring:**
  * `Space`: Toggle side-by-side vs. split slider in comparison modal.
  * `Ctrl+O`: Open File Dialog.
  * `Ctrl+S`: Save all / Save active.
  * `Ctrl+V`: Paste image from clipboard.
  * `Esc`: Close modals / blur inputs.
  * `Delete`: Remove selected item from queue.
  * `Enter`: Start compression batch.
* **Settings Persistence:**
  * `localStorage` keys for: `quality`, `output_format`, `resize_mode`, `resize_value`, `strip_metadata`, `lossless`, `optimize`.
* **Zero Leak Object URL Management:**
  * Dedicated `ObjectUrlRegistry` class jo `URL.createObjectURL` track karegi aur DOM replacement ya reset par systematic `URL.revokeObjectURL` execute karegi.
* **Responsive & Accessible CSS:**
  * Breakpoints for 820px, 1024px, 1280px, 1440px+.
  * WCAG AA contrast ratio compliance (>4.5:1 on all text).
  * Focus indicators (`:focus-visible`) for all interactive buttons and inputs.
  * ARIA attributes on split slider handle (`role="slider"`, `tabindex="0"`, `aria-valuenow`).

### 3.4 Packaging & Packaging Verification
* Remove `gunicorn` from `requirements.txt`.
* Pin exact versions in `requirements-desktop.txt`.
* Update PyInstaller specs (`PixelPress.spec`, `PixelPress-Portable.spec`) with clean metadata.
* Inno Setup 6 clean packaging with Start Menu and Desktop shortcuts.

---

## 4. SUCCESS CRITERIA & AUDIT SCORE TARGET

| Milestone | Target Score | Focus Areas |
| :--- | :---: | :--- |
| **Current Baseline** | **358 / 1000** | Prototype state with major architectural & security gaps |
| **Phase 1 Complete (Security & Fixes)** | **560 / 1000** | Token auth, name errors, duplicate routes, core unlocks |
| **Phase 2 Complete (Engine & Formats)** | **720 / 1000** | ICC profiles, GIF/WebP animation, CMYK, cancellation |
| **Phase 3 Complete (UI/UX & 1:1 Zoom)** | **860 / 1000** | Pixel zoom/pan, revokeObjectURL, space key, localStorage |
| **Phase 4 Complete (Tests, Docs & CI)** | **940 / 1000** | Full pytest suite, truthful docs, GitHub Actions, packaging |
