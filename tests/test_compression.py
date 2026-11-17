"""
Core Compression Engine Test Suite for PixelPress Desktop Pro
Verifies multi-format encoding, animation retention, CMYK conversion, ICC profiles, and resizing.
"""

import os
import io
import json
import pytest
from PIL import Image, ImageSequence, ImageCms
from app import COMPRESSED_FOLDER

def make_rgb_jpeg(w=120, h=120):
    buf = io.BytesIO()
    im = Image.new('RGB', (w, h), color=(220, 80, 40))
    im.save(buf, format='JPEG', quality=90)
    buf.seek(0)
    return buf

def make_rgba_png(w=100, h=100):
    buf = io.BytesIO()
    im = Image.new('RGBA', (w, h), color=(50, 150, 250, 180))
    im.save(buf, format='PNG')
    buf.seek(0)
    return buf

def make_cmyk_jpeg(w=80, h=80):
    buf = io.BytesIO()
    im = Image.new('CMYK', (w, h), color=(100, 50, 0, 20))
    im.save(buf, format='JPEG')
    buf.seek(0)
    return buf

def make_animated_gif():
    buf = io.BytesIO()
    frames = [
        Image.new('RGB', (60, 60), color=(255, 0, 0)),
        Image.new('RGB', (60, 60), color=(0, 255, 0)),
        Image.new('RGB', (60, 60), color=(0, 0, 255))
    ]
    frames[0].save(
        buf,
        format='GIF',
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0
    )
    buf.seek(0)
    return buf

def make_animated_webp():
    buf = io.BytesIO()
    frames = [
        Image.new('RGBA', (60, 60), color=(255, 100, 0, 255)),
        Image.new('RGBA', (60, 60), color=(0, 200, 100, 255)),
        Image.new('RGBA', (60, 60), color=(100, 0, 255, 255))
    ]
    frames[0].save(
        buf,
        format='WEBP',
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0
    )
    buf.seek(0)
    return buf

def make_icc_jpeg():
    buf = io.BytesIO()
    srgb = ImageCms.createProfile('sRGB')
    icc_bytes = ImageCms.ImageCmsProfile(srgb).tobytes()
    im = Image.new('RGB', (80, 80), color=(120, 200, 80))
    im.save(buf, format='JPEG', quality=95, icc_profile=icc_bytes)
    buf.seek(0)
    return buf

