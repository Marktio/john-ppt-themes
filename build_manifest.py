#!/usr/bin/env python3
"""
build_manifest.py  --  turns the zips in this repo into manifest.json.

Think of manifest.json as the menu, and the zips as the dishes. You drop new
zips into the folders below, run this script once, and the menu rewrites itself
(including a fingerprint for each zip so the app can tell if a file was
tampered with on the way).

Folders it scans (the folder decides the "kind"):
    themes/           *.zip  -> kind "theme"     (a DESIGN.md inside; just data)
    looks/standard/   *.zip  -> kind "standard"  (manifest.json + engine .js; runs code)
    looks/static/     *.zip  -> kind "static"    (same as above)

Optional preview picture: put <same-name>.png next to the zip.

Usage:
    python build_manifest.py                 # rebuild manifest.json
    python build_manifest.py --owner NAME    # also save your GitHub username
    python build_manifest.py --ref v1.0.0    # pin links to a tag (recommended for releases)
    python build_manifest.py --check         # validate only, write nothing

Only the Python standard library is used. Safe to run repeatedly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "repo.config.json"
MANIFEST_PATH = ROOT / "manifest.json"
MANIFEST_VERSION = 2
MAX_ZIP_BYTES = 5 * 1024 * 1024  # a theme/look is tiny; anything bigger is suspicious

# kind -> folder (relative to ROOT). Defined ONCE; everything else reads this.
KIND_FOLDERS = {
    "theme": "themes",
    "standard": "looks/standard",
    "static": "looks/static",
}

# A look's engine.js may only use these modules (same contract as the app's
# layout-pack-builder prompt). Anything else is flagged as an error.
ALLOWED_REQUIRES = {"pptxgenjs", "fs", "path"}

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
_FRONT_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.S)
_REQUIRE_RE = re.compile(r"""require\(\s*['"]([^'"]+)['"]\s*\)""")


class BuildError(Exception):
    pass


def load_config() -> dict:
    cfg = {"owner": "YOUR_GITHUB_USERNAME", "repo": "john-ppt-themes", "ref": "main",
           "author": "VOL PPT", "minAppVersion": "1.0.0"}
    if CONFIG_PATH.is_file():
        cfg.update(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
    return cfg


def save_config(cfg: dict) -> None:
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


def cdn_url(cfg: dict, rel_path: str) -> str:
    """jsDelivr serves any public GitHub file at this address, for free."""
    return f"https://cdn.jsdelivr.net/gh/{cfg['owner']}/{cfg['repo']}@{cfg['ref']}/{rel_path}"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _front_matter_field(text: str, key: str) -> str:
    m = _FRONT_RE.match(text)
    if not m:
        raise BuildError("DESIGN.md has no front-matter block (--- ... ---).")
    fm = re.search(rf'^{key}:\s*"?(.*?)"?\s*$', m.group(1), re.M)
    return fm.group(1).strip() if fm else ""


def _check_member_names(zf: zipfile.ZipFile, label: str) -> list[str]:
    names = zf.namelist()
    for n in names:
        p = PurePosixPath(n)
        if n.startswith(("/", "\\")) or ".." in p.parts or ":" in p.parts[0]:
            raise BuildError(f"{label}: unsafe path inside zip: {n}")
    return names


def inspect_theme(zip_path: Path) -> dict:
    with zipfile.ZipFile(zip_path) as zf:
        names = _check_member_names(zf, zip_path.name)
        designs = [n for n in names if PurePosixPath(n).name == "DESIGN.md"]
        if len(designs) != 1:
            raise BuildError(f"{zip_path.name}: expected exactly one DESIGN.md, found {len(designs)}.")
        text = zf.read(designs[0]).decode("utf-8", "replace")
    name = _front_matter_field(text, "name")
    if not name:
        raise BuildError(f"{zip_path.name}: DESIGN.md front-matter has no name.")
    return {"name": name, "description": _front_matter_field(text, "description")}


def inspect_look(zip_path: Path) -> dict:
    with zipfile.ZipFile(zip_path) as zf:
        names = _check_member_names(zf, zip_path.name)
        mans = [n for n in names if PurePosixPath(n).name == "manifest.json"]
        if len(mans) != 1:
            raise BuildError(f"{zip_path.name}: expected exactly one manifest.json, found {len(mans)}.")
        try:
            man = json.loads(zf.read(mans[0]).decode("utf-8"))
        except ValueError as e:
            raise BuildError(f"{zip_path.name}: manifest.json is not valid JSON ({e}).")
        engines = [n for n in names if n.lower().endswith(".js")]
        if not engines:
            raise BuildError(f"{zip_path.name}: no engine .js file inside.")
        for eng in engines:
            code = zf.read(eng).decode("utf-8", "replace")
            for mod in _REQUIRE_RE.findall(code):
                if mod not in ALLOWED_REQUIRES:
                    raise BuildError(
                        f"{zip_path.name}: {eng} requires '{mod}'. Looks may only use "
                        f"{sorted(ALLOWED_REQUIRES)}.")
    return {"name": str(man.get("name") or zip_path.stem), "description": str(man.get("description") or "")}


def collect(cfg: dict) -> list[dict]:
    entries, seen = [], set()
    for kind, folder in KIND_FOLDERS.items():
        d = ROOT / folder
        if not d.is_dir():
            continue
        for z in sorted(d.glob("*.zip")):
            tid = z.stem
            if not _ID_RE.match(tid):
                raise BuildError(f"{z.name}: file name must be lowercase letters, digits and hyphens only.")
            if tid in seen:
                raise BuildError(f"Two templates share the id '{tid}'. Rename one.")
            seen.add(tid)
            if z.stat().st_size > MAX_ZIP_BYTES:
                raise BuildError(f"{z.name}: bigger than {MAX_ZIP_BYTES // 1024 // 1024} MB.")
            if not zipfile.is_zipfile(z):
                raise BuildError(f"{z.name}: not a valid zip.")
            info = inspect_theme(z) if kind == "theme" else inspect_look(z)
            rel = f"{folder}/{z.name}"
            entry = {
                "id": tid,
                "name": info["name"],
                "description": info["description"],
                "author": cfg["author"],
                "kind": kind,
                "downloadUrl": cdn_url(cfg, rel),
                "sha256": sha256_of(z),
                "sizeBytes": z.stat().st_size,
                "minAppVersion": cfg["minAppVersion"],
            }
            png = z.with_suffix(".png")
            if png.is_file():
                entry["previewImageUrl"] = cdn_url(cfg, f"{folder}/{png.name}")
            entries.append(entry)
    return entries


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--owner", help="your GitHub username (saved to repo.config.json)")
    ap.add_argument("--repo", help="repo name (saved)")
    ap.add_argument("--ref", help="branch or tag used in the links, e.g. main or v1.0.0 (saved)")
    ap.add_argument("--check", action="store_true", help="validate only; write nothing")
    args = ap.parse_args(argv)

    cfg = load_config()
    changed = False
    for k in ("owner", "repo", "ref"):
        v = getattr(args, k)
        if v and v != cfg[k]:
            cfg[k] = v
            changed = True

    try:
        entries = collect(cfg)
    except BuildError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    manifest = {"version": MANIFEST_VERSION, "templates": entries}
    if args.check:
        print(f"OK: {len(entries)} template(s) valid. Nothing written.")
        return 0
    if changed or not CONFIG_PATH.is_file():
        save_config(cfg)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote manifest.json with {len(entries)} template(s).")
    if cfg["owner"] == "YOUR_GITHUB_USERNAME":
        print("NOTE: owner is still the placeholder. Run: python build_manifest.py --owner YOUR_NAME")
    return 0


if __name__ == "__main__":
    sys.exit(main())
