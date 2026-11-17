"""
PixelPress - Professional Image Compressor
Desktop-optimized Flask backend with multi-threaded compression & PyWebView compatibility.
"""

import os
import sys
import io
import uuid
import zipfile
import time
import shutil
import subprocess
import threading
import secrets
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps, ImageFile, ImageSequence, ImageCms

# Prevent truncated/partially corrupted image crashes
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = 250_000_000  # Support pro photography & panoramic images up to 250 Megapixels

# ─── PyInstaller / Development Path Resolution ────────────────────────────────

def resource_path(relative_path):
    """
    Get absolute path to bundled resource.
    Works in development AND in PyInstaller packaged mode.
    """
    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


def get_base_dir():
    if hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
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
    - ZERO extra folders on Desktop / Downloads (pure single-app studio look).
    - ZERO permission crashes when installed in C:\Program Files\.
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


def user_data_path(relative_path):
    """
    Get path for writable user data (uploads, compressed, logs, temp).
    Uses get_storage_root() to ensure zero clutter on Desktop and zero permission errors.
    """
    full = os.path.join(get_storage_root(), relative_path)
    os.makedirs(full, exist_ok=True)
    return full


# ─── Native Win32 Window Handle & Dialog Owner ────────────────────────────────

import ctypes
user32 = ctypes.windll.user32

_window_hwnd = None

def set_window_hwnd(hwnd):
    global _window_hwnd
    _window_hwnd = int(hwnd)


def get_dialog_owner():
    """
    Returns an IWin32Window wrapper (NativeWindow) around the main app window HWND,
    or None if the main window HWND is not set.
    Allows Save and Folder dialogs to inherit the application icon in the title bar
    and stay properly centered/modal to the main window.
    """
    global _window_hwnd
    if not _window_hwnd:
        return None
    try:
        import clr
        clr.AddReference('System.Windows.Forms')
        from System import IntPtr
        from System.Windows.Forms import NativeWindow
        nw = NativeWindow()
        nw.AssignHandle(IntPtr(_window_hwnd))
        return nw
    except Exception:
        return None


# ─── Flask App Init ───────────────────────────────────────────────────────────

app = Flask(
    __name__,
    template_folder=resource_path('templates'),
    static_folder=resource_path('static'),
)

# ─── Folder Setup ────────────────────────────────────────────────────────────

UPLOAD_FOLDER     = user_data_path('uploads')
COMPRESSED_FOLDER = user_data_path('compressed')
TEMP_FOLDER       = user_data_path('temp')
LOG_FOLDER        = user_data_path('logs')

MAX_FILE_SIZE     = 500 * 1024 * 1024  # 500 MB max request size (supports massive chunked batches)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'tiff', 'ico'}

app.config['UPLOAD_FOLDER']      = UPLOAD_FOLDER
app.config['COMPRESSED_FOLDER']  = COMPRESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


# ─── Helpers ──────────────────────────────────────────────────────────────────

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_size(path):
    return os.path.getsize(path)


