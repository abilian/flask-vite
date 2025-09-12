# Flask-Vite API Reference

Complete API documentation for Flask-Vite.

## Table of Contents

- [Vite Extension](#vite-extension)
- [Configuration](#configuration)
- [Template Functions](#template-functions)
- [CLI Commands](#cli-commands)
- [Utility Classes](#utility-classes)
- [Exceptions](#exceptions)

## Vite Extension

### `flask_vite.Vite`

The main Flask extension class.

```python
class Vite:
    def __init__(
        self, 
        app: Flask | None = None, 
        vite_routes_host: str | None = None
    ) -> None
```

**Parameters:**
- `app` (Flask, optional): Flask application instance
- `vite_routes_host` (str, optional): Host for serving Vite assets when using host matching

**Example:**
```python
from flask import Flask
from flask_vite import Vite

app = Flask(__name__)
vite = Vite(app)

# Or using factory pattern
vite = Vite()
vite.init_app(app)
```

#### Methods

##### `init_app(app, vite_routes_host=None)`

Initialize the extension with a Flask application.

```python
def init_app(
    self, 
    app: Flask, 
    vite_routes_host: str | None = None
) -> None
```

**Parameters:**
- `app` (Flask): Flask application instance
- `vite_routes_host` (str, optional): Host for serving Vite assets

**Raises:**
- `ViteError`: If extension is already registered or configuration is invalid

**Example:**
```python
app = Flask(__name__)
vite = Vite()
vite.init_app(app, vite_routes_host='cdn.example.com')
```

##### `vite_static(filename, vite_routes_host=None)`

Serve built Vite assets in production mode.

```python
def vite_static(
    self, 
    filename: str, 
    vite_routes_host: str | None = None
) -> Response
```

**Parameters:**
- `filename` (str): Asset filename to serve
- `vite_routes_host` (str, optional): Host parameter for host matching

**Returns:**
- `Response`: Flask response object with the static file

**Note:** This method is automatically registered as a Flask route handler for `/_vite/<path:filename>`.

##### `after_request(response)`

Auto-inject Vite tags into HTML responses when `VITE_AUTO_INSERT` is enabled.

```python
def after_request(self, response: Response) -> Response
```

**Parameters:**
- `response` (Response): Flask response object

**Returns:**
- `Response`: Modified response with injected Vite tags

**Note:** This method is automatically registered when `VITE_AUTO_INSERT=True`.

#### Properties

##### `vite_folder_path`

Path to the Vite project directory.

```python
@property
def vite_folder_path(self) -> str
```

**Returns:**
- `str`: Path to Vite folder (default: "vite")

##### `npm`

NPM wrapper instance for running npm commands.

```python
@property
def npm(self) -> NPM | None
```

**Returns:**
- `NPM | None`: NPM wrapper instance

## Configuration

Flask-Vite uses Flask's configuration system. Set these variables in your Flask config:

### `VITE_AUTO_INSERT`

**Type:** `bool`
**Default:** `False`

Automatically inject Vite asset tags into HTML responses.

```python
app.config['VITE_AUTO_INSERT'] = True
```

When enabled, Flask-Vite automatically injects `{{ vite_tags() }}` into HTML responses before the closing `</head>` tag.

### `VITE_FOLDER_PATH`

**Type:** `str`
**Default:** `"vite"`

Path to the Vite project directory relative to the Flask app root.

```python
app.config['VITE_FOLDER_PATH'] = 'frontend'
```

### `VITE_NPM_BIN_PATH`

**Type:** `str`
**Default:** `"npm"`

Path to the npm binary executable.

```python
app.config['VITE_NPM_BIN_PATH'] = '/usr/local/bin/npm'
```

## Template Functions

### `vite_tags(static=False)`

Generate HTML tags for including Vite assets.

```python
def vite_tags(*, static: bool = False) -> Markup
```

**Parameters:**
- `static` (bool, optional): Force production mode tags regardless of Flask debug mode

**Returns:**
- `Markup`: Safe HTML markup containing script and link tags

**Template Usage:**
```html
<!-- In development (Flask debug mode) -->
{{ vite_tags() }}
<!-- Outputs: -->
<!-- <script type="module" src="http://localhost:3000/@vite/client"></script> -->
<!-- <script type="module" src="http://localhost:3000/main.js"></script> -->

<!-- In production (Flask production mode) -->
{{ vite_tags() }}
<!-- Outputs: -->
<!-- <script type="module" src="/_vite/index-abc123.js"></script> -->
<!-- <link rel="stylesheet" href="/_vite/index-abc123.css"></link> -->
```

## CLI Commands

All CLI commands are available under the `flask vite` command group.

### `flask vite init`

Initialize a new Vite project directory.

```bash
flask vite init
```

**Description:** Creates a new Vite project in the configured directory with starter files including `package.json`, `vite.config.js`, and `main.js`.

**Behavior:**
- Copies starter files from the extension's template
- Fails if target directory already exists
- Uses `VITE_FOLDER_PATH` configuration

### `flask vite install`

Install npm dependencies.

```bash
flask vite install
```

**Description:** Runs `npm install` in the Vite project directory.

**Equivalent to:** `npm install`

### `flask vite start`

Start Vite development server.

```bash
flask vite start
```

**Description:** Starts Vite in development mode with hot reloading.

**Equivalent to:** `npm run dev`

### `flask vite build`

Build assets for production.

```bash
flask vite build
```

**Description:** Builds optimized assets for production deployment.

**Equivalent to:** `npm run build`

### `flask vite check-updates`

Check for outdated dependencies.

```bash
flask vite check-updates
```

**Description:** Lists outdated npm packages.

**Equivalent to:** `npm outdated`

### `flask vite update`

Update dependencies.

```bash
flask vite update
```

**Description:** Updates npm dependencies to their latest versions.

**Equivalent to:** `npm update`

## Utility Classes

### `flask_vite.npm.NPM`

Wrapper class for executing npm commands.

```python
@dataclass
class NPM:
    cwd: str = ""
    npm_bin_path: str = "npm"
```

**Parameters:**
- `cwd` (str): Working directory for npm commands
- `npm_bin_path` (str): Path to npm executable

#### Methods

##### `run(*args)`

Execute npm command with given arguments.

```python
def run(self, *args: str) -> None
```

**Parameters:**
- `*args` (str): Command arguments to pass to npm

**Raises:**
- `NPMError`: If npm command fails or npm is not found

**Example:**
```python
npm = NPM(cwd="/path/to/vite", npm_bin_path="npm")
npm.run("install")  # Equivalent to: npm install
npm.run("run", "build")  # Equivalent to: npm run build
```

## Exceptions

### `flask_vite.extension.ViteError`

Base exception for Flask-Vite errors.

```python
class ViteError(ValueError):
    pass
```

**Raised when:**
- Extension is already registered on a Flask app
- Invalid configuration is provided
- Host matching configuration errors

### `flask_vite.npm.NPMError`

Exception for npm-related errors.

```python
class NPMError(Exception):
    pass
```

**Raised when:**
- npm binary is not found
- npm command execution fails
- Working directory is invalid

## Advanced Usage

### Host Matching Configuration

For Flask applications using `host_matching=True`:

```python
app = Flask(__name__)
app.url_map.host_matching = True

# Serve assets from specific host
vite = Vite(app, vite_routes_host='static.example.com')

# Or serve from same host as request (wildcard)
vite = Vite(app, vite_routes_host='*')
```

### Custom Asset Serving

Override the default asset serving behavior:

```python
from flask_vite import Vite

class CustomVite(Vite):
    def vite_static(self, filename, vite_routes_host=None):
        # Custom asset serving logic
        return custom_serve_file(filename)

vite = CustomVite(app)
```

### Integration with Flask Blueprints

Flask-Vite works seamlessly with Flask blueprints:

```python
from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')  # Uses {{ vite_tags() }}
```

### Multiple Vite Instances

While not common, you can register multiple Vite instances with different configurations:

```python
# Not recommended - Flask-Vite is designed as a singleton extension
# Each instance would overwrite the previous one in app.extensions['vite']
```

## Type Hints

Flask-Vite is fully typed. Import types for enhanced IDE support:

```python
from flask_vite import Vite
from flask_vite.npm import NPM, NPMError
from flask_vite.extension import ViteError

# All classes and functions include proper type annotations
```