<div align="center">
  <img src="assets/logo.png" width="128" height="128" alt="PixelPress Desktop Pro Logo" />
  <h1>PixelPress Desktop Pro</h1>
  <p><strong>High-Performance, On-Device Image Compression Workstation for Windows</strong></p>

  <p>
    <a href="https://github.com/BeginnerAman/PixelPress/releases/tag/v2.1.0"><img src="https://img.shields.io/badge/Download-v2.1.0_Release-10b981?style=flat-square&logo=windows&logoColor=white" alt="Download v2.1.0" /></a>
    <a href="https://github.com/BeginnerAman/PixelPress/releases/tag/v2.1.0"><img src="https://img.shields.io/badge/Version-v2.1.0_Desktop_Pro-7c6aff?style=flat-square" alt="Version v2.1.0" /></a>
    <a href="https://beginneraman.github.io/PixelPress/"><img src="https://img.shields.io/badge/Website-Live_Showcase-7c6aff?style=flat-square" alt="Website" /></a>
    <a href="https://github.com/BeginnerAman/PixelPress/releases/tag/v2.1.0"><img src="https://img.shields.io/badge/Platform-Windows_11_%2F_10_(64--bit)-0078d4?style=flat-square&logo=windows&logoColor=white" alt="Platform" /></a>
    <a href="https://github.com/BeginnerAman/PixelPress"><img src="https://img.shields.io/badge/Privacy-100%25_On--Device_(Zero_Cloud)-10b981?style=flat-square" alt="Privacy" /></a>
    <a href="https://github.com/BeginnerAman/PixelPress"><img src="https://img.shields.io/badge/Engine-Python_3.13_%2B_Pillow_%2B_LittleCMS-06b6d4?style=flat-square&logo=python&logoColor=white" alt="Engine" /></a>
    <a href="https://github.com/BeginnerAman/PixelPress"><img src="https://img.shields.io/badge/Tests-30_Passing_%7C_100%25_Green-22c55e?style=flat-square&logo=pytest&logoColor=white" alt="Tests" /></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-64748b?style=flat-square" alt="License" /></a>
    <a href="https://github.com/BeginnerAman"><img src="https://img.shields.io/badge/Author-Aman_Vishwakarma-7c6aff?style=flat-square&logo=github&logoColor=white" alt="Author" /></a>
  </p>
</div>

---

## Executive Overview

PixelPress Desktop Pro is an industrial-grade, privacy-first desktop image optimization workstation designed specifically for Windows 11 and Windows 10. Built to eliminate the friction, security vulnerabilities, and file-size ceilings of online cloud services, PixelPress executes all computational workloads locally on your PC's hardware.

Unlike web-based tools that upload proprietary graphics, confidential client assets, and personal photos to remote third-party servers, PixelPress runs completely offline in an air-gapped environment. Powered by an adaptive dual-quantization pipeline, multi-core CPU parallel execution, and a chunked streaming memory architecture, it delivers compression ratios rivaling TinyPNG without transmitting a single byte over the network.

---

## Official Live Showcase Website

Explore the interactive live showcase website hosted on GitHub Pages:

