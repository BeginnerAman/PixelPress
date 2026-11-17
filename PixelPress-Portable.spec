# -*- mode: python ; coding: utf-8 -*-
"""
PixelPress-Portable.spec — PyInstaller Build Specification (ONEFILE Portable Mode)
==================================================================================
Packages PixelPress into a SINGLE portable .exe file (PixelPress-Portable.exe).
Zero installation required: copy to USB drive or Desktop and double click to run!

Build: pyinstaller PixelPress-Portable.spec --noconfirm --clean
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
    'PIL.ImageCms',
    'PIL.JpegImagePlugin',
    'PIL.PngImagePlugin',
    'PIL.WebPImagePlugin',
    'PIL.GifImagePlugin',
    'PIL.BmpImagePlugin',
    'PIL.TiffImagePlugin',
    'PIL.IcoImagePlugin',
    'PIL.ExifTags',
    'PIL._imaging',
    'PIL._imagingcms',
    'PIL._webp',
    'PIL.features',

    # Standard lib
    'uuid',
    'secrets',
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

# Collect all pywebview assets
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PixelPress-Portable',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)
