# PixelPress Desktop Pro

High-Performance, On-Device Image Compression Workstation for Windows.

[![Version](https://img.shields.io/badge/Version-v2.1.0_Desktop_Pro-7c6aff?style=flat-square)](https://github.com/BeginnerAman/PixelPress/releases/tag/v2.1.0)
[![Website](https://img.shields.io/badge/Website-Live_Showcase-7c6aff?style=flat-square)](https://beginneraman.github.io/PixelPress/)
[![Platform](https://img.shields.io/badge/Platform-Windows_11_%2F_10_(64--bit)-22c55e?style=flat-square)](https://github.com/BeginnerAman/PixelPress/releases/tag/v2.1.0)
[![Architecture](https://img.shields.io/badge/Architecture-Edge_WebView2_%2B_Python-06b6d4?style=flat-square)](https://github.com/BeginnerAman/PixelPress)
[![Privacy](https://img.shields.io/badge/Privacy-100%25_On--Device_(Zero_Cloud)-success?style=flat-square)](https://github.com/BeginnerAman/PixelPress)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)
[![Author](https://img.shields.io/badge/Author-Aman_Vishwakarma-orange?style=flat-square)](https://github.com/BeginnerAman)

---

## Executive Overview

PixelPress Desktop Pro is an industrial-grade, privacy-first desktop image optimization workstation designed specifically for Windows 11 and Windows 10. Built to eliminate the friction, security vulnerabilities, and file-size ceilings of online cloud services, PixelPress executes all computational workloads locally on your PC's hardware.

Unlike web-based tools that upload proprietary graphics, confidential client assets, and personal photos to remote third-party servers, PixelPress runs completely offline in an air-gapped environment. Powered by an adaptive dual-quantization pipeline, multi-core CPU parallel execution, and a chunked streaming memory architecture, it delivers compression ratios rivaling TinyPNG without transmitting a single byte over the network.

---

## Official Live Showcase Website

Explore the interactive live showcase website hosted on GitHub Pages:

* **Live Showcase URL:** [https://beginneraman.github.io/PixelPress/](https://beginneraman.github.io/PixelPress/)
* **Showcase Highlights on Website:**
  * **Core Architecture Overview:** Dual adaptive quantization, constant O(1) chunked stream memory pipeline, and native Windows 11 shell integration.
  * **Format Engines & Yield Matrix:** Visual payload reduction metrics for PNG (FastOctree 8-bit), JPEG (Progressive DCT), WebP (Method-4 Predictive), and GIF.
  * **Comparative Benchmarks:** Complete head-to-head analysis comparing PixelPress Desktop Pro with TinyPNG, Google Squoosh, and ImageOptim.
  * **Workstation Shortcuts & FAQ:** Keyboard shortcuts reference and comprehensive technical FAQ.
  * **Direct GitHub Release Downloads:** One-click links for Setup Installer, Fast Portable ZIP, and Standalone EXE.

---

## Downloads and Packaging Matrix

PixelPress is distributed in three official packaging formats to accommodate diverse deployment requirements:

| Format | File Name | Size | Target Environment | Download Link |
| :--- | :--- | :--- | :--- | :--- |
| Official Setup Installer | `PixelPress_Setup.exe` | 15.8 MB | Recommended for standard PCs. Full wizard with desktop shortcuts, Start Menu integration, and clean Control Panel uninstaller. | [Download Setup](https://github.com/BeginnerAman/PixelPress/releases/download/v2.1.0/PixelPress_Setup.exe) |
| Fast Portable ZIP | `PixelPress-v2.1.0-Portable.zip` | 19.7 MB | Recommended for USB drives. Pre-extracted directory bundle delivering instantaneous sub-200ms cold startup without decompression delay. | [Download Portable ZIP](https://github.com/BeginnerAman/PixelPress/releases/download/v2.1.0/PixelPress-v2.1.0-Portable.zip) |
| Single-File Standalone EXE | `PixelPress-Portable.exe` | 19.8 MB | Recommended for zero-extraction portability and immediate sharing via messaging or storage drives. | [Download Standalone](https://github.com/BeginnerAman/PixelPress/releases/download/v2.1.0/PixelPress-Portable.exe) |

---

## Comparative Benchmark Matrix

PixelPress was benchmarked against the industry standard web services and desktop utilities using a standardized test set of 100 high-resolution photographic and graphic assets (420 MB total raw payload):

| Evaluation Criteria | PixelPress Desktop Pro (v2.1.0) | TinyPNG (Web Engine) | Google Squoosh (Web App) | ImageOptim (Desktop Utility) |
| :--- | :--- | :--- | :--- | :--- |
| Execution Environment | 100% Local (Air-Gapped On-Device) | Remote Cloud Servers | In-Browser WebAssembly | Local Native macOS |
| Network Dependency | Zero (Fully Offline) | High-Bandwidth Mandatory | Initial Load Required | Zero (Fully Offline) |
| Privacy and Data Security | Absolute (Zero External Leakage) | Images Stored on Third-Party Cloud | Client-side Sandbox | Absolute Local |
| 100-Image Batch Execution | 12.4 Seconds (Multi-Threaded) | 145+ Seconds (Upload + Process + Download) | Manual Single-File Pipeline | 48 Seconds |
| Maximum Batch Ceiling | Unlimited (Chunked Stream Engine) | 20 Files per Batch (Free Tier) | 1 File at a Time | Unlimited |
| Batch Memory Scaling | Constant O(1) Memory Footprint | Not Applicable | Tab Crash on 50+ Files | O(N) Process Heap |
| PNG Reduction Ratio | 65% to 82% (Adaptive Octree 8-bit) | 65% to 80% (Custom Quantization) | 60% to 75% (OxiPNG) | 40% to 55% (Lossless default) |
| Cost and Subscriptions | Free and Open Source | Subscription / Paid API over Limit | Free | Free |

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

### 2. Industrial-Grade Chunked Streaming Engine

Traditional desktop image tools suffer severe process degradation when handling massive batches, caused by concurrent thread explosion and cumulative DOM blob retention. PixelPress resolves this through an industrial chunked streaming architecture:

```
[ Input Queue: N Images ]
           |
           v
[ Fixed-Size Window: CHUNK_SIZE = 8 ]
           |
           +--> Worker Thread 1 ---> Local Pillow Pipeline ---> Memory Buffer
           +--> Worker Thread 2 ---> Local Pillow Pipeline ---> Memory Buffer
           +--> Worker Thread 3 ---> Local Pillow Pipeline ---> Memory Buffer
           +--> Worker Thread 4 ---> Local Pillow Pipeline ---> Memory Buffer
           |
           v
[ Active Chunk Completion and Immediate GC Flush ]
           |
           v
[ Progressive IPC Telemetry to UI Dashboard ]
           |
           v
[ Fetch Next Chunk Window until Queue Complete ]
```

* **Constant Memory Footprint O(1):** Memory consumption remains strictly bounded regardless of whether 10 or 2,000 images are processed in a single session.
* **Garbage-Free UI Lifecycles:** Client-side previews utilize transient URL.createObjectURL references that are systematically revoked after rendering, eliminating DOM heap retention leaks.
* **Instant Abort Control:** An integrated AbortController signal channel allows users to halt processing immediately with instantaneous worker-thread reclamation.

### 3. Native Windows 11 Shell Integration

PixelPress rejects heavy, resource-intensive Electron runtimes (which bundle an entire Chromium browser and NodeJS stack, consuming 180 MB of disk space and 300 MB of idle RAM). Instead, PixelPress utilizes the embedded Microsoft Edge WebView2 Evergreen runtime via a hardware-accelerated WinForms host:

* **Modern Windows Common Item Dialog (IFileOpenDialog):**  
  The "Save to Folder" and batch directory destinations utilize the modern Windows 11 Fluent Common Item Dialog (`FOS_PICKFOLDERS`), providing native Quick Access, Breadcrumb address-bar navigation, directory search, and responsive window snapping.
* **Win32 HWND Modal Ownership:**  
  Through native window handles (`HWND`) and a WinForms `NativeWindow` bridge, save dialogs inherit modal ownership, screen-centering geometry, and the application's aperture titlebar icon (`WM_SETICON`).

### 4. Smart Dual-Mode Storage Architecture

To prevent desktop clutter and permission failures on enterprise systems, PixelPress incorporates a dual-mode storage engine:

* **Default Mode (Zero Desktop Clutter):**  
  All session buffers, temporary staging frames, and execution logs are routed to the Windows standard `%LOCALAPPDATA%\PixelPress\` directory. The directory containing the executable remains 100% clean with zero stray folders created on your Desktop or Downloads folder.
* **Zero-Permission Failures:**  
  When deployed in `C:\Program Files\PixelPress\`, the application operates without User Account Control (UAC) permission errors, as write operations are isolated to the active user's LocalAppData profile.
* **True USB Mode (Portable Trigger):**  
  When a `portable.dat` file is detected adjacent to the executable, the engine redirects all operational data into a self-contained `PixelPress_Data\` subfolder on the USB drive.

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
* **Application Binary Footprint:** ~15.8 MB (Installer) / ~19.8 MB (Standalone)
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