def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def compress_image(input_path, output_path, settings):
    """
    Core high-performance compression engine.
    Supports: quality, resize, format conversion, metadata strip, deep optimize,
    PNG quantization, ICC profile preservation, CMYK correction, and multi-frame animation.
    """
    img = Image.open(input_path)
    original_format = (img.format or 'JPEG').upper()
    is_animated = getattr(img, 'is_animated', False) and getattr(img, 'n_frames', 1) > 1
    duration = img.info.get('duration', 100)
    loop = img.info.get('loop', 0)
    icc_profile = img.info.get('icc_profile')
    exif_data = img.info.get('exif')

    # Auto-orient based on EXIF for non-animated images
    if not is_animated:
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

    strip_metadata = settings.get('strip_metadata', False)

    # ── Output Format Resolution ──
    out_format = settings.get('output_format', 'same').lower()
    ext_map = {
        'jpeg': 'jpg', 'jpg': 'jpg', 'png': 'png',
        'webp': 'webp', 'gif': 'gif', 'bmp': 'bmp', 'tiff': 'tiff'
    }
    if out_format == 'same':
        out_format = original_format.lower()

    out_format_norm = 'jpeg' if out_format in ('jpg', 'jpeg') else out_format
    out_ext = ext_map.get(out_format_norm, 'jpg')
    output_path = os.path.splitext(output_path)[0] + '.' + out_ext

    # ── Quality & Optimization Parameters ──
    quality  = int(settings.get('quality', 85))
    optimize = settings.get('optimize', True)
    lossless = settings.get('lossless', False)

    # ── Resizing Helper ──
    def _apply_resize(target_img):
        resize_mode = settings.get('resize_mode', 'none')
        w, h = target_img.width, target_img.height
        if resize_mode == 'percentage':
            pct = int(settings.get('resize_value', 100)) / 100.0
            new_w = max(1, int(w * pct))
            new_h = max(1, int(h * pct))
            return target_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        elif resize_mode == 'width':
            target_w = int(settings.get('resize_value', w))
            ratio = target_w / float(w)
            new_h = max(1, int(h * ratio))
            return target_img.resize((target_w, new_h), Image.Resampling.LANCZOS)
        elif resize_mode == 'height':
            target_h = int(settings.get('resize_value', h))
            ratio = target_h / float(h)
            new_w = max(1, int(img.width * ratio))
            return target_img.resize((new_w, target_h), Image.Resampling.LANCZOS)
        elif resize_mode == 'custom':
            target_w = int(settings.get('resize_width', w))
            target_h = int(settings.get('resize_height', h))
            return target_img.resize((max(1, target_w), max(1, target_h)), Image.Resampling.LANCZOS)
        return target_img

    # ── Color Mode Conversion Helper ──
    def _convert_color_mode(target_img, target_format):
        # CMYK to RGB Perceptual Color Profile Conversion
        if target_img.mode == 'CMYK':
            if icc_profile:
                try:
                    in_p = ImageCms.getOpenProfile(io.BytesIO(icc_profile))
                    out_p = ImageCms.createProfile('sRGB')
                    target_img = ImageCms.profileToProfile(target_img, in_p, out_p, outputMode='RGB')
                except Exception:
                    target_img = target_img.convert('RGB')
            else:
                target_img = target_img.convert('RGB')

        if target_format == 'jpeg':
            if target_img.mode in ('RGBA', 'P', 'LA'):
                bg = Image.new('RGB', target_img.size, (255, 255, 255))
                if target_img.mode == 'P':
                    target_img = target_img.convert('RGBA')
                if target_img.mode in ('RGBA', 'LA'):
                    bg.paste(target_img, mask=target_img.split()[-1])
                return bg
            elif target_img.mode != 'RGB':
                return target_img.convert('RGB')
        return target_img

    # ── Multi-Frame Animated GIF & WebP Preservation ──
    if is_animated and out_format_norm in ('gif', 'webp'):
        frames = []
        for frame in ImageSequence.Iterator(img):
            f = frame.copy()
            f = _apply_resize(f)
            f = _convert_color_mode(f, out_format_norm)
            frames.append(f)

        out_w, out_h = frames[0].width, frames[0].height
        save_kwargs = {
            'save_all': True,
            'append_images': frames[1:],
            'duration': duration,
            'loop': loop,
            'optimize': optimize,
        }
        if out_format_norm == 'webp':
            save_kwargs['quality'] = quality
            save_kwargs['lossless'] = lossless
            save_kwargs['method'] = 4
        elif out_format_norm == 'gif':
            pass

        frames[0].save(output_path, format=out_format_norm.upper(), **save_kwargs)
        for f in frames:
            try:
                f.close()
            except Exception:
                pass
        try:
            img.close()
        except Exception:
            pass
        return output_path, out_w, out_h

    # ── Single-Frame Image Processing Pipeline ──
    img = _apply_resize(img)
    img = _convert_color_mode(img, out_format_norm)

    save_kwargs = {}

    # Preserve ICC Color Profiles (Display-P3, Adobe RGB, ProPhoto)
    if not strip_metadata and icc_profile:
        try:
            save_kwargs['icc_profile'] = icc_profile
        except Exception:
            pass

    if out_format_norm == 'jpeg':
        subsampling = 0 if quality >= 90 else 2
        save_kwargs.update({
            'quality':     quality,
            'optimize':    True,
            'progressive': True,
            'subsampling': subsampling,
        })
        if not strip_metadata and exif_data:
            try:
                save_kwargs['exif'] = exif_data
            except Exception:
                pass

    elif out_format_norm == 'png':
        if not lossless and quality < 95:
            colors = max(32, min(256, int(quality * 2.56)))
            try:
                if img.mode == 'RGBA':
                    img = img.quantize(colors=colors, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG)
                elif img.mode in ('RGB', 'L'):
                    img = img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
            except Exception:
                pass

        compress_level = max(0, min(9, int((100 - quality) / 10) + 1))
        save_kwargs.update({
            'optimize':       True,
            'compress_level': compress_level,
        })

    elif out_format_norm == 'webp':
        save_kwargs.update({
            'quality':  quality,
            'lossless': lossless,
            'method':   4,
        })

    elif out_format_norm == 'gif':
        save_kwargs['optimize'] = optimize

    out_w, out_h = img.width, img.height
    img.save(
        output_path,
        format=out_format_norm.upper().replace('JPG', 'JPEG'),
        **save_kwargs
    )

    try:
        img.close()
    except Exception:
        pass

    return output_path, out_w, out_h


