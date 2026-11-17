"""
PixelPress Desktop Launcher
============================
- Dynamic screen resolution detection & centering.
- Starts Flask backend in a daemon thread.
- Polls /health until server is active.
- Creates and runs a modern frameless native desktop application window via PyWebView (Edge WebView2).
- Native Win32 window controls (hardware-accelerated drag, minimize, maximize, close).
- Mathematical screen centering via direct Win32 SetWindowPos.
- Zero js_api reflection to prevent COM recursion deadlocks and startup hangs.
- Handles clean shutdown on window close.
"""

import os
import sys
import time
import threading
import secrets
import urllib.request
import urllib.error
import logging
import socket
import ctypes

user32 = ctypes.windll.user32


# ─── Path & Icon Helpers ──────────────────────────────────────────────────────

def get_base_dir():
    if hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_dir():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_storage_root():
    r"""
    Smart Dual-Mode Storage Resolution:
    1. If a 'portable.dat' or '.portable' or 'portable.ini' marker exists next to the .exe:
       Activate True USB Mode -> Use '<base_dir>/PixelPress_Data'
    2. Otherwise (Desktop / Downloads / Program Files):
       Use '%LOCALAPPDATA%/PixelPress' (e.g. C:/Users/<User>/AppData/Local/PixelPress)
       Fallback to tempfile.gettempdir()/PixelPress if LOCALAPPDATA is unset.
    Guarantees:
    - Zero extra folders on Desktop / Downloads (pure single-app studio look).
    - Zero permission crashes when installed in C:\Program Files\.
    - Lightning-fast NVMe/SSD caching even when running from a slow USB 2.0 pendrive!
    """
    base_dir = get_base_dir()
    portable_markers = [
        os.path.join(base_dir, 'portable.dat'),
        os.path.join(base_dir, '.portable'),
        os.path.join(base_dir, 'portable.ini'),
    ]
    for marker in portable_markers:
        if os.path.exists(marker):
            target = os.path.join(base_dir, 'PixelPress_Data')
            os.makedirs(target, exist_ok=True)
            return target

    local_appdata = os.environ.get('LOCALAPPDATA')
    if local_appdata:
        target = os.path.join(local_appdata, 'PixelPress')
    else:
        import tempfile
        target = os.path.join(tempfile.gettempdir(), 'PixelPress')
    os.makedirs(target, exist_ok=True)
    return target


def get_log_path():
    log_dir = os.path.join(get_storage_root(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, 'pixelpress.log')


def get_icon_path():
    candidates = [
        os.path.join(get_resource_dir(), 'icon.ico'),
        os.path.join(get_base_dir(), 'icon.ico'),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


# ─── Configure Logging ────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(get_log_path(), encoding='utf-8'),
    ]
)
log = logging.getLogger('PixelPress')


# ─── Screen Geometry Calculation ──────────────────────────────────────────────

def get_optimal_window_dimensions():
    """
    Calculate optimal window size based on user's active screen.
    Opens at 95% width and 92% height (Edge-to-Edge Studio Workspace).
    """
    try:
        import webview
        screens = webview.screens
        if screens and len(screens) > 0:
            s = screens[0]
            sw = s.width
            sh = s.height
            log.info(f"Detected primary display: {sw}x{sh} (logical DIPs)")
            target_w = max(960, int(sw * 0.95))
            target_h = max(600, int((sh - 40) * 0.92))
            return target_w, target_h
    except Exception as e:
        log.warning(f"Could not detect screen via webview.screens: {e}")

    try:
        sw = user32.GetSystemMetrics(0)
        sh = user32.GetSystemMetrics(1)
        if sw > 0 and sh > 0:
            target_w = max(960, int(sw * 0.95))
            target_h = max(600, int((sh - 40) * 0.92))
            return target_w, target_h
    except Exception:
        pass

    return 1600, 920


# ─── Constants ────────────────────────────────────────────────────────────────

HOST    = '127.0.0.1'
PORT    = 5000
TIMEOUT = 30   # seconds to wait for server startup
POLL    = 0.2  # poll interval in seconds


# ─── Free Port Finder ─────────────────────────────────────────────────────────

def find_free_port(default_port=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, default_port))
            return default_port
        except OSError:
            s.bind((HOST, 0))
            return s.getsockname()[1]


# ─── Flask Server Thread ──────────────────────────────────────────────────────

def run_flask(port, auth_token=None):
    try:
        from app import app
        if auth_token:
            app.config['PIXELPRESS_AUTH_TOKEN'] = auth_token
        import logging as py_logging
        werkzeug_log = py_logging.getLogger('werkzeug')
        werkzeug_log.setLevel(py_logging.ERROR)

        log.info(f"Starting Flask server on {HOST}:{port}")
        app.run(
            host=HOST,
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True,
        )
    except Exception as e:
        log.error(f"Flask server error: {e}", exc_info=True)


