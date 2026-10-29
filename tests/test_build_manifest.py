"""
Tests for build_manifest.py. Run:  python -m unittest discover -s tests -v
Each test builds a throwaway copy of the repo layout, so nothing real is touched.
"""
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import build_manifest as bm  # noqa: E402

DESIGN = '---\nversion: "1.0"\nname: "Test Theme"\ndescription: "A test."\nppt:\n  accent: "FF0000"\n---\n# body\n'


def make_zip(path: Path, files: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as z:
        for name, data in files.items():
            z.writestr(name, data)


class BuildManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        # point the module at the temp tree
        self._old = (bm.ROOT, bm.CONFIG_PATH, bm.MANIFEST_PATH)
        bm.ROOT, bm.CONFIG_PATH, bm.MANIFEST_PATH = self.tmp, self.tmp / "repo.config.json", self.tmp / "manifest.json"
        self.cfg = {"owner": "me", "repo": "r", "ref": "v1", "author": "A", "minAppVersion": "1.0.0"}

    def tearDown(self):
        bm.ROOT, bm.CONFIG_PATH, bm.MANIFEST_PATH = self._old
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_theme_entry_has_checksum_url_and_kind(self):
        z = self.tmp / "themes" / "test-theme.zip"
        make_zip(z, {"DESIGN.md": DESIGN})
        (e,) = bm.collect(self.cfg)
        self.assertEqual(e["kind"], "theme")
        self.assertEqual(e["name"], "Test Theme")
        self.assertEqual(e["sha256"], hashlib.sha256(z.read_bytes()).hexdigest())
        self.assertEqual(e["downloadUrl"], "https://cdn.jsdelivr.net/gh/me/r@v1/themes/test-theme.zip")

    def test_look_ok_and_kind_from_folder(self):
        make_zip(self.tmp / "looks/static/neat.zip",
                 {"manifest.json": json.dumps({"name": "Neat"}), "engine.js": "const p=require('pptxgenjs');const fs=require('fs');"})
        (e,) = bm.collect(self.cfg)
        self.assertEqual((e["kind"], e["name"]), ("static", "Neat"))

    def test_look_requiring_forbidden_module_is_rejected(self):
        make_zip(self.tmp / "looks/standard/bad.zip",
                 {"manifest.json": "{}", "engine.js": "require('child_process')"})
        with self.assertRaises(bm.BuildError):
            bm.collect(self.cfg)

    def test_zip_slip_is_rejected(self):
        make_zip(self.tmp / "themes/evil.zip", {"../x/DESIGN.md": DESIGN})
        with self.assertRaises(bm.BuildError):
            bm.collect(self.cfg)

    def test_theme_without_design_md_is_rejected(self):
        make_zip(self.tmp / "themes/empty.zip", {"readme.txt": "hi"})
        with self.assertRaises(bm.BuildError):
            bm.collect(self.cfg)

    def test_bad_file_name_and_duplicates_rejected(self):
        make_zip(self.tmp / "themes/Bad Name.zip", {"DESIGN.md": DESIGN})
        with self.assertRaises(bm.BuildError):
            bm.collect(self.cfg)

    def test_duplicate_ids_across_kinds_rejected(self):
        make_zip(self.tmp / "themes/same.zip", {"DESIGN.md": DESIGN})
        make_zip(self.tmp / "looks/static/same.zip", {"manifest.json": "{}", "engine.js": "1"})
        with self.assertRaises(bm.BuildError):
            bm.collect(self.cfg)

    def test_preview_png_is_linked_when_present(self):
        make_zip(self.tmp / "themes/pic.zip", {"DESIGN.md": DESIGN})
        (self.tmp / "themes/pic.png").write_bytes(b"\x89PNG")
        (e,) = bm.collect(self.cfg)
        self.assertTrue(e["previewImageUrl"].endswith("themes/pic.png"))

    def test_main_writes_manifest_and_is_repeatable(self):
        make_zip(self.tmp / "themes/test-theme.zip", {"DESIGN.md": DESIGN})
        self.assertEqual(bm.main(["--owner", "me"]), 0)
        first = bm.MANIFEST_PATH.read_text(encoding="utf-8")
        self.assertEqual(bm.main([]), 0)
        self.assertEqual(first, bm.MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertEqual(json.loads(first)["version"], 2)


if __name__ == "__main__":
    unittest.main()
