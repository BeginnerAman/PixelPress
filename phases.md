# PIXELPRESS DESKTOP PRO — PHASED ROADMAP & EXECUTION PROTOCOL

> **Document Version:** 1.0.0  
> **Rule of Engagement:** Ek waqt par sirf EK Phase execute hoga. Phase complete hone ke baad thorough automated aur manual testing hogi, aur phir agle phase ke liye User confirmation ka wait kiya jayega.

---

## ROADMAP OVERVIEW

```
  ┌──────────────────────────────────────────────────────────────┐
  │  PHASE 1: Security Hardening & Backend Hygiene               │
  │  (Token Auth, Path Sandboxing, Dead Code, Core Scaling)     │
  └──────────────────────────────┬───────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  PHASE 2: Compression Engine & Format Integrity              │
  │  (ICC Profiles, Animated GIF/WebP, CMYK, True Cancel)       │
  └──────────────────────────────┬───────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  PHASE 3: Workstation UI/UX & 1:1 Pixel Peeping Zoom         │
  │  (Zoom/Pan, Space Key, RevokeObjectURL, LocalStorage)       │
  └──────────────────────────────┬───────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  PHASE 4: Test Suite, CI/CD & Truthful Documentation         │
  │  (Pytest Suite, GitHub Actions CI, Truthful Benchmarks)      │
  └──────────────────────────────────────────────────────────────┘
```

---

## PHASE 1: SECURITY HARDENING & BACKEND HYGIENE
**Primary Goal:** Localhost attack vectors ko seal karna, dead/broken code fix karna, CPU cores unlock karna, aur clean dependency environment banana.

### Scope:
1. **Import & Syntax Fixes:**
   * `app.py`: Top par `import threading` add karna taaki line 980 par `window_close()` mein `NameError` crash na ho.
   * `app.py`: Lines 386–408 se duplicate `/window/*` route definitions delete karna.
2. **Session Authentication Handshake (Anti-CSRF / Anti-Rebinding):**
   * `launcher.py`: Launch time par cryptographic random auth token generate karna (`secrets.token_urlsafe(32)`).
   * Token ko Flask config (`app.config['AUTH_TOKEN']`) aur template render context mein inject karna.
   * `app.py`: Flask `before_request` hook implement karna jo static assets aur `/health` ko chhodkar har sensitive endpoint par `X-PixelPress-Token` header validate kare. Invalid/missing token par turant `403 Forbidden` throw kare.
   * `templates/index.html` & `static/js/main.js`: Token ko window level par stage karna aur har `fetch` call mein `X-PixelPress-Token` header attach karna.
3. **Path Traversal & Sandboxing:**
   * `/api/reveal-file`: Strict check enforce karna ki requested path hamesha `COMPRESSED_FOLDER` ke inside ho. Arbitrary system file paths ko probe ya open karne ki permission na ho.
   * `/download/<filename>`: `send_file(os.path.join(...))` ko replace karke `send_from_directory(COMPRESSED_FOLDER, secure_filename(filename))` lagana.
4. **Worker Core Dynamic Scaling:**
   * Hard-coded `min(4, ...)` formula ko replace karke dynamic scaling lagana: `min(os.cpu_count() or 4, 16)`.
5. **Clean Dependency Environment:**
   * `requirements.txt`: Linux-only `gunicorn` package ko permanently remove karna.
   * `requirements-desktop.txt`: Dependencies ko production-tested versions par clean format mein configure karna.

### Acceptance & Testing Criteria:
* [ ] External `curl` without token returns `403 Forbidden` for all protected endpoints.
* [ ] Internal UI fetches pass valid token and succeed with `200 OK`.
* [ ] `/api/reveal-file` with `C:\Windows\System32` returns `403 Forbidden`.
* [ ] Window close button executes cleanly without `NameError`.
* [ ] 8-core CPU detects and runs up to 8 threads during compression.

---

## PHASE 2: COMPRESSION ENGINE & MULTI-FORMAT INTEGRITY
**Primary Goal:** Compression engine ko pro-photographer grade reliability dena—ICC profiles preserve karna, animations retain karna, CMYK colors skew na hona, aur large images par crash rokna.

### Scope:
1. **Decompression Bomb Protection:**
   * `Image.MAX_IMAGE_PIXELS = 250_000_000` set karna.
   * Decompression bomb catch block add karna taaki informative error mile aur app crash na ho.
2. **ICC Color Profile Preservation:**
   * JPEG aur PNG compression pipeline mein original image ka `icc_profile = img.info.get('icc_profile')` extract karna.
   * Agar ICC profile present hai, to save karte waqt `save_kwargs['icc_profile'] = icc_profile` pass karna (Display P3 / Adobe RGB color shift prevention).
3. **CMYK to RGB High-Fidelity Conversion:**
   * CMYK images ke liye direct `img.convert('RGB')` ko safe conversion routine se replace karna (using Pillow CMS or calibrated perceptual transform) taaki neon / inverted color shifts na hon.
4. **Animated GIF & Animated WebP Multi-Frame Engine:**
   * Input image check karna: `getattr(img, "is_animated", False) and img.n_frames > 1`.
   * Agar animated hai, to `ImageSequence.Iterator(img)` ke through har frame ko process karke `save_all=True`, `append_images=frames[1:]`, `duration=img.info.get('duration')`, `loop=img.info.get('loop', 0)` ke saath save karna.
5. **True Backend Cancellation Protocol:**
   * Backend par `active_batches` dictionary aur cancellation flags track karna.
   * UI jab cancel kare, to `/api/cancel-batch` endpoint backend token set karega.
   * Worker threads har image process karne se pehle cancel flag check karke turant remaining batch ko discard kar denge.

