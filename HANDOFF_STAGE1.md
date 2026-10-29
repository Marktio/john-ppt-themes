# HANDOFF: Stage 1 (the template repo)

## What this is
A standalone GitHub repo folder, `john-ppt-themes`, that holds community templates and a script that builds the `manifest.json` menu VOL PPT will read via jsDelivr. It contains no app code.

## Where everything landed
This is a NEW repo, not part of the app folder. Upload the contents of `john-ppt-themes/` to the **root of a new public GitHub repo** named `john-ppt-themes`. Nothing goes inside your app folder in this stage. (Stage 3 will tell you exactly which app files change: `src/communityTemplates.ts`, `src/components/tabs/ThemeTab.tsx`, `src/api/python.ts`, `sidecar/main.py`.)

## Do this after unzipping
1. Make the public GitHub repo `john-ppt-themes` and upload everything to its root.
2. Open a terminal in the folder and run `update-manifest.bat --owner YOUR_GITHUB_USERNAME` once (the .bat passes arguments through). Later updates are just a double-click.
3. Commit and push.
4. Open `https://cdn.jsdelivr.net/gh/YOUR_GITHUB_USERNAME/john-ppt-themes@main/manifest.json` in a browser. You should see the JSON.

## What was verified, not assumed
- 9 unit tests pass (checksums, URLs, kind-from-folder, zip-slip rejection, forbidden `require` rejection, duplicate ids, bad file names, preview picture, repeatable output).
- The sample `soft-lilac.zip` imported through the app's REAL `import_theme_zip` (from your app.zip) and the manifest's sha256 matched the file.
- `.bat` saved with CRLF line endings.

## Still open
- NOT tested: running `update-manifest.bat` on Windows, the winget Python install path, and a real jsDelivr fetch (my sandbox can't reach it). Step 4 above is how you test it.
- Your GitHub username (placeholder `YOUR_GITHUB_USERNAME` until you run step 2).
- Stage 2 fills `looks/standard` and `looks/static`; no looks exist yet, so the looks validator is covered by tests only, not by a real pack.
- jsDelivr caches branch links; pin a tag for releases (see README).
