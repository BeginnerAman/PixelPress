import os
import sys
import io
import time
from PIL import Image, ImageCms

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app

def test_phase2():
    temp_dir = os.path.join(os.path.dirname(__file__), 'tmp_phase2')
    os.makedirs(temp_dir, exist_ok=True)

    # ── Test 1: Animated GIF Multi-Frame Preservation ──
    gif_in = os.path.join(temp_dir, 'sample_anim.gif')
    gif_out = os.path.join(temp_dir, 'sample_anim_opt.gif')
    frames = [Image.new('RGB', (60, 60), color) for color in ['red', 'green', 'blue', 'yellow']]
    frames[0].save(gif_in, format='GIF', save_all=True, append_images=frames[1:], duration=120, loop=0)

    settings_gif = {'output_format': 'same', 'quality': 85, 'optimize': True}
    res_path, out_w, out_h = app.compress_image(gif_in, gif_out, settings_gif)
    with Image.open(res_path) as out_gif:
        assert getattr(out_gif, 'is_animated', False), "Output GIF must retain animation flag"
        assert out_gif.n_frames == 4, f"Output GIF must retain 4 frames, found {out_gif.n_frames}"
        assert out_gif.info.get('duration') == 120, "Output GIF must retain frame duration"
    print("✓ Test 1 Passed: Animated GIF multi-frame retention verified (4/4 frames preserved).")

    # ── Test 2: Animated WebP Multi-Frame Preservation ──
    webp_in = os.path.join(temp_dir, 'sample_anim.webp')
    webp_out = os.path.join(temp_dir, 'sample_anim_opt.webp')
    webp_frames = [Image.new('RGB', (50, 50), color) for color in ['purple', 'cyan', 'orange']]
    webp_frames[0].save(webp_in, format='WEBP', save_all=True, append_images=webp_frames[1:], duration=150, loop=0)

    settings_webp = {'output_format': 'webp', 'quality': 80, 'lossless': False}
    res_path, out_w, out_h = app.compress_image(webp_in, webp_out, settings_webp)
    with Image.open(res_path) as out_webp:
        assert getattr(out_webp, 'is_animated', False), "Output WebP must retain animation flag"
        assert out_webp.n_frames == 3, f"Output WebP must retain 3 frames, found {out_webp.n_frames}"
    print("✓ Test 2 Passed: Animated WebP multi-frame retention verified (3/3 frames preserved).")

    # ── Test 3: CMYK to RGB Clean Conversion ──
    cmyk_in = os.path.join(temp_dir, 'sample_cmyk.jpg')
    cmyk_out = os.path.join(temp_dir, 'sample_cmyk_opt.jpg')
    cmyk_img = Image.new('CMYK', (80, 80), (0, 100, 100, 0)) # Pure Cyan/Magenta/Yellow blend
    cmyk_img.save(cmyk_in, format='JPEG')

    settings_cmyk = {'output_format': 'jpeg', 'quality': 85}
    res_path, out_w, out_h = app.compress_image(cmyk_in, cmyk_out, settings_cmyk)
    with Image.open(res_path) as out_cmyk:
        assert out_cmyk.mode == 'RGB', f"Output must be converted to RGB, got {out_cmyk.mode}"
        pixel = out_cmyk.getpixel((10, 10))
        assert pixel[0] > 200, f"Red channel must be preserved without inversion, got {pixel}"
    print("✓ Test 3 Passed: CMYK conversion executed cleanly without neon color inversion.")

    # ── Test 4: ICC Color Profile Retention ──
    srgb_profile = ImageCms.createProfile('sRGB')
    srgb_bytes = ImageCms.ImageCmsProfile(srgb_profile).tobytes()

    icc_in = os.path.join(temp_dir, 'sample_icc.jpg')
    icc_out = os.path.join(temp_dir, 'sample_icc_opt.jpg')
    base_img = Image.new('RGB', (100, 100), (45, 120, 200))
    base_img.save(icc_in, format='JPEG', icc_profile=srgb_bytes)

    # 4a: Strip metadata = False -> ICC preserved
    settings_keep_icc = {'output_format': 'jpeg', 'quality': 90, 'strip_metadata': False}
    res_path, _, _ = app.compress_image(icc_in, icc_out, settings_keep_icc)
    with Image.open(res_path) as out_icc:
        assert 'icc_profile' in out_icc.info, "ICC profile must be preserved when strip_metadata=False"
    print("✓ Test 4a Passed: ICC Profile preserved on JPEG output.")

    # 4b: Strip metadata = True -> ICC stripped
    icc_out_strip = os.path.join(temp_dir, 'sample_icc_stripped.jpg')
    settings_strip_icc = {'output_format': 'jpeg', 'quality': 90, 'strip_metadata': True}
    res_path, _, _ = app.compress_image(icc_in, icc_out_strip, settings_strip_icc)
    with Image.open(res_path) as out_strip:
        assert 'icc_profile' not in out_strip.info, "ICC profile must be stripped when strip_metadata=True"
    print("✓ Test 4b Passed: ICC Profile stripped cleanly when requested.")

    # ── Test 5: Decompression Bomb Limit ──
    assert Image.MAX_IMAGE_PIXELS == 250_000_000, f"Expected 250MP limit, got {Image.MAX_IMAGE_PIXELS}"
    print(f"✓ Test 5 Passed: Decompression bomb ceiling elevated to {Image.MAX_IMAGE_PIXELS:,} pixels (250MP).")

    # ── Test 6: Backend Batch Cancellation Protocol ──
    client = app.app.test_client()
    token = app.get_auth_token()
    test_batch_id = 'test_cancel_batch_99'
    res_cancel = client.post(f'/api/cancel-batch/{test_batch_id}', headers={'X-PixelPress-Token': token})
    assert res_cancel.status_code == 200, f"Expected 200, got {res_cancel.status_code}"
    json_data = res_cancel.get_json()
    assert json_data.get('cancelled') is True, "Batch must be marked as cancelled"
    with app._active_batches_lock:
        assert app._active_batches.get(test_batch_id, {}).get('cancelled') is True
    print("✓ Test 6 Passed: Backend Batch Cancellation API & lock registry verified.")

    # Clean up test files
    import shutil
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass

    print("\n==========================================")
    print("  ALL PHASE 2 VERIFICATION CHECKS PASSED! ")
    print("==========================================")

if __name__ == '__main__':
    test_phase2()
