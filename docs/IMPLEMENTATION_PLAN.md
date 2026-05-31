# EPAP Mobile — Implementation Plan

## Overview
Native mobile app (Flutter) for the EPAP Greek news propaganda/bias analysis platform. Provides Android (and later iOS) integration via the OS share sheet — users can share a URL from any app (browser, Twitter, Facebook, etc.) and instantly analyze it.

## Tech Stack
- **Framework:** Flutter (Dart)
- **State Management:** Provider
- **Local Storage:** sqflite (history)
- **HTTP Client:** `http` package
- **Markdown Rendering:** `flutter_markdown`
- **Share Handling:** `receive_sharing_intent`

## Architecture
```
main.dart → App (MaterialApp + theme + routes)
              ↓
        Provider<AnalysisProvider>
              ↓
    ┌──────────┼──────────┐
  Home      Result    History
```

**Data flow:**
```
OS Share Intent → ShareHandler → AnalysisProvider.analyze(url)
                                      ↓
                              ApiService.post('/analyze', body)
                                      ↓
                              Response: { analysis: "markdown...", score: 42 }
                                      ↓
                              ScoreExtractor.parse(markdown) → score
                                      ↓
                              Provider updates state → UI renders
```

## Project Structure
```
epap_mobile/
├── android/app/src/main/AndroidManifest.xml     # Intent filters
├── ios/Runner/Info.plist                         # Share extension
├── lib/
│   ├── main.dart                                 # Entry, providers, share init
│   ├── app.dart                                  # MaterialApp, theme, routes
│   ├── providers/analysis_provider.dart          # ChangeNotifier
│   ├── models/analysis_result.dart               # Data model
│   ├── services/
│   │   ├── api_service.dart                      # HTTP to POST /analyze
│   │   ├── share_handler.dart                    # receive_sharing_intent
│   │   └── database_service.dart                 # sqflite history
│   ├── screens/
│   │   ├── home_screen.dart                      # Input + auto-analyze
│   │   ├── result_screen.dart                    # Score + criteria
│   │   ├── history_screen.dart                   # Past analyses list
│   │   └── about_screen.dart                     # App info
│   ├── widgets/
│   │   ├── score_gauge.dart                      # Circular animated gauge
│   │   ├── criteria_card.dart                    # Collapsible criterion
│   │   ├── analysis_header.dart                  # Score summary bar
│   │   └── empty_state.dart                      # No-data placeholder
│   └── utils/
│       ├── constants.dart                        # Colors, API URL, thresholds
│       ├── score_extractor.dart                  # Regex score parser
│       └── theme.dart                            # Light/dark themes
└── test/
    ├── services/
    │   ├── api_service_test.dart
    │   └── score_extractor_test.dart
    └── widgets/
        └── score_gauge_test.dart
```

## Key Dependencies
- `http` — API calls
- `receive_sharing_intent` — OS share sheet integration
- `sqflite` + `path_provider` — local history
- `flutter_markdown` — render analysis markdown
- `provider` — state management
- `url_launcher` — external links
- `share_plus` — share results
- `flutter_launcher_icons` — app icons

## Screens

### HomeScreen
- URL input (default) / text area toggle
- Optional source field
- Auto-detects shared intent on load, auto-submits
- Loading spinner during analysis
- Error display on failure

### ResultScreen
- Animated circular score gauge (1–100 with color coding)
- 7 collapsible criteria cards (parsed from markdown)
- Full markdown analysis view
- Share / copy actions

### HistoryScreen
- Chronological list with score badge + source + date
- Tap to re-view, swipe to delete
- Empty state when no history

### AboutScreen
- Same content as web `/about` page
- EPAP description, features, author, tech stack

## Score Color Coding
| Range | Color | Classification |
|-------|-------|----------------|
| 81–100 | `#28a745` Green | Excellent |
| 61–80 | `#ffc107` Yellow | High |
| 31–60 | `#fd7e14` Orange | Medium |
| 1–30 | `#dc3545` Red | Low |

## Share Integration
- **Android:** `ACTION_SEND` intent filter in AndroidManifest.xml for `text/plain`
- **iOS:** `NSSharingService` in Info.plist (future)
- **Handler:** `receive_sharing_intent` package listens for incoming URLs/text, passes to provider for auto-analysis

## Backend
- Uses existing `POST /analyze` endpoint (no changes needed)
- Base URL: `https://epap.vercel.app` (production) or `http://localhost:5000` (dev)
- Rendering: client-side via `flutter_markdown` (same markdown, different renderer)

## Dark Mode
- Detected via `MediaQuery.platformBrightness`
- Toggle in app (light / dark / system)
- Dark theme with adjusted gradients, card backgrounds, text colors

## Implementation Order
| # | Step | Status |
|---|------|--------|
| 1 | Create plan document | Done |
| 2 | `flutter create`, pubspec deps, folders | Done |
| 3 | Theme, constants, utils | Done |
| 4 | AnalysisResult model + ScoreExtractor | Done |
| 5 | ApiService + DatabaseService + ShareHandler | Done |
| 6 | AnalysisProvider | Done |
| 7 | HomeScreen | Done |
| 8 | ResultScreen (gauge + criteria + markdown) | Done |
| 9 | HistoryScreen | Done |
| 10 | AboutScreen | Done |
| 11 | Wire up main.dart + app.dart | Done |
| 12 | Android manifest + icons + app name config | Done |
| 13 | Tests (19 passing) | Done |
| 14 | Build APK (debug + release) | Done |

## Build Output
- **Debug APK:** `build/app/outputs/flutter-apk/app-debug.apk` (147MB)
- **Release APK:** `build/app/outputs/flutter-apk/app-release.apk` (52.4MB)
- **Tests:** 19/19 passing

## Notes
- Flutter chosen over native for single codebase targeting both platforms
- History is local-only (no cloud sync)
- App icon will use the existing EPAP logo (generate icons via `flutter_launcher_icons`)
