"""Regression checks for packaging the complete Sketch build."""

import argparse
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import build_site


class BuildSiteTests(unittest.TestCase):
    def test_includes_shared_lazy_and_nested_assets(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            website = root / "website"
            website.mkdir()
            (website / "index.html").write_text("<html><body></body></html>")
            bundle = root / "dist"
            files = {
                "sketch.js": 'import "./building.js";',
                "sketch.css": "canvas {}",
                "building.js": "export {};",
                "2026xmas.js": "export {};",
                "assets/example.svg": "<svg/>",
            }
            for name, content in files.items():
                target = bundle / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content)
            output = root / "output"
            args = argparse.Namespace(sketch_dist=bundle, output=output)
            with patch.object(build_site, "ROOT", website), patch.object(
                build_site, "arguments", return_value=args
            ):
                self.assertEqual(build_site.main(), 0)
            for name, content in files.items():
                self.assertEqual(
                    (output / "design/sketch/assets" / name).read_text(), content
                )


if __name__ == "__main__":
    unittest.main()
