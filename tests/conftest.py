"""
Pytest Test Fixtures for PixelPress Desktop Pro
Provides Flask test clients, auth headers, and synthetic test images.
"""

import os
import io
import sys
import pytest
from PIL import Image, ImageCms

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, get_auth_token

TEST_TOKEN = "test_pixelpress_secret_session_token_12345"

@pytest.fixture(scope="session", autouse=True)
def setup_app_token():
    """Ensure Flask app has a deterministic test token."""
    app.config['PIXELPRESS_AUTH_TOKEN'] = TEST_TOKEN
    app.config['TESTING'] = True
    yield
    app.config['TESTING'] = False

@pytest.fixture
def auth_token():
    return TEST_TOKEN

@pytest.fixture
def client():
    with app.test_client() as c:
        yield c

@pytest.fixture
def auth_headers(auth_token):
    return {'X-PixelPress-Token': auth_token}

@pytest.fixture
def sample_rgb_jpeg():
    buf = io.BytesIO()
    im = Image.new('RGB', (120, 120), color=(220, 80, 40))
    im.save(buf, format='JPEG', quality=90)
    buf.seek(0)
    return buf

@pytest.fixture
def sample_rgba_png():
    buf = io.BytesIO()
    im = Image.new('RGBA', (100, 100), color=(50, 150, 250, 180))
    im.save(buf, format='PNG')
    buf.seek(0)
    return buf

@pytest.fixture
def sample_cmyk_jpeg():
    buf = io.BytesIO()
    im = Image.new('CMYK', (80, 80), color=(100, 50, 0, 20))
    im.save(buf, format='JPEG')
    buf.seek(0)
    return buf

@pytest.fixture
def sample_animated_gif():
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

@pytest.fixture
def sample_animated_webp():
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

@pytest.fixture
def sample_icc_jpeg():
    buf = io.BytesIO()
    srgb = ImageCms.createProfile('sRGB')
    icc_bytes = ImageCms.ImageCmsProfile(srgb).tobytes()
    im = Image.new('RGB', (80, 80), color=(120, 200, 80))
    im.save(buf, format='JPEG', quality=95, icc_profile=icc_bytes)
    buf.seek(0)
    return buf
