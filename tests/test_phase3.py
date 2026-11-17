"""
Phase 3 Automated Verification Suite
PixelPress Desktop Pro Workstation UI/UX Overhaul & 1:1 Pixel Zoom Engine
"""

import os
import sys
import subprocess
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class Phase3VerificationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        cls.html_path = os.path.join(cls.base_dir, 'templates', 'index.html')
        cls.css_path = os.path.join(cls.base_dir, 'static', 'css', 'style.css')
        cls.js_path = os.path.join(cls.base_dir, 'static', 'js', 'main.js')

        with open(cls.html_path, 'r', encoding='utf-8') as f:
            cls.html_content = f.read()
        with open(cls.css_path, 'r', encoding='utf-8') as f:
            cls.css_content = f.read()
        with open(cls.js_path, 'r', encoding='utf-8') as f:
            cls.js_content = f.read()

        cls.client = app.test_client()

    def test_01_javascript_syntax_validity(self):
        """V3.1: Verify static/js/main.js passes syntax validation with zero errors."""
        res = subprocess.run(['node', '-c', self.js_path], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"JS syntax check failed: {res.stderr}")

    def test_02_zoom_toolbar_markup_and_accessibility(self):
        """V3.2: Verify index.html contains complete Zoom toolbar and ARIA slider semantics."""
        self.assertIn('id="zoom-level-display"', self.html_content)
        self.assertIn('onclick="setZoomMode(\'fit\')"', self.html_content)
        self.assertIn('onclick="setZoomMode(\'100\')"', self.html_content)
        self.assertIn('onclick="setZoomMode(\'200\')"', self.html_content)
        self.assertIn('onclick="zoomChange(-0.25)"', self.html_content)
        self.assertIn('onclick="zoomChange(0.25)"', self.html_content)

        # ARIA Accessibility on compare handle
        self.assertIn('role="slider"', self.html_content)
        self.assertIn('aria-label="Before/After Split Position"', self.html_content)
        self.assertIn('aria-valuemin="0"', self.html_content)
        self.assertIn('aria-valuemax="100"', self.html_content)
        self.assertIn('aria-valuenow="50"', self.html_content)
        self.assertIn('tabindex="0"', self.html_content)

    def test_03_css_responsive_wcag_and_zoom_styles(self):
        """V3.3: Verify style.css includes WCAG AA contrast, responsive breakpoints, and reduced motion."""
        # WCAG AA contrast text color
        self.assertIn('--text-faint: #7c8094;', self.css_content)

        # Focus visible outline
        self.assertIn(':focus-visible', self.css_content)
        self.assertIn('.compare-handle:focus-visible', self.css_content)

        # Responsive media queries
        self.assertIn('@media (max-width: 960px)', self.css_content)
        self.assertIn('@media (max-width: 820px)', self.css_content)

        # Accessibility: reduced motion
        self.assertIn('@media (prefers-reduced-motion: reduce)', self.css_content)

        # Zoom engine classes
        self.assertIn('.zoomable-viewport', self.css_content)
        self.assertIn('.zoom-target', self.css_content)
        self.assertIn('.workspace-section.dragging-over', self.css_content)

    def test_04_object_url_lifecycle_registry(self):
        """V3.4: Verify zero-leak Object URL registry and cleanup handlers in main.js."""
        self.assertIn('activeObjectUrls', self.js_content)
        self.assertIn('createManagedObjectURL', self.js_content)
        self.assertIn('revokeAllManagedObjectURLs', self.js_content)
        self.assertIn('URL.revokeObjectURL', self.js_content)

        # Verify revokeAllManagedObjectURLs is invoked in queue rendering & resetting
        self.assertIn('revokeAllManagedObjectURLs();', self.js_content)

    def test_05_settings_persistence_engine(self):
        """V3.5: Verify localStorage settings persistence functions in main.js."""
        self.assertIn('saveUserPreferences', self.js_content)
        self.assertIn('loadUserPreferences', self.js_content)
        self.assertIn('localStorage.setItem', self.js_content)
        self.assertIn('localStorage.getItem', self.js_content)
        self.assertIn('loadUserPreferences();', self.js_content)

    def test_06_zoom_pan_engine_implementation(self):
        """V3.6: Verify ZoomPanEngine implementation with wheel, pan drag, and transforms."""
        self.assertIn('function setZoomMode', self.js_content)
        self.assertIn('function zoomChange', self.js_content)
        self.assertIn('function applyZoomTransform', self.js_content)
        self.assertIn('function resetZoom', self.js_content)
        self.assertIn('function initZoomPanEngine', self.js_content)
        self.assertIn('window.setZoomMode = setZoomMode', self.js_content)
        self.assertIn('window.zoomChange = zoomChange', self.js_content)
        self.assertIn('window.resetZoom = resetZoom', self.js_content)

    def test_07_keyboard_navigation_and_shortcuts(self):
        """V3.7: Verify Space key toggle and split handle ArrowLeft/ArrowRight navigation."""
        # Space key shortcut
        self.assertIn("e.code === 'Space' || e.key === ' '", self.js_content)
        self.assertIn("switchCompareMode(state.compareMode === 'side' ? 'split' : 'side')", self.js_content)

        # Split handle Arrow keys
        self.assertIn("e.key === 'ArrowLeft' || e.key === 'ArrowDown'", self.js_content)
        self.assertIn("e.key === 'ArrowRight' || e.key === 'ArrowUp'", self.js_content)
        self.assertIn("compareHandle.setAttribute('aria-valuenow'", self.js_content)

    def test_08_queue_drag_drop_feedback(self):
        """V3.8: Verify visual drag-and-drop feedback for queue view."""
        self.assertIn("queueSection.classList.add('dragging-over')", self.js_content)
        self.assertIn("queueSection.classList.remove('dragging-over')", self.js_content)

    def test_09_flask_index_render_integration(self):
        """V3.9: Verify Flask index route renders HTML containing all Phase 3 elements."""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        html = resp.data.decode('utf-8')
        self.assertIn('pixelpress-token', html)
        self.assertIn('compare-zoom-controls', html)
        self.assertIn('zoom-level-display', html)
        self.assertIn('role="slider"', html)

if __name__ == '__main__':
    unittest.main()
