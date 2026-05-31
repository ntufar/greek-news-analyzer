# Changelog

All notable changes to this project will be documented in this file.

## [0.0.6] - 2026-06-01

### Fixed
- Added missing `ACCESS_NETWORK_STATE` permission and ensured `INTERNET` permission is properly included in release AAB

## [0.0.5] - 2026-06-01

### Changed
- Replaced server-side Python markdown rendering with client-side `marked.js` (v12.0.0) in web templates
- Replaced `flutter_html` with `flutter_markdown` for native markdown rendering in Flutter mobile app

## [0.0.4] - 2026-05-31

### Added
- Greek privacy policy page at /privacy (required for Google Play Store)

### Changed
- Migrated `track` → `tracks` in Play upload action (fix deprecation warning)

## [0.0.3] - 2026-05-31

### Fixed
- Corrected Google Play upload action input names (snake_case → camelCase)
- Granted GitHub release write permissions in workflow (fix 403 error)

## [0.0.2] - 2026-05-31

### Added
- Automated Google Play publishing on version tags
- Custom app launcher icons (custom icon replacing Flutter default)

### Changed
- CI builds AAB (Android App Bundle) for Play Store in addition to APK
- Improved adaptive icon configuration for Android

## [0.0.1] - 2026-05-31

### Added
- Initial release of ΕΠΑΠ (Ελληνική Πλατφόρμα Ανάλυσης Παραπληροφόρησης)
- Greek news propaganda/bias analysis using Mistral AI API
- Mobile app built with Flutter for Android and iOS
- Web backend with Flask deployed on Vercel
- PWA support with offline capabilities
- Google AdSense integration
- SEO meta tags, sitemap, and robots.txt
- Docker containerization and Heroku deployment support
- AWS EC2 deployment scripts
- Comprehensive CI/CD with testing, security scanning, and builds
- Rate limiting and security hardening
