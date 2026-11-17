"""
Security & Privacy Audit Test Suite for PixelPress Desktop Pro
Verifies token gatekeeper, CSRF/rebinding defense, path traversal sandboxing, and safe downloads.
"""

import os
import json
import pytest

def test_whitelisted_routes_accessible_without_token(client):
    """Verify public endpoints return 200 without requiring session auth token."""
    resp_index = client.get('/')
    assert resp_index.status_code == 200
    assert b'pixelpress-token' in resp_index.data

    resp_health = client.get('/health')
    assert resp_health.status_code == 200
    data = json.loads(resp_health.data)
    assert data.get('status') == 'ok'

def test_protected_routes_blocked_without_token(client):
    """Verify unauthorized external callers (e.g., malicious browser DNS rebinding) receive 403."""
    endpoints = [
        ('/clear-workspace', 'POST'),
        ('/open-folder', 'POST'),
        ('/window/minimize', 'POST'),
        ('/window/maximize', 'POST'),
        ('/api/save-file', 'POST'),
        ('/api/save-all-folder', 'POST'),
        ('/api/save-zip', 'POST'),
        ('/api/cancel-batch/dummy', 'POST'),
    ]
    for url, method in endpoints:
        if method == 'POST':
            resp = client.post(url)
        else:
            resp = client.get(url)
        assert resp.status_code == 403, f"Endpoint {url} was not protected with 403!"
        data = json.loads(resp.data)
        assert 'Unauthorized' in data.get('error', '')

def test_protected_routes_succeed_with_header_token(client, auth_headers):
    """Verify valid X-PixelPress-Token header grants access to protected routes."""
    resp = client.post('/clear-workspace', headers=auth_headers)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert 'cleaned' in data

def test_protected_routes_succeed_with_query_param_token(client, auth_token):
    """Verify ?token= query parameter grants access to protected endpoints."""
    resp = client.post(f'/clear-workspace?token={auth_token}')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert 'cleaned' in data

def test_api_reveal_file_blocks_external_system_paths(client, auth_headers):
    """Verify /api/reveal-file strictly blocks arbitrary system files outside workspace root."""
    forbidden_targets = [
        r'C:\Windows\System32\notepad.exe',
        r'C:\Windows\win.ini',
        r'C:\Users',
        r'..\app.py',
        r'/etc/passwd'
    ]
    for target in forbidden_targets:
        resp = client.post(
            '/api/reveal-file',
            headers=auth_headers,
            json={'path': target}
        )
        assert resp.status_code == 403, f"Arbitrary path {target} was not blocked!"
        data = json.loads(resp.data)
        assert 'Access denied' in data.get('error', '')

def test_download_directory_traversal_neutralized(client, auth_token):
    """Verify /download/<filename> neutralizes directory traversal payloads."""
    malicious_filenames = [
        '..%2F..%2Fapp.py',
        '..\\..\\app.py',
        '..%5C..%5Cwindows%5Cwin.ini',
        'sub/../../app.py'
    ]
    for fn in malicious_filenames:
        resp = client.get(f'/download/{fn}?token={auth_token}')
        # Should return 404 Not Found (or 403 if path validation fails)
        assert resp.status_code in [404, 403], f"Traversal payload {fn} was not safely blocked!"
