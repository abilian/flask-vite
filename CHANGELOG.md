# Changelog

All notable changes to Flask-Vite will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation in `/docs` directory
- User guide with installation, configuration, and usage examples
- Developer guide with architecture overview and contribution guidelines
- Complete API reference documentation
- Enhanced README with project overview and documentation links

### Changed
- Improved project documentation structure
- Enhanced README with better feature descriptions and visual architecture diagrams

## [0.6.0] - 2024-03-06

### Changed
- Migrated build and dependency management from Poetry to uv
- Updated CI configuration for better reliability
- Improved development workflow with uv integration

### Fixed
- CI pipeline stability issues
- Build process improvements

## [0.5.3] - 2024-07-16

### Fixed
- Fixed vite.static endpoint routing issue
- Improved CI workflow stability

### Changed
- Updated GitHub Actions for CI pipeline
- Enhanced tox integration for multi-version testing

## [0.5.1] - 2024-07-16

### Fixed
- **Windows compatibility**: Fixed path handling issues on Windows systems
- Resolved file path separators for cross-platform support

### Documentation
- Updated contribution guidelines with better formatting
- Enhanced README with clearer setup instructions
- Added comprehensive troubleshooting section

## [0.5.0] - 2024-06-26

### Added
- Official changelog file for tracking project changes
- Structured release notes format

### Changed
- Refactored contribution guidelines for better clarity
- Improved documentation organization

## [0.4.1] - 2024-05-21

### Fixed
- **Security**: Made template tags markup-safe to prevent XSS vulnerabilities
- Proper HTML escaping in generated script and link tags

## [0.4.0] - 2024-05-21

### Changed
- **BREAKING**: `VITE_AUTO_INSERT` now defaults to `False`
- This means you should now explicitly use `{{ vite_tags() }}` in your Jinja2 templates
- To restore previous behavior, set `VITE_AUTO_INSERT = True` in your Flask config

### Why this change?
- Provides developers with explicit control over where Vite assets are injected
- Follows Flask's principle of explicit over implicit behavior
- Prevents unexpected HTML modifications in complex template hierarchies

## [0.3.10] - 2024-05-21

### Changed
- Reverted `VITE_AUTO_INSERT` default to `False` for better developer control

## [0.3.8] - 2024-03-28

### Changed
- Updated dependency versions for better compatibility
- Improved package maintenance

## [0.3.5] - 2023-10-27

### Changed
- **Compatibility**: Relaxed Flask version constraints for broader compatibility
- Supports Flask 2.x and newer versions

### Documentation
- Enhanced release notes and documentation

## [0.3.4] - 2023-10-27

### Changed
- **Python Support**: Dropped support for Python 3.8 (end of life)
- Minimum Python version is now 3.9+

### Documentation
- Significant README improvements by @neeerp and @michaelcho
- Better installation and usage instructions
- Enhanced troubleshooting section

### Contributors
- First contributions by @neeerp and @michaelcho

## [0.3.2] - 2023-09-19

### Added
- **Configuration**: `VITE_NPM_BIN_PATH` option to specify custom npm binary path
- Useful for systems with npm installed in non-standard locations

### Fixed
- Removed debug print statements that were accidentally included

## [0.3.1] - 2023-09-19

### Added
- Configurable npm binary path via `VITE_NPM_BIN_PATH` setting

### Fixed
- Cleaned up codebase by removing unnecessary files

## [0.3.0] - 2023-07-04

### Added
- **Demo Application**: Complete working example using TailwindCSS
- Better starter files for new Vite projects with realistic configuration
- Improved `flask vite init` command with production-ready templates

### Changed
- **BREAKING**: Removed automatic insertion of Vite tags in HTML responses
- Now requires explicit `{{ vite_tags() }}` in templates or `VITE_AUTO_INSERT = True` config
- **Template Function**: Renamed `vite_header_tags()` to `vite_tags()` for simplicity

### Why these breaking changes?
- Gives developers explicit control over asset injection placement
- Prevents conflicts with complex template inheritance patterns
- Aligns with Flask's explicit-over-implicit philosophy

## [0.2.5] - 2023-07-04

### Changed
- Simplified template function name from `vite_header_tags()` to `vite_tags()`

### Fixed
- Improved Vite integration and configuration handling
- Fixed demo application setup
- Updated starter files to use proper Vite configuration

### Removed
- Cleaned up unnecessary demo files

## [0.2.3] - 2023-03-29

### Fixed
- **CORS Issues**: Resolved Cross-Origin Resource Sharing problems in development
- Better handling of requests between Flask app and Vite dev server

## [0.2.1] - 2022-12-22

### Development
- Updated testing infrastructure with pyanalyze improvements
- Enhanced code quality checks

## [0.1.4] - 2022-07-19

### Added
- **Performance**: Static asset caching with proper HTTP headers
- Assets served with `Cache-Control` headers for better performance

### Fixed
- Proper HTML tag generation for production builds
- Improved asset serving reliability

## [0.1.3] - 2022-04-28

### Added
- Asset caching for improved performance
- Proper HTTP cache headers for static files

## [0.1.1] - 2022-04-14

### Added
- Proper HTML tag insertion for Vite assets
- Basic template integration functionality

## [0.1.0] - 2022-04-08

### Added
- Initial release on PyPI
- Basic Flask extension for Vite integration
- CLI commands for Vite operations (`flask vite init`, `flask vite build`, etc.)
- Template tag support for asset injection
- Development and production mode support

### Features
- Integration with Vite dev server for hot reloading
- Automatic asset serving in production mode
- Flask CLI integration
- Support for modern frontend frameworks (React, Vue, Svelte)

---

## Migration Guide

### Upgrading from 0.3.x to 0.4.x

The main breaking change is the default value of `VITE_AUTO_INSERT`:

**Before (0.3.x):**
```python
# Assets were automatically injected
app = Flask(__name__)
vite = Vite(app)
# No template changes needed
```

**After (0.4.x):**
```python
# Option 1: Use explicit template tags (recommended)
app = Flask(__name__)
vite = Vite(app)
```
```html
<!-- In your templates -->
<head>
    {{ vite_tags() }}
</head>
```

```python
# Option 2: Restore auto-injection behavior
app = Flask(__name__)
app.config['VITE_AUTO_INSERT'] = True
vite = Vite(app)
```

### Upgrading from 0.2.x to 0.3.x

Template function was renamed:

**Before:** `{{ vite_header_tags() }}`  
**After:** `{{ vite_tags() }}`