def get_image_info(path):
    try:
        with Image.open(path) as img:
            return {'width': img.width, 'height': img.height, 'mode': img.mode, 'format': img.format}
    except Exception:
        return {}


# ─── Native Win32 Window Management ──────────────────────────────────────────

def get_window_hwnd():
    try:
        import ctypes
        user32 = ctypes.windll.user32
        hwnd = user32.FindWindowW(None, 'PixelPress - Professional Image Compressor')
        if not hwnd:
            hwnd = user32.GetForegroundWindow()
        return hwnd
    except Exception:
        return None


def native_drag():
    try:
        import ctypes
        user32 = ctypes.windll.user32
        hwnd = get_window_hwnd()
        if hwnd:
            user32.ReleaseCapture()
            user32.PostMessageW(hwnd, 0x00A1, 2, 0)  # WM_NCLBUTTONDOWN, HTCAPTION
    except Exception:
        pass


def native_minimize():
    try:
        import ctypes
        user32 = ctypes.windll.user32
        hwnd = get_window_hwnd()
        if hwnd:
            user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE
    except Exception:
        pass


def native_toggle_maximize():
    try:
        import ctypes
        user32 = ctypes.windll.user32
        hwnd = get_window_hwnd()
        if hwnd:
            if user32.IsZoomed(hwnd):
                user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                return False
            else:
                user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE
                return True
    except Exception:
        pass
    return False


def native_close():
    try:
        import ctypes
        user32 = ctypes.windll.user32
        hwnd = get_window_hwnd()
        if hwnd:
            user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
        else:
            os._exit(0)
    except Exception:
        os._exit(0)


# ─── Session Security & Authentication ────────────────────────────────────────

def get_auth_token():
    """Retrieve or generate cryptographically secure local session token."""
    token = app.config.get('PIXELPRESS_AUTH_TOKEN')
    if not token:
        token = secrets.token_urlsafe(32)
        app.config['PIXELPRESS_AUTH_TOKEN'] = token
    return token


@app.before_request
def verify_auth_token():
    """
    Zero-Trust Localhost Gatekeeper:
    Rejects any unauthenticated external browser tab / script attempting CSRF or DNS rebinding.
    Whitelists only root page, health probe, and static bundle assets.
    """
    if request.path == '/' or request.path == '/health' or request.path.startswith('/static/'):
        return None

    expected_token = get_auth_token()
    provided_token = request.headers.get('X-PixelPress-Token') or request.args.get('token')

    if not provided_token or provided_token != expected_token:
        return jsonify({'error': 'Unauthorized: Missing or invalid authentication token'}), 403


# ─── Routes ───────────────────────────────────────────────────────────────────

_desktop_api = None

def set_desktop_api(api):
    global _desktop_api
    _desktop_api = api


@app.route('/')
def index():
    return render_template('index.html', auth_token=get_auth_token())


# ─── Batch Cancellation Registry ──────────────────────────────────────────────
_active_batches = {}
_active_batches_lock = threading.Lock()


@app.route('/api/cancel-batch/<batch_id>', methods=['POST'])
def api_cancel_batch(batch_id):
    safe_id = secure_filename(batch_id)
    with _active_batches_lock:
        _active_batches[safe_id] = {'cancelled': True, 'timestamp': time.time()}
    return jsonify({'status': 'ok', 'cancelled': True, 'batch_id': safe_id})


