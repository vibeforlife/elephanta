# Elephanta Guide

A mobile-first PWA audio walking guide for the Elephanta Caves at Gharapuri.

## Local test

From this folder, run a local static server (for example `python3 -m http.server 8080`) and open `http://localhost:8080/`. Service workers require localhost or HTTPS.

## GitHub Pages

Upload the contents of this folder to the repository root, enable GitHub Pages for the branch/folder containing the site, and open the generated HTTPS Pages URL on Android. Use Edge Read Aloud on each stop page.

## Design

- Separate substantial tour pages with Previous / All Stops / Next navigation.
- Visual sculpture index.
- Photographs are decorative/visual only and carry no narration text.
- PWA manifest + service worker.
- Generated Trimurti-inspired app icon.
- Wikimedia Commons images are credited in `credits.html`.