### Acceptance & Testing Criteria:
* [ ] Animated GIF compress hone ke baad bhi multi-frame animation retain karta hai.
* [ ] Animated WebP multi-frame animation retain karta hai.
* [ ] CMYK JPEG convert hone par normal natural colors show karta hai (no color inversion).
* [ ] Display-P3 color profile wali photos compressed hone ke baad color integrity maintain karti hain.
* [ ] 100-file batch cancel karne par background threads agle files process karna band kar dete hain.

---

## PHASE 3: WORKSTATION UI/UX OVERHAUL & 1:1 PIXEL ZOOM
**Primary Goal:** Desktop workstation ki visual inspection capabilities ko elevate karna—true 1:1 pixel peeping zoom, keyboard accessibility, zero memory leaks, aur responsive layout.

### Scope:
1. **1:1 (100%) & 200% Pixel Peeping Zoom & Pan Canvas:**
   * Comparison Modal mein deep zoom & pan engine implement karna:
     * Mouse wheel se smooth zoom (0.5x, 1x, 2x, 4x).
     * Drag-to-pan jab image viewport se badi ho.
     * Quick action buttons: `Fit (100% Fit)`, `1:1 (Actual Pixels)`, `200% Zoom`.
     * Split slider aur side-by-side dono modes mein zoom coordinate synchronization.
2. **Missing `Space` Shortcut Wiring:**
   * `keydown` listener mein `e.code === 'Space'` implement karna: modal open hone par Side-by-Side aur Split Slider views ke beech instantaneous toggle.
3. **Settings Persistence via `localStorage`:**
   * Quality slider, output format, resize dropdown & inputs, strip metadata, lossless, optimize toggles ko `localStorage` mein auto-save aur restore karna.
4. **Zero-Leak Object URL Registry:**
   * Client-side `ObjectUrlRegistry` create karna jo generated `URL.createObjectURL` references ko store kare aur re-render, file removal, aur workspace reset par `URL.revokeObjectURL` call kare.
5. **Responsive Layout & WCAG AA Accessibility:**
   * CSS `@media` queries add karna for 820px min-width screens (auto-adjust sidebar and action toolbars).
   * `--text-faint` contrast ratio elevate karna from `#565968` (3.2:1) to `#7c8094` (4.8:1) to achieve WCAG AA compliance.
   * Accessible `:focus-visible` outline rings add karna.
   * Split handle par ARIA attributes (`role="slider"`, `tabindex="0"`, `aria-valuenow`, `aria-valuemin="0"`, `aria-valuemax="100"`) aur Arrow Left / Right key handling implement karna.
   * `@media (prefers-reduced-motion: reduce)` support add karna.
6. **Queue Drag-and-Drop Affordance:**
   * Jab queue section visible ho, tab bhi window-level file drag par visible drop indicator show karna.

### Acceptance & Testing Criteria:
* [ ] User comparison modal mein mouse wheel se 1:1 pixel level tak zoom aur pan kar sakta hai.
* [ ] Spacebar dabane par Side-by-Side se Split Slider toggle hota hai.
* [ ] App reload karne par user ke quality slider aur options restore hote hain.
* [ ] DevTools Memory timeline mein 100 files add/remove karne par Object URL memory leak zero rehti hai.
* [ ] Screen-reader / keyboard navigation se slider ko left/right arrow keys se adjust kiya ja sakta hai.

---

## PHASE 4: AUTOMATED TEST SUITE, CI/CD & TRUTHFUL DOCUMENTATION
**Primary Goal:** Quality assurance automate karna, production builds verify karna, aur documentation ko 100% truthful aur reliable banana.

### Scope:
1. **Automated `pytest` Test Suite:**
   * `tests/test_compression.py`:
     * Test JPEG progressive DCT & chroma subsampling.
     * Test PNG adaptive quantization & lossless mode.
     * Test WebP method-4 encoding.
     * Test Animated GIF multi-frame retention.
     * Test CMYK color conversion.
     * Test ICC profile preservation.
     * Test Decompression Bomb limits.
   * `tests/test_security.py`:
     * Test unauthenticated access rejection (403).
     * Test valid auth token acceptance (200).
     * Test path traversal attacks on `/download` and `/api/reveal-file`.
   * `tests/test_api.py`:
     * Test batch queue API, save single, save all, clear workspace.
2. **GitHub Actions CI/CD Pipeline:**
   * `.github/workflows/ci.yml`:
     * Python 3.11, 3.12, 3.13 matrix testing.
     * Automated pytest run.
     * PyInstaller automated build dry-run for Windows.
3. **Truthful Documentation Rewrite:**
   * `README.md` & `README_DESKTOP.md`:
     * "O(1) constant memory" ko replace karke accurate "Bounded Chunked Streaming Memory Pipeline" likhna with exact RAM metrics.
     * "Sub-200ms cold startup" ko realistic benchmarks se replace karna (Directory bundle ~1.1s, Portable EXE ~3.2s).
     * Updated accurate benchmark table publish karna.
     * Code signing / SmartScreen setup guide include karna.
4. **Build Pipeline Sanity:**
   * `build.bat` test run karna, PyInstaller output verify karna, Inno Setup installer generate karke test karna.

### Acceptance & Testing Criteria:
* [ ] `pytest tests/` 100% pass rate ke saath execute hota hai.
* [ ] GitHub Actions workflow syntax verified.
* [ ] README mein koi bhi exaggerated ya false claim nahi bachta.
* [ ] Clean standalone binary successfully builds and launches.