@app.route('/compress', methods=['POST'])
def compress():
    if 'files' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400

    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No files selected'}), 400

    batch_id = request.form.get('batch_id')
    if batch_id:
        safe_batch_id = secure_filename(batch_id)
        with _active_batches_lock:
            if safe_batch_id not in _active_batches:
                _active_batches[safe_batch_id] = {'cancelled': False, 'timestamp': time.time()}
    else:
        safe_batch_id = None

    settings = {
        'quality':        request.form.get('quality', 85),
        'optimize':       request.form.get('optimize', 'true') == 'true',
        'lossless':       request.form.get('lossless', 'false') == 'true',
        'strip_metadata': request.form.get('strip_metadata', 'false') == 'true',
        'output_format':  request.form.get('output_format', 'same'),
        'resize_mode':    request.form.get('resize_mode', 'none'),
        'resize_value':   request.form.get('resize_value', 100),
        'resize_width':   request.form.get('resize_width', 0),
        'resize_height':  request.form.get('resize_height', 0),
    }

    # Stage files and prepare batch tasks
    tasks = []
    skipped = []

    for file in files:
        if file.filename == '':
            continue
        if not allowed_file(file.filename):
            skipped.append({'error': f'Unsupported type: {file.filename}', 'filename': file.filename})
            continue

        try:
            file_id        = str(uuid.uuid4())
            original_ext   = file.filename.rsplit('.', 1)[1].lower()
            original_name  = file.filename
            input_filename = f"{file_id}_original.{original_ext}"
            input_path     = os.path.join(UPLOAD_FOLDER, input_filename)
            file.save(input_path)

            output_filename = f"{file_id}_compressed.{original_ext}"
            output_path     = os.path.join(COMPRESSED_FOLDER, output_filename)

            tasks.append({
                'file_id':       file_id,
                'original_name': original_name,
                'input_path':    input_path,
                'output_path':   output_path,
            })
        except Exception as e:
            skipped.append({'error': str(e), 'filename': file.filename})

    # Execute batch compression concurrently with ThreadPoolExecutor
    def _run_single(task):
        in_path  = task['input_path']
        out_path = task['output_path']

        # Check if batch was cancelled prior to processing
        if safe_batch_id:
            with _active_batches_lock:
                if _active_batches.get(safe_batch_id, {}).get('cancelled'):
                    return {'cancelled': True, 'filename': task['original_name'], 'file_id': task['file_id']}

        try:
            start = time.time()
            final_path, out_w, out_h = compress_image(in_path, out_path, settings)
            elapsed = round(time.time() - start, 2)

            # Check again after compression before thumbnail I/O
            if safe_batch_id:
                with _active_batches_lock:
                    if _active_batches.get(safe_batch_id, {}).get('cancelled'):
                        return {'cancelled': True, 'filename': task['original_name'], 'file_id': task['file_id']}

            # Pre-generate lightweight 104x104 thumbnail (~3KB) for instantaneous 144Hz card scrolling
            try:
                t_name = f"thumb_{os.path.basename(final_path)}.jpg"
                t_path = os.path.join(TEMP_FOLDER, t_name)
                with Image.open(final_path) as cimg:
                    cimg.thumbnail((104, 104), Image.Resampling.BOX)
                    if cimg.mode in ('RGBA', 'LA', 'P'):
                        bg = Image.new('RGB', cimg.size, (18, 20, 29))
                        if cimg.mode == 'P':
                            cimg = cimg.convert('RGBA')
                        if cimg.mode in ('RGBA', 'LA'):
                            bg.paste(cimg, mask=cimg.split()[-1])
                        cimg = bg
                    elif cimg.mode != 'RGB':
                        cimg = cimg.convert('RGB')
                    cimg.save(t_path, format='JPEG', quality=82, optimize=True)
            except Exception:
                pass

            orig_size = get_file_size(in_path)
            comp_size = get_file_size(final_path)
            savings   = round((1 - comp_size / orig_size) * 100, 1) if orig_size > 0 else 0
            orig_info = get_image_info(in_path)

            return {
                'success':             True,
                'original_name':       task['original_name'],
                'file_id':             task['file_id'],
                'input_filename':      os.path.basename(in_path),
                'compressed_filename': os.path.basename(final_path),
                'original_size':       orig_size,
                'compressed_size':     comp_size,
                'original_size_fmt':   format_size(orig_size),
                'compressed_size_fmt': format_size(comp_size),
                'savings_percent':     savings,
                'original_width':      orig_info.get('width', 0),
                'original_height':     orig_info.get('height', 0),
                'output_width':        out_w,
                'output_height':       out_h,
                'time_taken':          elapsed,
            }
        except Image.DecompressionBombError as e:
            return {'error': f'Image exceeds 250 Megapixel limit (DecompressionBomb protection): {e}', 'filename': task['original_name']}
        except Exception as e:
            return {'error': str(e), 'filename': task['original_name']}

    # Dynamically scale worker threads up to 16 cores (minimum 2)
    worker_count = max(2, min(os.cpu_count() or 4, 16))
    results = list(skipped)

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        batch_results = list(executor.map(_run_single, tasks))
        results.extend(batch_results)

    return jsonify({'results': results})


