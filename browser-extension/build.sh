#!/usr/bin/env bash
# Packages the extension for Chrome/Edge (MV3) and Firefox (MV2)
set -euo pipefail

SHARED_FILES="popup.html popup.js content.js icons"

rm -rf dist
mkdir -p dist/chrome dist/firefox

# Chrome / Edge
cp manifest.chrome.json dist/chrome/manifest.json
for f in $SHARED_FILES; do cp -r "$f" dist/chrome/; done
cd dist/chrome && zip -r ../epap-chrome.zip . -x "*.DS_Store" && cd ../..
echo "✓  dist/epap-chrome.zip  (Chrome & Edge)"

# Firefox
cp manifest.firefox.json dist/firefox/manifest.json
for f in $SHARED_FILES; do cp -r "$f" dist/firefox/; done
cd dist/firefox && zip -r ../epap-firefox.zip . -x "*.DS_Store" && cd ../..
echo "✓  dist/epap-firefox.zip  (Firefox)"

echo ""
echo "Chrome/Edge: load dist/chrome/ as unpacked extension"
echo "Firefox:     submit dist/epap-firefox.zip to addons.mozilla.org"
