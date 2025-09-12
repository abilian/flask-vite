# Flask-Vite Developer Guide

This guide covers the internal architecture, development setup, and contribution guidelines for Flask-Vite.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Development Setup](#development-setup)
- [Code Structure](#code-structure)
- [Extension Implementation](#extension-implementation)
- [Testing](#testing)
- [Contributing](#contributing)
- [Release Process](#release-process)

## Architecture Overview

Flask-Vite follows the Flask extension pattern and integrates with Vite's development and build processes.

### Core Components

```
src/flask_vite/
├── __init__.py          # Public API exports
├── extension.py         # Main Vite extension class
├── cli.py              # Flask CLI commands
├── npm.py              # NPM process wrapper
├── tags.py             # Template tag generation
└── starter/            # Default Vite project template
```

### Request Flow

1. **Development Mode** (`app.debug=True`):
   - `{{ vite_tags() }}` generates `<script>` tags pointing to `localhost:3000`
   - Vite dev server serves assets with hot reload
   - Flask serves the application on a different port

2. **Production Mode** (`app.debug=False`):
   - `{{ vite_tags() }}` generates `<script>` tags pointing to built assets
   - Flask serves built assets via `/_vite/<filename>` route
   - Assets are fingerprinted and cached

## Development Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- npm or pnpm

### Setup Instructions

```bash
# Clone the repository
git clone https://github.com/abilian/flask-vite.git
cd flask-vite

# Install Python dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Run the demo
cd demo
python app.py
```

### Development Workflow

```bash
# Code formatting
uv run ruff format .

# Linting
uv run ruff check . --fix

# Type checking
uv run mypy src tests

# Run all checks
make lint

# Run tests with coverage
make test-with-coverage
```

## Code Structure

### Extension Class (`extension.py`)

The `Vite` class is the main extension:

```python
class Vite:
    def __init__(self, app: Flask | None = None, vite_routes_host: str | None = None):
        """Initialize the extension."""
        
    def init_app(self, app: Flask, vite_routes_host: str | None = None):
        """Configure the extension for the Flask app."""
        
    def after_request(self, response: Response):
        """Auto-inject vite tags if VITE_AUTO_INSERT is enabled."""
        
    def vite_static(self, filename):
        """Serve built Vite assets in production."""
```

### CLI Commands (`cli.py`)

Flask CLI commands are implemented using Click:

```python
@click.group()
def vite():
    """Perform Vite operations."""

@command()
@with_appcontext
def init():
    """Init the vite/ directory (if it doesn't exist)"""
```

### NPM Wrapper (`npm.py`)

Handles subprocess calls to npm:

```python
class NPM:
    def __init__(self, cwd: str, npm_bin_path: str = "npm"):
        self.cwd = cwd
        self.npm_bin_path = npm_bin_path
    
    def run(self, *args):
        """Execute npm command with given arguments."""
```

### Template Tags (`tags.py`)

Generates appropriate HTML tags based on Flask's debug mode:

```python
def make_tag() -> str:
    """Generate script/link tags for Vite assets."""
    if current_app.debug:
        return make_dev_tag()  # Point to Vite dev server
    else:
        return make_prod_tag()  # Point to built assets
```

## Extension Implementation

### Flask Extension Pattern

Flask-Vite follows Flask's extension patterns:

```python
# Registration
app.extensions["vite"] = self

# Configuration
config = app.config
vite_folder_path = config.get("VITE_FOLDER_PATH", "vite")

# Route registration
app.route("/_vite/<path:filename>", endpoint="vite.static")(self.vite_static)

# Template global registration
app.template_global("vite_tags")(make_tag)
```

### Host Matching Support

For applications using `host_matching=True`:

```python
def _validate_and_configure_vite_routes_host(self, app, vite_routes_host):
    """Configure host-specific routing for vite assets."""
    if vite_routes_host == "*":
        # Use wildcard to serve from same host as request
        vite_routes_host = VITE_ROUTES_HOST_WILDCARD_VARIABLE
    
    @app.url_defaults
    def inject_vite_routes_host_if_required(endpoint, values):
        if app.url_map.is_endpoint_expecting(endpoint, "vite_routes_host"):
            values.setdefault("vite_routes_host", request.host)
```

### Auto-injection Feature

When `VITE_AUTO_INSERT=True`:

```python
def after_request(self, response: Response):
    """Automatically inject vite tags into HTML responses."""
    if response.status_code != OK or not response.mimetype.startswith("text/html"):
        return response
    
    body = b"".join(response.response).decode()
    tag = make_tag()
    body = body.replace("</head>", f"{tag}\n</head>")
    response.response = [body.encode("utf8")]
    response.content_length = len(response.response[0])
    return response
```

## Testing

### Test Structure

```
tests/
├── conftest.py          # Pytest configuration and fixtures
├── test_flask_vite.py   # Main extension tests
└── __init__.py
```

### Key Test Areas

1. **Extension Registration**: Test proper Flask extension setup
2. **CLI Commands**: Test all CLI command functionality
3. **Template Tags**: Test tag generation in dev/prod modes
4. **Auto-injection**: Test automatic HTML modification
5. **Host Matching**: Test multi-host configuration
6. **Error Handling**: Test error scenarios and validation

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov flask_vite

# Specific test
uv run pytest tests/test_flask_vite.py::test_extension_registration

# Multiple Python versions
tox
```

### Test Fixtures

Common fixtures in `conftest.py`:

```python
@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def vite_app(app):
    """Flask app with Vite extension."""
    vite = Vite(app)
    return app
```

## Contributing

### Code Style

- Follow PEP 8 and project's ruff configuration
- Use type hints for all function signatures
- Write docstrings for public APIs
- Prefer f-strings for string formatting

### Commit Guidelines

- Use conventional commits: `feat:`, `fix:`, `docs:`, etc.
- Write clear, descriptive commit messages
- Keep commits atomic (one logical change per commit)

### Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feat/my-feature`
3. **Make** changes with appropriate tests
4. **Run** the test suite: `make test`
5. **Run** code quality checks: `make lint`
6. **Submit** a pull request with clear description

### Adding New Features

When adding features:

1. **Design**: Consider the API and how it fits with Flask patterns
2. **Implement**: Write the feature with appropriate error handling
3. **Test**: Add comprehensive tests covering edge cases
4. **Document**: Update user and developer documentation
5. **Demo**: Consider adding an example to the demo app

## Release Process

### Version Management

- Follow semantic versioning (SemVer)
- Update version in `pyproject.toml`
- Update `CHANGELOG.md` with changes

### Release Steps

```bash
# 1. Ensure all tests pass
make test-all

# 2. Update changelog
git-cliff > CHANGELOG.md

# 3. Commit changes
git commit -m "chore: release vX.Y.Z"

# 4. Create tag
git tag vX.Y.Z

# 5. Push changes and tags
git push --tags

# 6. Build and publish
make publish
```

### CI/CD Pipeline

The project uses GitHub Actions for:

- **Testing**: Run tests on multiple Python versions
- **Linting**: Check code quality and formatting
- **Type Checking**: Run mypy for type safety
- **Publishing**: Automatic PyPI publishing on tagged releases

## Debugging and Profiling

### Debug Mode

Enable Flask debug mode to see detailed error messages:

```python
app.debug = True
```

### Logging

Add logging for debugging extension behavior:

```python
import logging
logger = logging.getLogger(__name__)

def init_app(self, app: Flask):
    logger.debug("Initializing Flask-Vite extension")
```

### Common Development Issues

1. **Template Tags Not Working**: Check if extension is properly registered
2. **Assets Not Loading**: Verify Vite dev server is running and reachable
3. **Import Errors**: Ensure proper Python path and dependencies
4. **CLI Commands Failing**: Check Flask application context

## Performance Considerations

### Asset Serving

- Built assets are served with 1-year cache headers
- Assets are fingerprinted for cache busting
- Gzip compression should be handled by the web server

### Memory Usage

- Extension maintains minimal state
- No persistent connections to Vite dev server
- NPM processes are spawned only when needed

### Production Optimizations

- Set `FLASK_ENV=production`
- Use a proper WSGI server (gunicorn, uWSGI)
- Configure web server to serve static assets
- Enable gzip compression for text assets