@app.route('/download/<filename>')
def download_file(filename):
    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify({'error': 'Invalid filename'}), 400
    path = os.path.join(COMPRESSED_FOLDER, safe_name)
    if not os.path.exists(path):
        return jsonify({'error': 'File not found'}), 404
    clean = '_'.join(safe_name.split('_')[2:]) if safe_name.count('_') >= 2 else safe_name
    return send_from_directory(COMPRESSED_FOLDER, safe_name, as_attachment=True, download_name=f"compressed_{clean}")


@app.route('/download-zip', methods=['POST'])
def download_zip():
    data      = request.get_json()
    filenames = data.get('filenames', [])
    if not filenames:
        return jsonify({'error': 'No files specified'}), 400

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename in filenames:
            path = os.path.join(COMPRESSED_FOLDER, filename)
            if os.path.exists(path):
                clean = '_'.join(filename.split('_')[2:]) if filename.count('_') >= 2 else filename
                zf.write(path, f"compressed_{clean}")

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='pixelpress_optimized_images.zip'
    )




def prompt_save_file_dialog(default_filename, filter_str='All Files (*.*)|*.*', title="Save File"):
    """
    Spawns Windows native SaveFileDialog via STA thread with PixelPress owner window attached.
    Inherits PixelPress logo in title bar and centers over app window.
    Returns dict with 'status' ('ok', 'cancelled', 'error') and 'path'.
    """
    res = {'status': 'error', 'path': None}
    try:
        import clr
        clr.AddReference('System.Windows.Forms')
        clr.AddReference('System.Threading')
        from System.Windows.Forms import SaveFileDialog, DialogResult
        from System.Threading import Thread, ThreadStart, ApartmentState

        def _worker():
            owner = None
            try:
                sfd = SaveFileDialog()
                sfd.FileName = default_filename
                sfd.Filter = filter_str
                sfd.RestoreDirectory = True
                sfd.Title = title
                
                downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
                if os.path.exists(downloads_dir):
                    sfd.InitialDirectory = downloads_dir

                owner = get_dialog_owner()
                dr = sfd.ShowDialog(owner) if owner else sfd.ShowDialog()
                if dr == DialogResult.OK and sfd.FileName:
                    res['status'] = 'ok'
                    res['path'] = sfd.FileName
                else:
                    res['status'] = 'cancelled'
            except Exception as e:
                res['status'] = 'error'
                res['error'] = str(e)
            finally:
                if owner is not None:
                    try:
                        owner.ReleaseHandle()
                    except Exception:
                        pass

        t = Thread(ThreadStart(_worker))
        t.SetApartmentState(ApartmentState.STA)
        t.Start()
        t.Join()
    except Exception as e:
        res['status'] = 'error'
        res['error'] = str(e)

    # Fallback to direct Downloads folder if dialog couldn't be spawned
    if res['status'] == 'error':
        downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        os.makedirs(downloads_dir, exist_ok=True)
        res['path'] = os.path.join(downloads_dir, default_filename)
        res['status'] = 'ok'

    return res


