# PixelPress Desktop Pro - Internal Architecture Guide

> High-Performance, On-Device Image Compression Workstation for Windows 11 and 10.
> Built with Python, PyWebView (WebView2), Flask, and Pillow.

---

## Technical Highlights

* **Native Desktop Window:** Powered by `pywebview` utilizing the native Windows Edge WebView2 runtime. Zero browser popups or tabs.
* **Ultra-Lightweight Footprint:** Single portable `.exe` is only ~19.8 MB (compared to 150 MB+ for Electron apps).
* **100% Offline Resilience:** Bundled Lucide vector SVG icons and native system typography. Zero external CDN calls.
* **Pro Desktop Workspace:** Compact 2-column workstation with real-time settings dock, drag-and-drop batch queue, and instant metrics dashboard.
* **Interactive Quality Inspection:** Before / After Split Slider modal allowing 1:1 pixel comparison between original and compressed images.
* **Multi-Threaded Engine:** Parallel compression using Python's `ThreadPoolExecutor` for blazing-fast batch processing.
* **Advanced PNG Quantization:** Adaptive palette quantization delivering 65% to 82% size reduction on PNGs without perceptible quality loss.
* **Zero Junk Disk Policy:** Temporary session files are immediately purged on reset (`/clear-workspace`).

---

## Project Structure

```
PixelPress-Desktop/
|
+-- app.py                      # Multi-threaded Flask backend with Pillow engine
+-- launcher.py                 # Desktop entry point with PyWebView window wrapper
+-- PixelPress.spec             # PyInstaller spec for Directory Bundle (Inno Setup)
+-- PixelPress-Portable.spec    # PyInstaller spec for Single-File Standalone EXE
+-- build.bat                   # Automated compilation pipeline
+-- installer.iss               # Inno Setup 6 installer script
+-- requirements-desktop.txt    # Desktop build dependencies
+-- generate_icon.py            # Multi-size .ico generator
+-- icon.ico                    # Application icon
+-- README.md                   # Official Repository Documentation
|
+-- docs/                       # GitHub Pages Official Showcase Website
|   +-- index.html              # Semantic HTML structure
|   +-- css/style.css           # Modular Dark Studio stylesheet
|   +-- js/main.js              # Split slider & savings calculator
|
+-- templates/
|   +-- index.html              # Desktop UI with embedded Lucide SVG sprite
|
+-- static/
    +-- css/style.css           # Desktop window styling
    +-- js/main.js              # UI controller, split slider, & batch manager
```

---

## How to Build (Dual Pipeline)

Run the automated compilation script:
```bat
build.bat
```

Interactive selection menu:
```
[1] Portable Standalone EXE (Single-file dist/PixelPress-Portable.exe)
[2] Fast Directory Bundle + Inno Setup Installer (dist/PixelPress_Setup.exe)
[3] Build Both Targets
[4] Exit
```
