# ARCHITECTURE: john-ppt-themes (Stages 1-2)

**Shape chosen:** folder tree + one JSON manifest. Folders because you browse templates and the folder decides the kind; JSON because the app needs one small file to read. Best alternative: a single JSON with zips base64-embedded (one file, but unreadable in GitHub and huge diffs).

```
john-ppt-themes/
├── manifest.json            ← GENERATED menu the app reads (never hand-edit)
├── repo.config.json         ← owner / repo / ref / author (names live here once)
├── build_manifest.py        ← scans zips, validates, fingerprints, writes manifest.json
├── update-manifest.bat      ← one-click wrapper (CRLF, installs Python via winget if missing)
├── themes/                  ← kind "theme"   (DESIGN.md zips; data only)
│   └── soft-lilac.zip       ← sample, real, imports through the app's importer
├── looks/standard/          ← kind "standard": slate-pro, paper-notes, mint-classroom (.zip + .png preview)
├── looks/static/            ← kind "static":   midnight-gold, sunrise-pop, ink-and-rose (.zip + .png)
├── tools/make_looks.py      ← Stage 2: builds + tests + zips the looks from looks_src/
├── tools/looks_src/looks.json, engine_template.js  ← the ONE place look names/colors/layouts are defined
├── tests/test_build_manifest.py
├── README.md
├── ARCHITECTURE_THEMES_REPO.md / HANDOFF_STAGE1.md / PROOF_OF_WORK.md
```

**Spine:** you drop a zip into a kind-folder, `update-manifest.bat` validates it (safe paths, one DESIGN.md or manifest.json, looks may only `require` pptxgenjs/fs/path, size cap, unique id), fingerprints it (sha256) and rewrites `manifest.json`. GitHub holds the files; jsDelivr serves them at `cdn.jsdelivr.net/gh/<owner>/<repo>@<ref>/<path>`. The app (Stage 3) fetches `manifest.json`, shows entries, downloads a zip, checks the sha256, then hands it to the existing `import_theme_zip` (themes) or the looks importer (looks).

**Looks:** every look is the same engine contract the app already expects (`LAYOUTS, resolveTheme, buildDeck`, 10 x 5.625 in, pptxgenjs/fs/path only). Standard and Static packs are identical in format; the folder only decides which gallery they land in. Each look has 6 layouts and 2 color themes. Slides with more bullets than a layout has room for hand over to the two-column layout instead of dropping text.

**Manifest v2 entry:** `id, name, description, author, kind, downloadUrl, sha256, sizeBytes, minAppVersion, previewImageUrl?`. v1 (current app) entries lacked `kind`, `sha256`, `sizeBytes`, `minAppVersion`; the Stage 3 app code treats a missing `kind` as "theme".

**Dead / not used:** nothing retired. R2 is not used (jsDelivr chosen); `r2.config.json` in the app is untouched.