@app.route('/api/save-file', methods=['POST'])
def api_save_file():
    data = request.get_json() or {}
    filename = data.get('filename')
    original_name = data.get('original_name', filename)
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400

    source_path = os.path.join(COMPRESSED_FOLDER, filename)
    if not os.path.exists(source_path):
        return jsonify({'error': 'File not found'}), 404

    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    clean_orig = os.path.splitext(original_name)[0] if original_name else 'image'
    default_filename = f"optimized_{clean_orig}.{ext}" if ext else f"optimized_{clean_orig}"

    filter_map = {
        'jpg': 'JPEG Image (*.jpg;*.jpeg)|*.jpg;*.jpeg|All Files (*.*)|*.*',
        'jpeg': 'JPEG Image (*.jpg;*.jpeg)|*.jpg;*.jpeg|All Files (*.*)|*.*',
        'png': 'PNG Image (*.png)|*.png|All Files (*.*)|*.*',
        'webp': 'WebP Image (*.webp)|*.webp|All Files (*.*)|*.*',
        'gif': 'GIF Image (*.gif)|*.gif|All Files (*.*)|*.*',
        'bmp': 'BMP Image (*.bmp)|*.bmp|All Files (*.*)|*.*',
        'tiff': 'TIFF Image (*.tiff)|*.tiff|All Files (*.*)|*.*',
    }
    filter_str = filter_map.get(ext, 'All Files (*.*)|*.*')

    res = prompt_save_file_dialog(default_filename, filter_str, title="Save Optimized Image")
    if res.get('status') == 'cancelled':
        return jsonify({'status': 'cancelled'})

    target_path = res.get('path')
    if not target_path:
        return jsonify({'error': 'No save path selected'}), 400

    try:
        shutil.copy2(source_path, target_path)
        return jsonify({
            'status': 'ok',
            'saved_path': target_path,
            'filename': os.path.basename(target_path)
        })
    except Exception as e:
        return jsonify({'error': f"Failed to save file: {e}"}), 500


