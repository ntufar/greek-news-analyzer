# ΕΠΑΠ Mobile 🇬🇷

Mobile app for the Ελληνική Πλατφόρμα Ανάλυσης Παραπληροφόρησης (EPAP) — an AI-powered Greek news propaganda analysis platform.

[![Flutter](https://img.shields.io/badge/Flutter-3.44+-02569B.svg?logo=flutter)](https://flutter.dev)
[![Android](https://img.shields.io/badge/Android-34DDDDDD.svg?logo=android)](https://play.google.com/store/apps/details?id=io.github.ntufar.epap)
[![iOS](https://img.shields.io/badge/iOS-17-000000.svg?logo=apple)](https://developer.apple.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../LICENSE)

## Features

- 📱 **Native mobile experience** — Android & iOS with Material Design
- 🔍 **Analyze by URL** — paste a news article URL; the server fetches content automatically
- ✏️ **Analyze by text** — paste article text directly
- 📊 **Detailed scoring** — 1-100 reliability rating with visual gauges
- 🧠 **AI-powered analysis** — detects propaganda, emotional manipulation, bias, logical fallacies
- 📋 **Analysis history** — stored locally via SQLite
- 📤 **Share** — share results with others
- 📩 **Receive share intent** — analyze shared news links from other apps
- 🌙 **Dark mode** — automatic theme support
- 🏛️ **Source attribution** — tag analyses with news source (ΕΡΤ, ΣΚΑΪ, ANT1, etc.)

## Screenshots

| Home | Analysis | Result |
|------|----------|--------|
| Input URL or text | Processing indicator | Score & detailed breakdown |

## Build

### Prerequisites

- Flutter SDK 3.12+
- Android SDK (for Android builds)
- Xcode (for iOS builds)

### Setup

```bash
cd epap_mobile
flutter pub get
```

### Run (debug)

```bash
flutter run
```

### Build for Android (release)

Requires JDK 17 and the release keystore.

```bash
export JAVA_HOME=/path/to/jdk-17
export ANDROID_HOME=$HOME/Library/Android/sdk
flutter build appbundle
```

Output: `build/app/outputs/bundle/release/app-release.aab`

### Build for iOS (release)

```bash
flutter build ipa
```

## Architecture

```
lib/
├── app.dart                  # App entry & theme
├── main.dart                 # Main entry point
├── models/
│   └── analysis_result.dart  # Data model
├── providers/
│   └── analysis_provider.dart# State management
├── screens/
│   ├── home_screen.dart      # Input form
│   ├── result_screen.dart    # Analysis results
│   ├── history_screen.dart   # Past analyses
│   └── about_screen.dart     # App info
├── services/
│   ├── api_service.dart      # HTTP client
│   └── database_service.dart # SQLite storage
├── utils/
│   ├── constants.dart        # App constants
│   └── score_extractor.dart  # Score parsing
└── widgets/
    ├── analysis_header.dart  # Result header
    ├── criteria_card.dart    # Criteria display
    └── score_gauge.dart      # Score visualization
```

## Tech Stack

- **Framework:** Flutter 3.44+
- **State management:** Provider
- **Local DB:** SQLite (sqflite)
- **HTTP:** `http` package
- **Markdown rendering:** flutter_markdown
- **Sharing:** share_plus, receive_sharing_intent
- **Linking:** url_launcher

## Related

- **Web backend:** [`../app.py`](../app.py) — Flask server with Gemini AI
- **Serverless API:** [`../api/`](../api/) — Vercel serverless functions
- **Live demo:** [https://epap.vercel.app/](https://epap.vercel.app/)
