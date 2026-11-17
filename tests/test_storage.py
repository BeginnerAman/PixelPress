"""
Storage Management & Workspace Lifecycle Test Suite for PixelPress Desktop Pro
Verifies LocalAppData vs Portable resolution, file cleanup, and workspace clearing.
"""

import os
import time
import json
import pytest
from app import get_storage_root, get_base_dir, user_data_path, UPLOAD_FOLDER, COMPRESSED_FOLDER, TEMP_FOLDER

def test_storage_root_default_resolution():
    """Verify default storage resolves to %LOCALAPPDATA%/PixelPress."""
    root = get_storage_root()
    expected_appdata = os.environ.get('LOCALAPPDATA')
    if expected_appdata:
        assert expected_appdata.lower() in root.lower()
        assert 'pixelpress' in root.lower()
    assert os.path.exists(root)

def test_storage_root_portable_resolution(tmp_path, monkeypatch):
    """Verify that when a portable marker (.portable) exists next to executable, PixelPress_Data is used."""
    fake_base = str(tmp_path)
    marker = os.path.join(fake_base, '.portable')
    with open(marker, 'w') as f:
        f.write('')

    import app as app_module
    monkeypatch.setattr(app_module, 'get_base_dir', lambda: fake_base)

    resolved = app_module.get_storage_root()
    assert resolved == os.path.join(fake_base, 'PixelPress_Data')
    assert os.path.exists(resolved)

def test_clear_workspace_endpoint(client, auth_headers):
    """Verify /clear-workspace removes all files in upload, compressed, and temp folders."""
    test_file_path = os.path.join(UPLOAD_FOLDER, 'dummy_test_to_clear.tmp')
    with open(test_file_path, 'w') as f:
        f.write('dummy content')

    assert os.path.exists(test_file_path)

    resp = client.post('/clear-workspace', headers=auth_headers)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert 'cleaned' in data
    assert not os.path.exists(test_file_path)

def test_cleanup_expired_files_endpoint(client, auth_headers):
    """Verify /cleanup removes files older than 3600 seconds."""
    expired_file = os.path.join(TEMP_FOLDER, 'expired_test_file.tmp')
    with open(expired_file, 'w') as f:
        f.write('expired content')

    # Artificially age the file by 2 hours (7200 seconds)
    old_time = time.time() - 7200
    os.utime(expired_file, (old_time, old_time))

    resp = client.post('/cleanup', headers=auth_headers)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert 'cleaned' in data
    assert not os.path.exists(expired_file)