@app.route('/api/save-zip', methods=['POST'])
def api_save_zip():
    data = request.get_json() or {}
    filenames = data.get('filenames', [])
    if not filenames:
        return jsonify({'error': 'No files specified'}), 400

    default_filename = 'pixelpress_optimized_images.zip'
    filter_str = 'ZIP Archive (*.zip)|*.zip|All Files (*.*)|*.*'

    res = prompt_save_file_dialog(default_filename, filter_str, title="Save ZIP Archive")
    if res.get('status') == 'cancelled':
        return jsonify({'status': 'cancelled'})

    target_path = res.get('path')
    if not target_path:
        return jsonify({'error': 'No destination selected'}), 400

    try:
        with zipfile.ZipFile(target_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for fname in filenames:
                path = os.path.join(COMPRESSED_FOLDER, fname)
                if os.path.exists(path):
                    clean = '_'.join(fname.split('_')[2:]) if fname.count('_') >= 2 else fname
                    zf.write(path, f"optimized_{clean}")

        return jsonify({
            'status': 'ok',
            'saved_path': target_path,
            'filename': os.path.basename(target_path)
        })
    except Exception as e:
        return jsonify({'error': f"Failed to create ZIP: {e}"}), 500


def prompt_folder_dialog(title="Select Destination Folder"):
    """
    Spawns Modern Windows 11/10 IFileDialog (FOS_PICKFOLDERS) File Explorer via STA thread.
    Inherits PixelPress logo in title bar and centers over app window.
    Features: Quick Access sidebar, Breadcrumb navigation, Search bar, and modern Fluent design.
    """
    res = {'status': 'error', 'path': None}
    try:
        from webview.platforms.winforms import OpenFolderDialog
        import clr
        clr.AddReference('System.Threading')
        from System.Threading import Thread, ThreadStart, ApartmentState

        def _worker():
            owner = None
            try:
                downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
                pictures_dir = os.path.join(os.path.expanduser('~'), 'Pictures')
                init_dir = pictures_dir if os.path.exists(pictures_dir) else downloads_dir

                owner = get_dialog_owner()

                # Invoke Modern Windows 11/10 IFileOpenDialog with FOS_PICKFOLDERS
                selected = OpenFolderDialog.show(
                    parent=owner,
                    initialDirectory=init_dir,
                    allow_multiple=False,
                    title=title
                )

                if selected and len(selected) > 0 and selected[0]:
                    res['status'] = 'ok'
                    res['path'] = selected[0]
                else:
                    res['status'] = 'cancelled'
            except Exception as e:
                res['status'] = 'error'
                res['error'] = str(e)
            finally:
                if owner is not None:
                    try:
                        owner.ReleaseHandle()
                    except Exception:
                        pass

        t = Thread(ThreadStart(_worker))
        t.SetApartmentState(ApartmentState.STA)
        t.Start()
        t.Join()
    except Exception as e:
        res['status'] = 'error'
        res['error'] = str(e)

    # Fallback to Downloads if error occurred
    if res['status'] == 'error':
        downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        if os.path.exists(downloads_dir):
            res['path'] = downloads_dir
            res['status'] = 'ok'

    return res


@app.route('/api/save-all-folder', methods=['POST'])
def api_save_all_folder():
    """
    Saves all compressed batch images directly to a selected directory.
    Zero unzip friction for desktop users!
    """
    data = request.get_json() or {}
    filenames = data.get('filenames', [])
    if not filenames:
        return jsonify({'error': 'No files specified'}), 400

    res = prompt_folder_dialog("Select Destination Folder to Save Optimized Images")
    if res.get('status') == 'cancelled':
        return jsonify({'status': 'cancelled'})

    target_dir = res.get('path')
    if not target_dir or not os.path.exists(target_dir):
        return jsonify({'error': 'No valid destination folder selected'}), 400

    saved_count = 0
    try:
        for fname in filenames:
            src = os.path.join(COMPRESSED_FOLDER, fname)
            if os.path.exists(src):
                clean = '_'.join(fname.split('_')[2:]) if fname.count('_') >= 2 else fname
                dst = os.path.join(target_dir, f"optimized_{clean}")
                shutil.copy2(src, dst)
                saved_count += 1

        return jsonify({
            'status': 'ok',
            'saved_count': saved_count,
            'folder': target_dir
        })
    except Exception as e:
        return jsonify({'error': f"Failed to save to folder: {e}"}), 500


@app.route('/api/reveal-file', methods=['POST'])
def api_reveal_file():
    data = request.get_json() or {}
    path = data.get('path')
    if not path:
        return jsonify({'error': 'No path provided'}), 400

    # Strict sandboxing: resolve canonical absolute path
    norm_path = os.path.realpath(os.path.abspath(path))
    allowed_roots = [
        os.path.realpath(os.path.abspath(COMPRESSED_FOLDER)),
        os.path.realpath(os.path.abspath(UPLOAD_FOLDER)),
        os.path.realpath(os.path.abspath(TEMP_FOLDER)),
    ]

    is_allowed = any(
        norm_path.startswith(d + os.sep) or norm_path == d
        for d in allowed_roots
    )

    if not is_allowed:
        return jsonify({'error': 'Access denied: Path is outside allowed workspace'}), 403

    if os.path.exists(norm_path):
        try:
            subprocess.run(['explorer.exe', '/select,', norm_path])
            return jsonify({'status': 'ok'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'File not found'}), 404


@app.route('/thumb/<filename>')
def thumb_file(filename):
    """
    Ultra-lightweight thumbnail endpoint (104x104px, ~3-4 KB).
    Eliminates GPU bottleneck of rendering 16MP raw photos into small 52px card thumbnails.
    """
    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify({'error': 'Invalid filename'}), 400

    t_name = f"thumb_{safe_name}.jpg"
    t_path = os.path.join(TEMP_FOLDER, t_name)
    if os.path.exists(t_path):
        return send_from_directory(TEMP_FOLDER, t_name, mimetype='image/jpeg')

    # Fallback: generate on demand
    src = os.path.join(COMPRESSED_FOLDER, safe_name)
    if not os.path.exists(src):
        src = os.path.join(UPLOAD_FOLDER, safe_name)

    if os.path.exists(src):
        try:
            with Image.open(src) as img:
                img.thumbnail((104, 104), Image.Resampling.BOX)
                if img.mode in ('RGBA', 'LA', 'P'):
                    bg = Image.new('RGB', img.size, (18, 20, 29))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode in ('RGBA', 'LA'):
                        bg.paste(img, mask=img.split()[-1])
                    img = bg
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(t_path, format='JPEG', quality=82, optimize=True)
            return send_from_directory(TEMP_FOLDER, t_name, mimetype='image/jpeg')
        except Exception:
            return send_from_directory(COMPRESSED_FOLDER, safe_name)

    return jsonify({'error': 'Not found'}), 404


@app.route('/preview/<filename>')
def preview_file(filename):
    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify({'error': 'Invalid filename'}), 400
    return send_from_directory(COMPRESSED_FOLDER, safe_name)


@app.route('/original/<filename>')
def original_file(filename):
    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify({'error': 'Invalid filename'}), 400
    return send_from_directory(UPLOAD_FOLDER, safe_name)


@app.route('/health')
def health():
    """Used by launcher to detect when server is ready."""
    return jsonify({'status': 'ok'}), 200


@app.route('/open-folder', methods=['POST'])
def open_folder():
    """Opens the compressed files directory in Windows File Explorer."""
    try:
        os.makedirs(COMPRESSED_FOLDER, exist_ok=True)
        os.startfile(COMPRESSED_FOLDER)
        return jsonify({'status': 'ok', 'path': COMPRESSED_FOLDER})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/clear-workspace', methods=['POST'])
def clear_workspace():
    """Immediately remove all temporary session files when user clears queue or resets."""
    cleaned = 0
    for folder in [UPLOAD_FOLDER, COMPRESSED_FOLDER, TEMP_FOLDER]:
        if not os.path.exists(folder):
            continue
        for f in os.listdir(folder):
            fpath = os.path.join(folder, f)
            if os.path.isfile(fpath):
                try:
                    os.remove(fpath)
                    cleaned += 1
                except Exception:
                    pass
    return jsonify({'cleaned': cleaned})


@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Remove files older than 1 hour."""
    now     = time.time()
    cleaned = 0
    for folder in [UPLOAD_FOLDER, COMPRESSED_FOLDER, TEMP_FOLDER]:
        if not os.path.exists(folder):
            continue
        for f in os.listdir(folder):
            fpath = os.path.join(folder, f)
            if os.path.isfile(fpath) and now - os.path.getmtime(fpath) > 3600:
                try:
                    os.remove(fpath)
                    cleaned += 1
                except Exception:
                    pass
    return jsonify({'cleaned': cleaned})


# ─── Native Win32 Desktop Window Controls ─────────────────────────────────────


@app.route('/window/drag', methods=['POST'])
def window_drag():
    if _window_hwnd:
        try:
            user32.ReleaseCapture()
            user32.PostMessageW(_window_hwnd, 0x0112, 0xF012, 0)
        except Exception:
            pass
    return jsonify({'status': 'ok'})


@app.route('/window/move', methods=['POST'])
def window_move():
    if _window_hwnd:
        try:
            data = request.get_json(silent=True) or {}
            dx = int(data.get('dx', 0))
            dy = int(data.get('dy', 0))
            if dx != 0 or dy != 0:
                rect = (ctypes.c_long * 4)()
                user32.GetWindowRect(_window_hwnd, ctypes.byref(rect))
                user32.SetWindowPos(_window_hwnd, 0, rect[0] + dx, rect[1] + dy, 0, 0, 0x0001 | 0x0010)
        except Exception:
            pass
    return jsonify({'status': 'ok'})


@app.route('/window/minimize', methods=['POST'])
def window_minimize():
    if _window_hwnd:
        try:
            user32.ShowWindow(_window_hwnd, 6)  # SW_MINIMIZE
        except Exception:
            pass
    return jsonify({'status': 'ok'})


@app.route('/window/maximize', methods=['POST'])
def window_maximize():
    if _window_hwnd:
        try:
            is_max = bool(user32.IsZoomed(_window_hwnd))
            if is_max:
                user32.ShowWindow(_window_hwnd, 9)  # SW_RESTORE
                return jsonify({'maximized': False})
            else:
                user32.ShowWindow(_window_hwnd, 3)  # SW_MAXIMIZE
                return jsonify({'maximized': True})
        except Exception:
            pass
    return jsonify({'maximized': False})


@app.route('/window/close', methods=['POST'])
def window_close():
    try:
        def terminate():
            time.sleep(0.08)
            os._exit(0)
        threading.Thread(target=terminate, daemon=True).start()
    except Exception:
        os._exit(0)
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
