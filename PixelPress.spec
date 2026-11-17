# -*- mode: python ; coding: utf-8 -*-
"""
PixelPress.spec — PyInstaller Build Specification (ONEDIR / Installer Mode)
=============================================================================
Packages the PixelPress PyWebView desktop app into a high-performance directory bundle.
Ideal for the Inno Setup Installer (fast startup, instant execution, zero extraction delay).

Build: pyinstaller PixelPress.spec --noconfirm --clean
"""

import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# ─── Collect Hidden Imports ───────────────────────────────────────────────────

hidden_imports = [
    # Flask stack
    'flask',
    'flask.templating',
    'flask.json',
    'jinja2',
    'jinja2.ext',
    'werkzeug',
    'werkzeug.routing',
    'werkzeug.exceptions',
    'werkzeug.middleware.shared_data',
    'werkzeug.serving',
    'click',
    'itsdangerous',
    'markupsafe',

    # Pillow plugins
    'PIL',
    'PIL.Image',
    'PIL.ImageOps',
    'PIL.ImageFile',
    'PIL.JpegImagePlugin',
    'PIL.PngImagePlugin',
    'PIL.WebPImagePlugin',
    'PIL.GifImagePlugin',
    'PIL.BmpImagePlugin',
    'PIL.TiffImagePlugin',
    'PIL.IcoImagePlugin',
    'PIL.ExifTags',
    'PIL._imaging',
    'PIL._webp',
    'PIL.features',

    # Standard lib
    'uuid',
    'io',
    'zipfile',
    'threading',
    'concurrent.futures',
    'logging',
    'urllib.request',
    'urllib.error',
    'socket',
    'ctypes',

    # PyWebView & Windows GUI bindings
    'webview',
    'webview.platforms.winforms',
    'webview.platforms.edgechromium',
    'clr_loader',
    'pythonnet',
    'proxy_tools',
]

hidden_imports += collect_submodules('flask')
hidden_imports += collect_submodules('werkzeug')
hidden_imports += collect_submodules('jinja2')
hidden_imports += collect_submodules('webview')

# ─── Data Files to Bundle ─────────────────────────────────────────────────────

datas = [
    ('templates', 'templates'),
    ('static',    'static'),
]

# Collect all pywebview assets (Edge WebView2 DLLs, JS bridge)
datas += collect_data_files('webview')

if os.path.exists('icon.ico'):
    datas.append(('icon.ico', '.'))

# ─── Analysis ─────────────────────────────────────────────────────────────────

a = Analysis(
    ['launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'pytest',
        'IPython',
        'notebook',
        'docutils',
        'sphinx',
        'unittest',
        'test',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

icon_file = 'icon.ico' if os.path.exists('icon.ico') else None

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PixelPress',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PixelPress',
)
