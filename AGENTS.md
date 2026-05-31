# Project-level instructions for AI agents

## Version bump procedure

Every time you bump the version in `epap_mobile/pubspec.yaml`:

1. Update `CHANGELOG.md` — add a new entry for the new version above the existing entries, following the existing format:
   - `## [X.X.X] - YYYY-MM-DD`
   - Categorize changes under `### Added`, `### Changed`, `### Fixed` as appropriate
2. Increment the build number (the part after `+`) in the version string
3. Commit the changes
4. Create a tag matching the version (e.g., `v0.0.2`)
5. Push commits and tags