# ─── Health Check ─────────────────────────────────────────────────────────────

def wait_for_server(port, timeout=TIMEOUT):
    url = f'http://{HOST}:{port}/health'
    deadline = time.time() + timeout
    log.info(f"Waiting for backend server at {url} ...")

    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.5) as resp:
                if resp.status == 200:
                    log.info("Backend server is ready.")
                    return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(POLL)

    log.error(f"Server did not start within {timeout}s.")
    return False


# ─── Main Desktop Entry Point ─────────────────────────────────────────────────

def main():
    log.info("=" * 60)
    log.info("PixelPress Desktop Application Starting (Centered Responsive Mode)")
    log.info("=" * 60)

    port = find_free_port(PORT)
    auth_token = secrets.token_urlsafe(32)
    url = f'http://{HOST}:{port}'

    # Start Flask in daemon thread
    flask_thread = threading.Thread(target=run_flask, args=(port, auth_token), daemon=True)
    flask_thread.start()

    # Wait for server to be ready
    ready = wait_for_server(port)

    if not ready:
        try:
            user32.MessageBoxW(
                0,
                "PixelPress failed to start internal server.\nPlease check logs/pixelpress.log for details.",
                "PixelPress - Error",
                0x10  # MB_ICONERROR
            )
        except Exception:
            pass
        sys.exit(1)

    # Launch PyWebView Frameless Native Window
    try:
        import webview
        icon_path = get_icon_path()
        target_w, target_h = get_optimal_window_dimensions()
        log.info(f"Window initial dimensions: {target_w}x{target_h}")

        window = webview.create_window(
            title='PixelPress - Professional Image Compressor',
            url=url,
            width=target_w,
            height=target_h,
            min_size=(820, 500),
            resizable=True,
            frameless=True,      # Eliminates OS title bar
            easy_drag=False,     # Managed cleanly via Win32 routes
            text_select=False,
            zoomable=False,
            background_color='#0b0c10',
            # NOTE: DO NOT pass js_api here. Passing js_api causes PyWebView's
            # inject_pywebview to inspect COM/CLR objects recursively, which locks
            # up the UI message pump and triggers "Not responding".
        )

        def on_window_ready(win):
            try:
                # Wait until window is rendered on screen
                win.events.shown.wait(10)
                if getattr(win, 'native', None) is not None:
                    hwnd = win.native.Handle.ToInt32()
                    log.info(f"Native Form HWND captured: {hwnd}")

                    from app import set_window_hwnd
                    set_window_hwnd(hwnd)

                    # Explicitly set small (16x16) and big (32x32) application icons on the window handle
                    # so that all native child dialogs (IFileOpenDialog, SaveFileDialog) inherit the PixelPress logo
                    icon_path = get_icon_path()
                    if icon_path and os.path.exists(icon_path):
                        try:
                            IMAGE_ICON = 1
                            LR_LOADFROMFILE = 0x00000010
                            WM_SETICON = 0x0080
                            ICON_SMALL = 0
                            ICON_BIG = 1
                            h_icon_sm = user32.LoadImageW(0, icon_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
                            h_icon_big = user32.LoadImageW(0, icon_path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
                            if h_icon_sm:
                                user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h_icon_sm)
                            if h_icon_big:
                                user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, h_icon_big)
                            log.info("Native window WM_SETICON applied successfully for dialog icon inheritance.")
                        except Exception as icon_err:
                            log.warning(f"Could not apply WM_SETICON: {icon_err}")

                    # Mathematical center calculation on active monitor (95% width, 92% height)
                    sw = user32.GetSystemMetrics(0)
                    sh = user32.GetSystemMetrics(1)
                    opt_w = max(960, int(sw * 0.95))
                    opt_h = max(600, int((sh - 40) * 0.92))
                    center_x = max(0, (sw - opt_w) // 2)
                    center_y = max(0, (sh - 40 - opt_h) // 2)

                    user32.SetWindowPos(
                        hwnd, 0,
                        center_x, center_y,
                        opt_w, opt_h,
                        0x0004 | 0x0010 | 0x0040  # SWP_NOZORDER | SWP_NOACTIVATE | SWP_SHOWWINDOW
                    )
                    log.info(f"Window positioned at ({center_x}, {center_y}) with size {opt_w}x{opt_h} on {sw}x{sh} display (95%x92%).")
            except Exception as ex:
                log.error(f"Error during on_window_ready: {ex}", exc_info=True)

        log.info("Starting PyWebView event loop...")
        webview.start(on_window_ready, window, icon=icon_path, debug=False)

    except Exception as e:
        log.error(f"PyWebView runtime error: {e}", exc_info=True)
        import webbrowser
        log.warning("Falling back to default browser.")
        webbrowser.open(url)
        try:
            while True:
                time.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            pass
    finally:
        log.info("PixelPress session finished. Terminating all processes.")
        os._exit(0)


if __name__ == '__main__':
    main()
