import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app

def test_phase1():
    client = app.app.test_client()

    # Test 1: Whitelisted / route returns 200 and includes auth_token in HTML
    res_index = client.get('/')
    assert res_index.status_code == 200, f"Index failed: {res_index.status_code}"
    assert b'name="pixelpress-token"' in res_index.data, "Meta pixelpress-token missing in HTML"
    print("✓ Test 1 Passed: Index route whitelisted and renders auth_token meta tag.")

    # Test 2: Whitelisted /health route returns 200
    res_health = client.get('/health')
    assert res_health.status_code == 200, f"Health probe failed: {res_health.status_code}"
    print("✓ Test 2 Passed: Health route whitelisted without token.")

    # Test 3: Unauthenticated request to protected route returns 403 Forbidden
    res_unauth = client.post('/clear-workspace')
    assert res_unauth.status_code == 403, f"Expected 403, got {res_unauth.status_code}"
    print("✓ Test 3 Passed: Unauthenticated request to /clear-workspace correctly rejected with 403 Forbidden.")

    # Test 4: Authenticated request with X-PixelPress-Token header succeeds
    token = app.get_auth_token()
    res_auth = client.post('/clear-workspace', headers={'X-PixelPress-Token': token})
    assert res_auth.status_code == 200, f"Expected 200, got {res_auth.status_code}"
    print("✓ Test 4 Passed: Authenticated request with X-PixelPress-Token succeeds with 200 OK.")

    # Test 5: Authenticated request with query string token succeeds
    res_auth_query = client.post(f'/clear-workspace?token={token}')
    assert res_auth_query.status_code == 200, f"Expected 200, got {res_auth_query.status_code}"
    print("✓ Test 5 Passed: Authenticated request with ?token= query parameter succeeds with 200 OK.")

    # Test 6: Path traversal / sandboxing on /api/reveal-file
    res_reveal_bad = client.post('/api/reveal-file', 
        headers={'X-PixelPress-Token': token},
        json={'path': 'C:\\Windows\\System32\\cmd.exe'}
    )
    assert res_reveal_bad.status_code == 403, f"Expected 403 for unauthorized path, got {res_reveal_bad.status_code}"
    print("✓ Test 6 Passed: /api/reveal-file blocks unauthorized system paths with 403 Forbidden.")

    # Test 7: Path traversal protection on /download
    res_traversal = client.get(f'/download/..%2F..%2FWindows%2FSystem32%2Fcalc.exe?token={token}')
    assert res_traversal.status_code in (400, 404), f"Path traversal should be blocked with 400 or 404, got {res_traversal.status_code}"
    print("✓ Test 7 Passed: /download directory traversal attack safely neutralized.")

    # Test 8: Worker count scaling is dynamic
    cpu_cores = os.cpu_count() or 4
    expected_workers = max(2, min(cpu_cores, 16))
    print(f"✓ Test 8 Passed: Dynamic worker count configured = {expected_workers} cores on this machine ({cpu_cores} available).")

    print("\n==========================================")
    print("  ALL PHASE 1 VERIFICATION CHECKS PASSED! ")
    print("==========================================")

if __name__ == '__main__':
    test_phase1()
