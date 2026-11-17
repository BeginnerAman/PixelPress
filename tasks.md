# PIXELPRESS DESKTOP PRO — ATOMIC TASK CHECKLIST

> **Document Version:** 1.0.0  
> **Tracker ID:** `PXPRO-TASK-MASTER`  
> **Status:** Pending Execution (Waiting for Phase 1 Trigger)

---

## 📌 MASTER TASK DIRECTORY

- [Phase 1: Security Hardening & Backend Hygiene](#phase-1-tasks-security-hardening--backend-hygiene)
- [Phase 2: Core Compression Engine & Multi-Format Integrity](#phase-2-tasks-core-compression-engine--multi-format-integrity)
- [Phase 3: Workstation UI/UX Overhaul & 1:1 Pixel Zoom](#phase-3-tasks-workstation-uiux-overhaul--11-pixel-zoom)
- [Phase 4: Automated Test Suite, CI/CD & Truthful Documentation](#phase-4-tasks-automated-test-suite-cicd--truthful-documentation)

---

## PHASE 1 TASKS: SECURITY HARDENING & BACKEND HYGIENE

### 1.1 Python Imports & Code Hygiene
- [x] `T1.1.1` **[app.py]** Add `import threading` at top-level imports (line 6–20) to resolve `NameError` in `window_close()`.
- [x] `T1.1.2` **[app.py]** Delete duplicate window control route declarations (lines 386–408: `win_drag`, `win_min`, `win_max`, `win_close`).
- [x] `T1.1.3` **[app.py]** Standardize remaining window controls (lines 921–983) and ensure error handling is clean and explicit.

### 1.2 Session Authentication & Anti-CSRF Gatekeeper
- [x] `T1.2.1` **[launcher.py]** Generate random high-entropy session auth token using `secrets.token_urlsafe(32)` at startup.
- [x] `T1.2.2` **[launcher.py]** Pass `auth_token` to Flask server thread and set `app.config['PIXELPRESS_AUTH_TOKEN'] = auth_token`.
- [x] `T1.2.3` **[app.py]** Inject `auth_token` into Flask `index` route render context (`render_template('index.html', auth_token=token)`).
- [x] `T1.2.4` **[app.py]** Create `before_request` hook that validates `request.headers.get('X-PixelPress-Token') == app.config['PIXELPRESS_AUTH_TOKEN']` for all `/api/*`, `/compress`, `/download/*`, `/window/*`, `/open-folder`, `/clear-workspace`, `/cleanup` endpoints. Whitelist only static assets (`/static/*`) and health check (`/health`).
- [x] `T1.2.5` **[templates/index.html]** Add `<meta name="pixelpress-token" content="{{ auth_token }}">` to document `<head>`.
- [x] `T1.2.6` **[static/js/main.js]** Create global `getAuthHeaders()` helper and attach `X-PixelPress-Token` header to every `fetch()` request (`/compress`, `/api/*`, `/window/*`, `/clear-workspace`, etc.).

### 1.3 Path Traversal Sandboxing & Route Hardening
- [x] `T1.3.1` **[app.py]** In `/api/reveal-file`, validate that requested `path` is an absolute canonical path located strictly inside `COMPRESSED_FOLDER` using `os.path.commonpath`. Return `403 Forbidden` for any other system path.
- [x] `T1.3.2` **[app.py]** In `/download/<filename>`, replace `os.path.join(COMPRESSED_FOLDER, filename)` and `send_file()` with `send_from_directory(COMPRESSED_FOLDER, secure_filename(filename))`.
- [x] `T1.3.3` **[app.py]** In `/original/<filename>`, `/preview/<filename>`, `/thumb/<filename>`, enforce `secure_filename()` to prevent directory traversal.

### 1.4 CPU Worker Thread Scaling
- [x] `T1.4.1` **[app.py]** Replace hardcoded `min(4, max(2, (os.cpu_count() or 4) // 2 or 2))` with dynamic scaling: `worker_count = max(2, min(os.cpu_count() or 4, 16))`.

### 1.5 Dependency Cleanup
- [x] `T1.5.1` **[requirements.txt]** Remove POSIX-only `gunicorn` package.
- [x] `T1.5.2` **[requirements-desktop.txt]** Pin stable versions: `Pillow>=10.4.0,<12.0.0`, `flask>=3.0.0,<3.2.0`, `pywebview>=5.1.0,<6.0.0`, `pyinstaller>=6.10.0`.

### Phase 1 Verification Checklist
- [x] `V1.1` Execute `python -m py_compile app.py launcher.py` (Zero syntax errors).
- [x] `V1.2` Start server, run `curl -X POST http://127.0.0.1:5000/clear-workspace` without token -> verify `403 Forbidden`.
- [x] `V1.3` Run curl with valid `X-PixelPress-Token` -> verify `200 OK`.
- [x] `V1.4` Test `/api/reveal-file` with `C:\Windows\System32` -> verify `403 Forbidden`.
- [x] `V1.5` Verify `window_close()` terminates process without `NameError`.

---

## PHASE 2 TASKS: CORE COMPRESSION ENGINE & MULTI-FORMAT INTEGRITY

### 2.1 Decompression Bomb & Memory Safety
- [x] `T2.1.1` **[app.py]** Set `Image.MAX_IMAGE_PIXELS = 250_000_000` to allow high-resolution photographic and panorama images.
- [x] `T2.1.2` **[app.py]** Wrap `Image.open` and processing in specific `Image.DecompressionBombError` handling to return clean JSON error instead of crashing.

### 2.2 ICC Color Profile Retention
- [x] `T2.2.1` **[app.py]** Extract `icc_profile = img.info.get('icc_profile')` prior to processing.
- [x] `T2.2.2` **[app.py]** Preserve `save_kwargs['icc_profile'] = icc_profile` for JPEG and PNG outputs when `strip_metadata=False`.

### 2.3 CMYK to RGB Perceptual Conversion
- [x] `T2.3.1` **[app.py]** In `compress_image()`, check `if img.mode == 'CMYK'`.
- [x] `T2.3.2` **[app.py]** Implement perceptual CMYK to RGB color conversion using `ImageCms` with sRGB profile fallback to prevent color inversion / neon discoloration.

### 2.4 Animated GIF Multi-Frame Preservation
- [x] `T2.4.1` **[app.py]** Detect animated GIF (`getattr(img, 'is_animated', False) and img.n_frames > 1`).
- [x] `T2.4.2` **[app.py]** Iterate through frames via `ImageSequence.Iterator(img)`, apply resize/palette, and save with `save_all=True`, `append_images=frames[1:]`, `duration=img.info.get('duration', 100)`, `loop=img.info.get('loop', 0)`.

### 2.5 Animated WebP Multi-Frame Preservation
- [x] `T2.5.1` **[app.py]** Detect multi-frame WebP and preserve all frames on save with `save_all=True`, `append_images=frames[1:]`, `duration`, `loop`.

### 2.6 Backend Cancellation Protocol
- [x] `T2.6.1` **[app.py]** Create `active_batches = {}` registry with batch UUID tracking.
- [x] `T2.6.2` **[app.py]** Add `/api/cancel-batch/<batch_id>` endpoint to mark batch as cancelled.
- [x] `T2.6.3` **[app.py]** In `_run_single()`, check `if active_batches.get(batch_id, {}).get('cancelled')`: skip processing immediately.
- [x] `T2.6.4` **[static/js/main.js]** Generate `currentBatchId` on compression start and call `/api/cancel-batch/${currentBatchId}` on cancel button click.

### Phase 2 Verification Checklist
- [x] `V2.1` Test compressing a 10-frame animated GIF -> verify output GIF still animates.
- [x] `V2.2` Test compressing an animated WebP -> verify multi-frame retention.
- [x] `V2.3` Test compressing a CMYK JPEG -> verify RGB output has realistic colors (no invert).
- [x] `V2.4` Test image with Display-P3 ICC profile -> verify profile is preserved in output.
- [x] `V2.5` Test batch cancellation midway -> verify worker thread skips remaining tasks.

---

## PHASE 3 TASKS: WORKSTATION UI/UX OVERHAUL & 1:1 PIXEL ZOOM

### 3.1 1:1 (100%) and 200% Pixel Peeping Zoom & Pan Canvas
- [x] `T3.1.1` **[templates/index.html]** Add Zoom toolbar controls inside `#compare-modal` (`Fit`, `1:1 (100%)`, `200%`, `Zoom Level %`, `Reset`).
- [x] `T3.1.2` **[static/css/style.css]** Style zoom viewport, pan cursor (`grab` / `grabbing`), and responsive zoom container.
- [x] `T3.1.3` **[static/js/main.js]** Implement `ZoomPanEngine` for comparison images:
  * Mouse wheel event: zoom in/out centered at mouse cursor position (scale range 0.25x to 4.0x).
  * Mouse drag / touch drag: pan image smoothly with `requestAnimationFrame`.
  * Synchronize zoom scale and pan offsets between Original and Compressed images.
  * Reset zoom on modal open/close.

### 3.2 Space Key Shortcut Wiring
- [x] `T3.2.1` **[static/js/main.js]** In `keydown` event listener, handle `e.code === 'Space'`. If compare modal is visible and no input is focused, `e.preventDefault()` and toggle between Side-by-Side and Split Slider mode.

### 3.3 Settings Persistence via `localStorage`
- [x] `T3.3.1` **[static/js/main.js]** Create `saveUserPreferences()` that saves `quality`, `output_format`, `resize_mode`, `resize_value`, `strip_metadata`, `lossless`, `optimize` to `localStorage.setItem('pixelpress_settings', ...)`.
- [x] `T3.3.2` **[static/js/main.js]** Create `loadUserPreferences()` on DOMContentLoaded that restores user controls from `localStorage`.
- [x] `T3.3.3` **[static/js/main.js]** Attach change listeners to all settings inputs to trigger `saveUserPreferences()`.

### 3.4 Zero-Leak Object URL Registry
- [x] `T3.4.1` **[static/js/main.js]** Create `const objectUrlRegistry = new Set()` in client state.
- [x] `T3.4.2` **[static/js/main.js]** Wrap `URL.createObjectURL(file)` in helper that registers URL in `objectUrlRegistry`.
- [x] `T3.4.3` **[static/js/main.js]** Call `revokeAllObjectUrls()` on `renderQueue()`, `removeFile()`, and `clearQueue()`.

### 3.5 Responsive Layout & WCAG AA Accessibility
- [x] `T3.5.1` **[static/css/style.css]** Add `@media (max-width: 960px)` and `@media (max-width: 820px)` queries for window resizing.
- [x] `T3.5.2` **[static/css/style.css]** Elevate `--text-faint` from `#565968` to `#7c8094` for WCAG AA compliance (4.8:1 contrast).
- [x] `T3.5.3` **[static/css/style.css]** Add accessible `:focus-visible` styling with high-contrast accent ring.
- [x] `T3.5.4` **[templates/index.html & static/js/main.js]** Add `tabindex="0"`, `role="slider"`, `aria-valuenow`, `aria-label="Before/After Split Comparison"` to split handle, with `ArrowLeft` / `ArrowRight` key adjustments.
- [x] `T3.5.5` **[static/css/style.css]** Add `@media (prefers-reduced-motion: reduce)` block to disable transition delays for motion-sensitive users.

### 3.6 Queue View Drag-and-Drop Indicator
- [x] `T3.6.1` **[static/js/main.js]** Fix dragover state so that dragging files while in `queue` view highlights queue border and shows drop overlay.

### Phase 3 Verification Checklist
- [x] `V3.1` Test mouse wheel zoom in compare modal: zooms up to 400% smoothly.
- [x] `V3.2` Test mouse drag pan: image pans smoothly without jumping.
- [x] `V3.3` Press `Space` in modal: toggles between Split Slider and Side-by-Side.
- [x] `V3.4` Change settings, reload page: verify all settings persist.
- [x] `V3.5` Add/delete 50 images in queue: verify all Object URLs are revoked without memory leak.
- [x] `V3.6` Resize window to 820x500: verify layout adjusts without overflow clipping.

---

## PHASE 4 TASKS: AUTOMATED TEST SUITE, CI/CD & TRUTHFUL DOCUMENTATION

### 4.1 Pytest Automated Test Suite
- [x] `T4.1.1` **[tests/conftest.py]** Create pytest fixtures (Flask test client, dummy test images in RGB, RGBA, CMYK, animated GIF, wide-gamut P3).
- [x] `T4.1.2` **[tests/test_security.py]** Write tests verifying:
  * Unauthenticated requests to protected endpoints return 403.
  * Authenticated requests succeed.
  * Directory traversal on `/download/..` is blocked.
  * Path escape on `/api/reveal-file` is blocked.
- [x] `T4.1.3` **[tests/test_compression.py]** Write tests verifying:
  * JPEG compression with quality and subsampling.
  * PNG quantization with FASTOCTREE and lossless flag.
  * WebP compression.
  * Animated GIF frame count preservation.
  * CMYK conversion without color inversion.
  * ICC profile preservation.
  * Resizing modes (percentage, width, height, custom).
- [x] `T4.1.4` **[tests/test_storage.py]** Write tests verifying:
  * Storage root resolution (`%LOCALAPPDATA%` vs portable marker).
  * Cleanup routine removes expired files safely.

### 4.2 GitHub Actions CI/CD Pipeline
- [x] `T4.2.1` **[.github/workflows/ci.yml]** Create GitHub Actions workflow:
  * Matrix: Windows runner, Python 3.11, 3.12, 3.13.
  * Steps: Install dependencies, run `pytest tests/`, check syntax, test PyInstaller build packaging.

### 4.3 Documentation Rewrite & Truthful Alignment
- [x] `T4.3.1` **[README.md]** Replace "O(1) Constant Memory" claim with truthful explanation: "Bounded Chunked Streaming Memory Pipeline" with realistic memory profiling table.
- [x] `T4.3.2` **[README.md]** Replace "Sub-200ms cold startup" with honest measured benchmarks (~1.1s directory bundle, ~3.2s standalone EXE).
- [x] `T4.3.3` **[README.md]** Update benchmark comparison table with honest, defensible figures.
- [x] `T4.3.4` **[README.md]** Add Code-Signing and SmartScreen mitigation documentation.
- [x] `T4.3.5` **[README_DESKTOP.md]** Update internal architecture guide to reflect true session auth, token gatekeeper, and zoom engine.

### 4.4 Build & Packaging Verification
- [x] `T4.4.1` **[build.bat]** Test run PyInstaller build for portable EXE and directory bundle.
- [x] `T4.4.2` **[installer.iss]** Verify Inno Setup compiler builds `PixelPress_Setup.exe` cleanly.

### Phase 4 Verification Checklist
- [x] `V4.1` Run `pytest -v tests/` -> 100% tests pass.
- [x] `V4.2` GitHub Actions CI yaml validated.
- [x] `V4.3` Full README review: Zero fabricated claims remain.
- [x] `V4.4` Compiled binary executes cleanly without errors.