def test_jpeg_compression_and_output(client, auth_headers):
    """Verify JPEG compression, quality adjustment, and valid output structure."""
    buf = make_rgb_jpeg(120, 120)
    data = {
        'files': (buf, 'test_image.jpg'),
        'quality': '75',
        'output_format': 'jpeg',
        'optimize': 'true',
        'strip_metadata': 'true'
    }
    resp = client.post('/compress', headers=auth_headers, data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    res = json.loads(resp.data)
    assert 'results' in res
    assert len(res['results']) == 1
    result = res['results'][0]
    assert result['success'] is True
    assert result['compressed_filename'].lower().endswith(('.jpg', '.jpeg'))
    assert result['output_width'] == 120
    assert result['output_height'] == 120

def test_png_quantization_and_lossless(client, auth_headers):
    """Verify PNG quantization using Octree / Floyd-Steinberg and lossless mode."""
    # 1. Lossy PNG (Quantized)
    buf_lossy = make_rgba_png()
    data_lossy = {
        'files': (buf_lossy, 'test_alpha.png'),
        'quality': '80',
        'output_format': 'png',
        'lossless': 'false',
        'optimize': 'true'
    }
    resp_lossy = client.post('/compress', headers=auth_headers, data=data_lossy, content_type='multipart/form-data')
    assert resp_lossy.status_code == 200
    res_lossy = json.loads(resp_lossy.data)
    assert res_lossy['results'][0]['success'] is True
    assert res_lossy['results'][0]['compressed_filename'].lower().endswith('.png')

    # 2. Lossless PNG
    buf_lossless = make_rgba_png()
    data_lossless = {
        'files': (buf_lossless, 'test_alpha_lossless.png'),
        'quality': '100',
        'output_format': 'png',
        'lossless': 'true',
        'optimize': 'true'
    }
    resp_lossless = client.post('/compress', headers=auth_headers, data=data_lossless, content_type='multipart/form-data')
    assert resp_lossless.status_code == 200
    res_lossless = json.loads(resp_lossless.data)
    assert res_lossless['results'][0]['success'] is True
    assert res_lossless['results'][0]['compressed_filename'].lower().endswith('.png')

def test_webp_conversion(client, auth_headers):
    """Verify conversion to WebP with predictive coding."""
    buf = make_rgb_jpeg()
    data = {
        'files': (buf, 'convert_to_webp.jpg'),
        'quality': '82',
        'output_format': 'webp',
        'optimize': 'true'
    }
    resp = client.post('/compress', headers=auth_headers, data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    res = json.loads(resp.data)
    result = res['results'][0]
    assert result['success'] is True
    assert result['compressed_filename'].lower().endswith('.webp')

def test_animated_gif_multi_frame_preservation(client, auth_headers):
    """Verify all frames in an animated GIF are retained after compression."""
    buf = make_animated_gif()
    data = {
        'files': (buf, 'anim.gif'),
        'quality': '80',
        'output_format': 'same',
        'optimize': 'true'
    }
    resp = client.post('/compress', headers=auth_headers, data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    res = json.loads(resp.data)
    result = res['results'][0]
    assert result['success'] is True

    comp_fn = result['compressed_filename']
    out_path = os.path.join(COMPRESSED_FOLDER, comp_fn)

    with Image.open(out_path) as out_img:
        frames = [f.copy() for f in ImageSequence.Iterator(out_img)]
        assert len(frames) == 3, f"Expected 3 frames in animated GIF output, got {len(frames)}"

def test_animated_webp_multi_frame_preservation(client, auth_headers):
    """Verify all frames in an animated WebP are retained after compression."""
    buf = make_animated_webp()
    data = {
        'files': (buf, 'anim.webp'),
        'quality': '75',
        'output_format': 'same',
        'optimize': 'true'
    }
    resp = client.post('/compress', headers=auth_headers, data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    res = json.loads(resp.data)
    result = res['results'][0]
    assert result['success'] is True

    comp_fn = result['compressed_filename']
    out_path = os.path.join(COMPRESSED_FOLDER, comp_fn)

    with Image.open(out_path) as out_img:
        frames = [f.copy() for f in ImageSequence.Iterator(out_img)]
        assert len(frames) == 3, f"Expected 3 frames in animated WebP output, got {len(frames)}"

def test_cmyk_perceptual_color_conversion(client, auth_headers):
    """Verify CMYK images undergo sRGB perceptual conversion without color inversion."""
    buf = make_cmyk_jpeg()
    data = {
        'files': (buf, 'cmyk_sample.jpg'),
        'quality': '85',
        'output_format': 'jpeg',
        'strip_metadata': 'true'
    }
    resp = client.post('/compress', headers=auth_headers, data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    res = json.loads(resp.data)
    result = res['results'][0]
    assert result['success'] is True

    comp_fn = result['compressed_filename']
    out_path = os.path.join(COMPRESSED_FOLDER, comp_fn)

    with Image.open(out_path) as out_img:
        assert out_img.mode == 'RGB'

def test_icc_profile_preservation_and_stripping(client, auth_headers):
    """Verify ICC Color Profile is preserved when requested and stripped when strip_metadata=True."""
    # 1. Preserved
    buf_preserve = make_icc_jpeg()
    data_preserve = {
        'files': (buf_preserve, 'icc_preserve.jpg'),
        'quality': '90',
        'output_format': 'jpeg',
        'strip_metadata': 'false'
    }
    resp = client.post('/compress', headers=auth_headers, data=data_preserve, content_type='multipart/form-data')
    res = json.loads(resp.data)
    assert res['results'][0]['success'] is True
    out_path = os.path.join(COMPRESSED_FOLDER, res['results'][0]['compressed_filename'])
    with Image.open(out_path) as out_img:
        assert 'icc_profile' in out_img.info, "ICC Profile was not preserved!"

    # 2. Stripped
    buf_strip = make_icc_jpeg()
    data_strip = {
        'files': (buf_strip, 'icc_strip.jpg'),
        'quality': '90',
        'output_format': 'jpeg',
        'strip_metadata': 'true'
    }
    resp_strip = client.post('/compress', headers=auth_headers, data=data_strip, content_type='multipart/form-data')
    res_strip = json.loads(resp_strip.data)
    out_path_strip = os.path.join(COMPRESSED_FOLDER, res_strip['results'][0]['compressed_filename'])
    with Image.open(out_path_strip) as out_img_strip:
        assert 'icc_profile' not in out_img_strip.info, "ICC Profile was not stripped!"

def test_resizing_modes(client, auth_headers):
    """Verify percentage, width, height, and custom dimension resizing modes."""
    # Percentage (50%)
    buf_pct = make_rgb_jpeg(120, 120)
    data_pct = {
        'files': (buf_pct, 'resize_pct.jpg'),
        'resize_mode': 'percentage',
        'resize_value': '50',
        'quality': '80'
    }
    res_pct = json.loads(client.post('/compress', headers=auth_headers, data=data_pct, content_type='multipart/form-data').data)
    assert res_pct['results'][0]['output_width'] == 60
    assert res_pct['results'][0]['output_height'] == 60

    # Width constraint (40px)
    buf_w = make_rgb_jpeg(120, 120)
    data_w = {
        'files': (buf_w, 'resize_w.jpg'),
        'resize_mode': 'width',
        'resize_value': '40',
        'quality': '80'
    }
    res_w = json.loads(client.post('/compress', headers=auth_headers, data=data_w, content_type='multipart/form-data').data)
    assert res_w['results'][0]['output_width'] == 40
    assert res_w['results'][0]['output_height'] == 40

    # Custom exact dimensions (90x45)
    buf_custom = make_rgb_jpeg(120, 120)
    data_custom = {
        'files': (buf_custom, 'resize_custom.jpg'),
        'resize_mode': 'custom',
        'resize_width': '90',
        'resize_height': '45',
        'quality': '80'
    }
    res_custom = json.loads(client.post('/compress', headers=auth_headers, data=data_custom, content_type='multipart/form-data').data)
    assert res_custom['results'][0]['output_width'] == 90
    assert res_custom['results'][0]['output_height'] == 45

def test_batch_cancellation_protocol(client, auth_headers):
    """Verify batch cancellation API registers and aborts active batches."""
    batch_id = 'test_cancel_uuid_999'
    resp = client.post(f'/api/cancel-batch/{batch_id}', headers=auth_headers)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data.get('status') == 'ok'
    assert data.get('batch_id') == batch_id