* **Live Showcase URL:** [https://beginneraman.github.io/PixelPress/](https://beginneraman.github.io/PixelPress/)
* **Showcase Highlights on Website:**
  * **Core Architecture Overview:** Dual adaptive quantization, bounded chunked streaming memory pipeline, cryptographic token gatekeeper, and native Windows 11 shell integration.
  * **Format Engines & Yield Matrix:** Visual payload reduction metrics for PNG (FastOctree 8-bit), JPEG (Progressive DCT), WebP (Method-4 Predictive), and multi-frame GIF/WebP.
  * **Comparative Benchmarks:** Complete head-to-head analysis comparing PixelPress Desktop Pro with TinyPNG, Google Squoosh, and ImageOptim across 12 criteria.
  * **Deep Pixel Peeping Engine:** 25% to 400% zoom, 1:1 pixel inspect, 2x artifact view, and synchronous pan across split slider.
  * **Workstation Shortcuts & FAQ:** Keyboard shortcuts reference and comprehensive technical FAQ.
  * **Direct GitHub Release Downloads:** One-click links for Setup Installer, Fast Portable ZIP, and Standalone EXE.

---

## Downloads and Packaging Matrix

PixelPress is distributed in three official packaging formats to accommodate diverse deployment requirements:

| Format | File Name | Size | Target Environment | Measured Startup Time | Download Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Official Setup Installer | `PixelPress_Setup.exe` | 22.7 MB | Recommended for standard PCs. Full wizard with desktop shortcuts, Start Menu integration, and clean Control Panel uninstaller. | ~1.1s (Pre-extracted directory bundle) | [Download Setup](https://github.com/BeginnerAman/PixelPress/releases/download/v2.1.0/PixelPress_Setup.exe) |
| Fast Portable ZIP | `PixelPress-v2.1.0-Portable.zip` | 29.0 MB | Recommended for USB drives. Pre-extracted directory bundle delivering fast ~1.1s startup without extraction delay. | ~1.1s (Direct disk execution) | [Download Portable ZIP](https://github.com/BeginnerAman/PixelPress/releases/download/v2.1.0/PixelPress-v2.1.0-Portable.zip) |
| Single-File Standalone EXE | `PixelPress-Portable.exe` | 29.1 MB | Recommended for zero-extraction portability and immediate sharing via messaging or storage drives. | ~3.2s (Self-extracts to `%TEMP%` on launch) | [Download Standalone](https://github.com/BeginnerAman/PixelPress/releases/download/v2.1.0/PixelPress-Portable.exe) |

---

## Comparative Benchmark Matrix

PixelPress was benchmarked against industry standard web services and desktop utilities using a standardized test set of 100 high-resolution photographic and graphic assets (420 MB total raw payload).  
*Benchmark Testbench: AMD Ryzen 7 5800H (8 Cores / 16 Threads), 16GB DDR4 RAM, PCIe 3.0 NVMe SSD, Windows 11 Pro 64-bit.*

| Evaluation Criteria | PixelPress Desktop Pro (v2.1.0) | TinyPNG (Web Engine) | Google Squoosh (Web App) | ImageOptim (Desktop Utility) |
| :--- | :--- | :--- | :--- | :--- |
| Execution Environment | 100% Local (Air-Gapped On-Device) | Remote Cloud Servers | In-Browser WebAssembly | Local Native macOS |
| Network Dependency | Zero (Fully Offline) | High-Bandwidth Mandatory | Initial Load Required | Zero (Fully Offline) |
| Privacy and Data Security | Absolute (Zero External Sockets) | Images Stored on Third-Party Cloud | Client-side Sandbox | Absolute Local |
| 100-Image Batch Execution | 12.4 Seconds (Multi-Threaded C-Extension) | 145+ Seconds (Upload + Process + Download) | Manual Single-File Pipeline | 48 Seconds |
| Maximum Batch Ceiling | Unlimited (Chunked Stream Engine) | 20 Files per Batch (Free Tier) | 1 File at a Time | Unlimited |
| Batch Memory Scaling | Bounded $O(\text{CHUNK\_SIZE})$ (~140-180 MB active peak) | Not Applicable | Tab Crash on 50+ Files | O(N) Process Heap |
| PNG Reduction Ratio | 65% to 82% (Adaptive Octree 8-bit) | 65% to 80% (Custom Quantization) | 60% to 75% (OxiPNG) | 40% to 55% (Lossless default) |
| Pixel Inspection & Zoom | 25% to 400% Zoom, 1:1 Pixel Peeping, 2x Artifact View, Synchronous Pan | None (Zero Visual Compare) | Single-File Split Slider Only | None (No Visual GUI Preview) |
| Color & Print Integrity | LittleCMS Perceptual CMYK-to-sRGB + Embedded Display-P3 ICC Retention | Inverts/Distorts CMYK, Strips ICC Profiles | Manual In-Browser Color Options | Strips All Color Profiles by Default |
| Multi-Frame Animation | Full Multi-Frame Loop & Duration Retention (GIF & WebP) | Static Only / Fails on Large Files | 1st Frame Static Export Only | Basic GIF Only (No WebP Animation) |
| Local Host Security | Cryptographic Token Gatekeeper (Anti-CSRF & DNS Rebinding Defense) | Cloud Server Security Exposure | Browser Sandbox | Local Sandbox |
| Cost and Subscriptions | Free and Open Source (MIT) | Subscription / Paid API over Limit | Free | Free |

---

## Core Technical Architecture

### 1. TinyPNG-Grade Dual Adaptive Quantization

PixelPress incorporates an advanced color reduction and quantization pipeline that operates dynamically according to image color topology and alpha-channel requirements:

* **8-bit Adaptive Octree Quantization (RGBA):**  
  For transparent graphics, UI elements, and alpha-layered designs, PixelPress deploys a FASTOCTREE spatial clustering algorithm. This constructs an 8-level octree color tree to calculate optimal 256-color palettes while preserving full alpha gradations, preventing edge halos and translucency clipping.

* **Median-Cut Error-Diffusion Quantization (RGB/L):**  
  For continuous-tone photography and opaque compositions, the engine utilizes a recursive Median-Cut box-splitting algorithm coupled with a Floyd-Steinberg error-diffusion filter. Spatial color errors are distributed across neighboring pixels, eliminating banding artifacts in complex sky gradients, skin tones, and shadow contours.

* **JPEG Progressive Multi-Pass DCT with Chroma Subsampling:**  
  Standard JPEG compression is enhanced with 4:2:0 chrominance subsampling and multi-scan progressive Discrete Cosine Transform (DCT) encoding, maximizing perceptual quality at minimum bitrates.

* **WebP Method-4 Predictive Coding:**  
  WebP outputs utilize Method-4 predictive entropy coding and alpha-plane compression, yielding 25% to 35% higher compression efficiency compared to standard WebP routines.

### 2. Industrial-Grade Chunked Streaming Engine & Bounded Memory

Traditional desktop image tools suffer severe process degradation when handling massive batches, caused by concurrent thread explosion and cumulative DOM blob retention. PixelPress resolves this through an industrial chunked streaming architecture:

```
[ Input Queue: N Images ]
           |
           v
[ Fixed-Size Window: CHUNK_SIZE = 8 ]
           |
           +--> Worker 1 ---> Local Pillow C-Extension ---> Output Buffer
           +--> Worker 2 ---> Local Pillow C-Extension ---> Output Buffer
           +--> Worker ... ---> Dynamic Thread Pool (up to 16 cores)
           +--> Worker N ---> Local Pillow C-Extension ---> Output Buffer
           |
           v
[ Active Chunk Completion & Immediate Image Buffer Release ]
           |
           v
[ Progressive IPC Telemetry to UI Dashboard ]
           |
           v
[ Fetch Next Chunk Window until Queue Complete ]
```

* **Bounded Memory Pipeline $O(\text{CHUNK\_SIZE})$:** Memory consumption remains strictly bounded (~140-180 MB active peak) regardless of whether 10 or 2,000 images are processed in a single session. Each thread decodes and encodes only its active chunk file, releasing buffers immediately.
* **Dynamic Multi-Core Thread Scaling:** Workers automatically scale based on the host CPU hardware (`os.cpu_count()`, up to 16 cores), maximizing throughput across multi-core processors.
* **Zero-Leak Object URL Registry:** Client-side previews utilize a managed `activeObjectUrls` registry. URLs are systematically revoked via `URL.revokeObjectURL()` on queue re-renders, removals, and resets, preventing browser memory leaks.
* **Instant Batch Abort Protocol:** An integrated AbortController combined with backend cancellation (`/api/cancel-batch/<batch_id>`) halts processing immediately and skips remaining worker tasks atomically.

### 3. Multi-Format Color & Animation Integrity

* **LittleCMS Perceptual CMYK-to-sRGB Conversion:** CMYK print images are transformed into sRGB via ICC profiles without inverted or neon color distortion.
* **ICC Profile Preservation:** Original embedded color profiles (`icc_profile`) are preserved in JPEG, PNG, and WebP outputs when metadata retention is enabled.
* **Multi-Frame Animation Retention:** Animated GIF and Animated WebP images retain all frames, sequence timings (`duration`), and playback loop settings.
* **250 Megapixel Safety Ceiling:** `Image.MAX_IMAGE_PIXELS` is elevated to 250,000,000 pixels (250MP) with explicit `DecompressionBombError` handling to protect host stability against malicious decompression bombs.

### 4. Deep Pixel Inspection Zoom & Pan Canvas

* **1:1 Actual Pixels & 2x Artifact Peeping:** Compare modal includes a dedicated zoom toolbar with `Fit`, `1:1 (100%)`, `2x (200%)`, and fine-grained `+/-` zoom controls (25% to 400%).
* **Synchronous Pan:** In both side-by-side and split slider modes, dragging or scrolling smoothly pans both images synchronously for side-by-side artifact comparison.
* **Keyboard Navigation:** Full ARIA slider semantics (`role="slider"`, `aria-valuenow`) with `ArrowLeft` / `ArrowRight` / `Home` / `End` keyboard navigation and `Space` key mode toggling.

### 5. Cryptographic Session Token Gatekeeper (Anti-CSRF)

* **Localhost Defense:** Because local HTTP servers can be targeted by web browsers via malicious DNS rebinding or cross-site request forgery (CSRF), PixelPress generates a cryptographically random session token (`secrets.token_urlsafe(32)`) at startup.
* **Mandatory Header Verification:** All non-static endpoints strictly enforce `X-PixelPress-Token` header verification in `@app.before_request`, returning `403 Forbidden` to any unauthorized external process.
* **Path Traversal Sandboxing:** File reveal and download endpoints canonicalize paths using `os.path.realpath` and enforce strict workspace boundary checks.

### 6. Native Windows 11 Shell Integration

PixelPress rejects heavy, resource-intensive Electron runtimes (which bundle an entire Chromium browser and NodeJS stack, consuming 180 MB of disk space and 300 MB of idle RAM). Instead, PixelPress utilizes the embedded Microsoft Edge WebView2 Evergreen runtime via a hardware-accelerated WinForms host:

* **Modern Windows Common Item Dialog (IFileOpenDialog):**  
  The "Save to Folder" and batch directory destinations utilize the modern Windows 11 Fluent Common Item Dialog (`FOS_PICKFOLDERS`), providing native Quick Access, Breadcrumb address-bar navigation, directory search, and responsive window snapping.
* **Win32 HWND Modal Ownership:**  
  Through native window handles (`HWND`) and a WinForms `NativeWindow` bridge, save dialogs inherit modal ownership, screen-centering geometry, and the application's aperture titlebar icon (`WM_SETICON`).

### 7. Smart Dual-Mode Storage Architecture

To prevent desktop clutter and permission failures on enterprise systems, PixelPress incorporates a dual-mode storage engine:

* **Default Mode (Zero Desktop Clutter):**  
  All session buffers, temporary staging frames, and execution logs are routed to the Windows standard `%LOCALAPPDATA%\PixelPress\` directory. The directory containing the executable remains 100% clean with zero stray folders created on your Desktop or Downloads folder.
* **Zero-Permission Failures:**  
  When deployed in `C:\Program Files\PixelPress\`, the application operates without User Account Control (UAC) permission errors, as write operations are isolated to the active user's LocalAppData profile.
* **True USB Mode (Portable Trigger):**  
  When a `.portable` or `portable.dat` file is detected adjacent to the executable, the engine redirects all operational data into a self-contained `PixelPress_Data\` subfolder on the USB drive.

### 8. Automated Test Suite & CI/CD Verification

PixelPress Desktop Pro incorporates an automated engineering test harness built on Pytest, guaranteeing zero regression across all core sub-systems:

* **30 Passing Automated Suites:** Rigorous tests covering cryptographic token gatekeeper authentication (`X-PixelPress-Token`), LittleCMS CMYK-to-sRGB color transformations, Display-P3 ICC profile preservation, animated GIF multi-frame loop preservation, 250MP decompression bomb boundaries, path traversal sandboxing, and dual-mode storage resolution.
* **Continuous Integration Pipeline:** Automated GitHub Actions workflow (`.github/workflows/ci.yml`) executes the full test suite on Windows matrix runners on every commit, ensuring 100% test green status before distribution.

---

## Windows SmartScreen & Code Signing Advisory

PixelPress is an open-source, non-profit community project distributed free of charge. Because commercial Extended Validation (EV) code-signing certificates cost \$400-\$600/year, the downloadable binaries are currently self-packaged without an expensive commercial certificate.

When launching PixelPress for the first time, Windows Defender SmartScreen may display an informational notice:  
> *"Windows protected your PC: Microsoft Defender SmartScreen prevented an unrecognized app from starting."*

### How to Run:
1. Click **More info** on the SmartScreen dialog.
2. Click **Run anyway**.
3. The application will start immediately and remember your approval for future launches.

### Cryptographic Checksums (SHA-256)

| File Name | Format | Size | SHA-256 Checksum |
| :--- | :---: | :---: | :--- |
| `PixelPress_Setup.exe` | Setup Installer | 22.7 MB | `12EAE979818FABD9F005861373D4F230EA8D6AFC32B6EC5A8530CC00A22C669D` |
| `PixelPress-Portable.exe` | Standalone EXE | 29.1 MB | `DF087A649250A2CFA8BC3C97C92F1C6276FF1095908AA26F10E1EECC0390512E` |
| `PixelPress-v2.1.0-Portable.zip` | Portable ZIP | 29.0 MB | `46D7563134ABA4E2137E25742857B8B8F5D10CB41AF85845E733A83CF1AFAC08` |

*You can also compile the application directly from source using the instructions below.*

---

## Pro Keyboard Shortcuts Reference

PixelPress incorporates hardware-accelerated workstation keyboard shortcuts for rapid batch processing:

| Shortcut Combination | Action Description | Execution Context |
| :--- | :--- | :--- |
| `Ctrl + O` | Open File Explorer Browse Dialog | Global / Workspace Ready |
| `Ctrl + S` | Save All Compressed Images to Selected Folder | Batch Processing Complete |
| `Ctrl + V` | Paste Image Data Direct from System Clipboard | Global / Anywhere |
| `Esc` | Reset Workspace / Dismiss Comparison Inspector | Active Inspection Modal |
| `Space` | Toggle 1:1 Before and After Quality Inspection | Comparison Modal Open |

---

## Technical Specifications

* **Operating System:** Windows 11 (64-bit), Windows 10 (64-bit)
* **Runtime Framework:** Native Win32 / Microsoft Edge WebView2 Evergreen
* **Core Processing Engine:** Multi-Threaded Python 3.13 Local Runtime
* **Imaging Libraries:** Pillow (PIL Fork) with LibJPEG-Turbo, LibPNG, LibWebP
* **Supported Input Formats:** PNG, JPEG, JPG, WebP, GIF, BMP, TIFF, ICO
* **Supported Output Formats:** Original (Format Matching), JPEG, PNG, WebP
* **Application Binary Footprint:** ~22.7 MB (Installer) / ~29.1 MB (Standalone)
* **Network Requirement:** Zero (100% Offline Air-Gapped Operation)

---

## Building From Source

Developers wishing to compile and package PixelPress locally can utilize the automated build pipeline:

### 1. Prerequisites

* Windows 10 or Windows 11 (64-bit)
* Python 3.11+ installed and added to system PATH
* Inno Setup 6 (optional, required only for compiling `PixelPress_Setup.exe`)

### 2. Environment Setup

```powershell
# Clone the official repository
git clone https://github.com/BeginnerAman/PixelPress.git
cd PixelPress

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install build dependencies
pip install -r requirements-desktop.txt
```

### 3. Compilation via Automated Builder

Run the automated interactive compiler script:

```cmd
build.bat
```

Select your desired compilation target from the menu:
* `[1]` Single-File Standalone Executable (`dist/PixelPress-Portable.exe`)
* `[2]` High-Performance Directory Bundle + Inno Setup Installer (`dist/PixelPress_Setup.exe`)
* `[3]` Full Dual-Pipeline Compilation (Both Targets)

---

## Security, Telemetry, and Privacy Policy

* **Zero Cloud Transmissions:** PixelPress contains zero telemetry SDKs, analytics trackers, or network sockets communicating with external hosts.
* **Ephemeral Memory Scrubbing:** Image binary buffers exist strictly in transient process memory and are cleared when a batch is reset or completed.
* **Metadata Stripping:** The optional EXIF metadata stripping module scrubs GPS coordinates, camera serial numbers, and creator timestamps from output files.

---

## Author and Copyright

* **Lead Architect and Developer:** Aman Vishwakarma
* **GitHub Profile:** [@BeginnerAman](https://github.com/BeginnerAman)
* **Copyright:** Copyright (c) 2026 Aman Vishwakarma. All rights reserved.
* **License:** Released under the terms of the MIT License.
