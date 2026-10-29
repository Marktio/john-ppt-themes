# john-ppt-themes

The community template shelf for VOL PPT. The app reads `manifest.json` from here (through the free jsDelivr CDN) and shows each entry in the Theme room.

## How to add a template

1. Drop the zip in the right folder:
   - `themes/` for a theme (a zip with one `DESIGN.md`)
   - `looks/standard/` for a Standard look (a zip with `manifest.json` + an engine `.js`)
   - `looks/static/` for a Static layout (same shape)
2. Optional: put `<same-name>.png` beside the zip as its preview picture.
3. Double-click `update-manifest.bat`. It checks every zip and rewrites `manifest.json`.
4. Commit and push.

File names: lowercase letters, digits and hyphens only (e.g. `soft-lilac.zip`). The name is the template's id.

## First-time setup (once, one click)

Double-click `publish-themes-repo.bat`. It finds your GitHub username through the `gh` tool, rebuilds `manifest.json`, creates the **public** repo `john-ppt-themes` (or updates it if it exists), pushes, and opens the manifest link. Run it again any time you add templates.

### Or by hand

1. Create a **public** GitHub repo named `john-ppt-themes` and upload everything in this folder to its root.
2. Run `update-manifest.bat --owner Marktio` once. It saves your name into `repo.config.json`.
3. Commit and push. The app's list address is then:
   `https://cdn.jsdelivr.net/gh/Marktio/john-ppt-themes@main/manifest.json`

## Notes

- **Caching.** jsDelivr remembers files for a while. For a quick refresh of a branch link, open `https://purge.jsdelivr.net/gh/Marktio/john-ppt-themes@main/manifest.json`. For steadier releases, tag the repo (e.g. `v1.0.0`) and run `update-manifest.bat --ref v1.0.0`.
- **Looks run code.** A look's `engine.js` is a small program. The builder only accepts looks that use `pptxgenjs`, `fs` and `path`. Themes are plain data.
- **Fingerprints.** Each entry carries a `sha256`. The app (Stage 3) refuses a download whose fingerprint doesn't match.
- Run the tests: `python -m unittest discover -s tests -v`

## Making more looks (maintainers)

The six starter looks are generated, not hand-drawn one by one. Edit `tools/looks_src/looks.json` (names, colors, fonts, which layouts) or `tools/looks_src/engine_template.js` (the shared drawing code), then run `python tools/make_looks.py`. It writes the zips and preview pictures, and refuses to finish if a test deck fails, text leaves the safe margin, or a bullet gets dropped. Needs Node + `npm install pptxgenjs` (set `NODE_PATH` to its `node_modules`); LibreOffice is optional, for the preview pictures.

## Credits

Add any third-party credit lines for templates here.
