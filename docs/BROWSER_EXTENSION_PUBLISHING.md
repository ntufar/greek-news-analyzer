# Browser Extension Publishing Guide

This guide covers how to publish the EPAP browser extension to Chrome Web Store, Firefox Add-ons (AMO), and Microsoft Edge Add-ons.

## Build the packages

Run the build script from the `browser-extension/` directory:

```bash
cd browser-extension && bash build.sh
```

This produces:
- `dist/epap-chrome.zip` — for Chrome and Edge (Manifest V3)
- `dist/epap-firefox.zip` — for Firefox (Manifest V2)

---

## Chrome Web Store

1. **Create a developer account** at [chrome.google.com/webstore/devconsole](https://chrome.google.com/webstore/devconsole). There is a one-time $5 registration fee.

2. In the Developer Dashboard click **New Item** → upload `dist/epap-chrome.zip`.

3. Fill in the store listing:
   - Description (Greek + English recommended)
   - Screenshots — at least 1 required, 1280×800 or 640×400 px
   - Category: **News & Weather** or **Productivity**
   - Privacy policy URL (required — see section below)

4. **Justify permissions** — Chrome will ask you to explain `activeTab` and `scripting`. Use:
   > *"activeTab is used to read the current page URL; scripting is used to inject a content script that extracts the article text for analysis."*

5. Click **Submit for review**. Approval typically takes 1–3 business days.

---

## Firefox Add-ons (AMO)

1. **Create a developer account** at [addons.mozilla.org](https://addons.mozilla.org) (free).

2. Go to [addons.mozilla.org/developers/addon/submit](https://addons.mozilla.org/en-US/developers/addon/submit/) and choose **On this site** (listed publicly).

3. Upload `dist/epap-firefox.zip`. AMO validates the manifest automatically.

4. If AMO requests source code, attach a zip of the `browser-extension/` folder (no build step required).

5. Fill in the listing: description, screenshots, category (**News & Politics**).

6. Listed extensions can take a few days to a few weeks for review. You can distribute as **Unlisted** (self-hosted, no review queue) while waiting.

---

## Microsoft Edge Add-ons

Edge uses the **same zip as Chrome** — both are Chromium/MV3.

1. **Create a developer account** at [partner.microsoft.com/dashboard/microsoftedge/overview](https://partner.microsoft.com/en-us/dashboard/microsoftedge/overview) (free).

2. Click **Create new extension** → upload `dist/epap-chrome.zip`.

3. Fill in the listing with the same assets as Chrome (screenshots, description, privacy policy URL).

4. Approval typically takes 1–7 business days.

---

## Required assets checklist

| Asset | Specification |
|---|---|
| Screenshots | At least 2, 1280×800 px recommended |
| Small promo tile | 440×280 px (required by Chrome and Edge) |
| Privacy policy URL | A URL on your site — see below |
| Description (short) | Max 132 characters |
| Description (long) | Recommended in both Greek and English |

---

## Privacy policy

Since the extension sends page text to `epap.vercel.app`, all three stores require a privacy policy URL. Minimum required disclosure:

> *"Article text from the active browser tab is sent to epap.vercel.app for AI-powered analysis. No personal data is collected or stored."*

Host this at a stable URL (e.g. `epap.vercel.app/privacy`) and use that URL in all store listings.

---

## Releasing updates

1. Increment `"version"` in both `manifest.chrome.json` and `manifest.firefox.json`.
2. Run `bash build.sh` to regenerate the zips.
3. Upload the new zip in each store's developer dashboard. Reviews for updates are generally faster than initial submissions.
