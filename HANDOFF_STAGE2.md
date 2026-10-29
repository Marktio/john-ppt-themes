# HANDOFF: Stage 2 (the starter looks)

## What this is
Six ready-to-use looks (3 Standard, 3 Static), each with 6 layouts and 2 color themes, plus the tool that generates and tests them. They join Stage 1's repo; `manifest.json` now lists 7 templates (these 6 + the Soft Lilac theme).

## Where everything landed
Replace your `john-ppt-themes` repo contents with this zip (it includes Stage 1). New or changed files:
- `looks/standard/` slate-pro, paper-notes, mint-classroom (each `.zip` + `.png` preview)
- `looks/static/` midnight-gold, sunrise-pop, ink-and-rose (each `.zip` + `.png`)
- `tools/make_looks.py`, `tools/looks_src/looks.json`, `tools/looks_src/engine_template.js`
- `manifest.json` (regenerated), `README.md`, `ARCHITECTURE_THEMES_REPO.md`
Nothing in your app folder changes in this stage.

## Do this after unzipping
1. Copy the contents over your local repo folder, run `update-manifest.bat --owner YOUR_GITHUB_USERNAME` (once), commit, push.
2. To eyeball a look before Stage 3: in the app, Settings > General > "Standard PPT looks" or "Static layouts" > Upload zip > pick one of the new zips.
3. To ship these inside the installer (the "starters" plan), Stage 3 copies the six zips into the app's bundled resources.

## What was verified, not assumed
- Each look generated real .pptx decks with pptxgenjs 4.0.1: mix mode, layout 1, layout 6, both themes, a bogus theme id (falls back, no crash).
- Test decks include a no-photo slide, a 60+ character title and a 9-bullet slide. Automated checks (python-pptx): no text box outside the 0.3 in safe margin; no bullet dropped.
- A full-deck contact sheet of all six looks was rendered with LibreOffice and looked at by eye (Calibri/Georgia/Palatino/Arial may be substituted on this Linux box, so spacing can differ slightly on Windows).
- All six zips imported through your app's REAL `import_style_pack_zip` and the manifest sha256 matched each file.

## Still open
- NOT tested: inside the running app, on Windows with real PowerPoint, or with real photos (stand-in gradient images used).
- Fonts: Georgia, Palatino Linotype, Calibri and Arial exist on standard Windows/Office installs; not on Mac without Office for some.
- Dynamic decks have no looks to ship (the Theme room already says so).
- "Looks" here use 6 shared layout shapes in different colors, fonts and decoration. They are good starters, not six unique art-directed designs. Stage 2b could add more archetypes if you want more variety.
- Stage 3 (app code) is next: manifest `kind`, installing looks as well as themes, checksum check, bundled starters, the multi-repo source list.
