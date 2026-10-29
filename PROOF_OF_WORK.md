# PROOF_OF_WORK (Stages 1-2)

Real run, in the Linux sandbox, Python 3, stdlib only. Fake input in, real output out.

**1. Unit tests:** `python -m unittest discover -s tests -v` -> `Ran 9 tests ... OK`

**2. Validate only:** `python build_manifest.py --check` -> `OK: 1 template(s) valid. Nothing written.`

**3. Build:** `python build_manifest.py --owner YOUR_GITHUB_USERNAME` -> `Wrote manifest.json with 1 template(s).` Output is the committed `manifest.json` (soft-lilac, sha256 `14630df3...ca33`, 579 bytes).

**4. App's real importer:** loaded `sidecar/core/theme_import.py` from the uploaded app.zip, pointed its output at a temp folder, checked the sha256 from the manifest against the zip, then ran `import_theme_zip`:

`IMPORTED via app's real import_theme_zip: soft-lilac | Soft Lilac | 9333EA Helvetica`

**Not run:** Windows `.bat`, winget install, live jsDelivr fetch (sandbox network allowlist).

## Stage 2 run

`python tools/make_looks.py` (Node 22, pptxgenjs 4.0.1, python-pptx, LibreOffice). For each of the 6 looks it printed `ok` for: mix mode, layout 1, layout 6, each of the 2 themes, unknown-theme fallback, thumbnail rendered, zip written. Margin and dropped-text checks passed on every deck (the dropped-text check first caught a real gap, "Title left" cutting bullets when forced onto every slide; fixed by handing over to two columns).

`python build_manifest.py --check` -> `OK: 7 template(s) valid.`

App's real `import_style_pack_zip` on all 6 looks:
```
mint-classroom | Mint Classroom | layouts: 6 | themes: ['mint', 'chalk']
paper-notes | Paper Notes | layouts: 6 | themes: ['paper', 'ink']
slate-pro | Slate Pro | layouts: 6 | themes: ['slate-dark', 'slate-light']
ink-and-rose | Ink and Rose | layouts: 6 | themes: ['ink', 'blush']
midnight-gold | Midnight Gold | layouts: 6 | themes: ['midnight', 'ivory']
sunrise-pop | Sunrise Pop | layouts: 6 | themes: ['sunrise', 'dusk']
```
Not run: the live app, Windows PowerPoint, real photos, live jsDelivr.
