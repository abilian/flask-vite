# Flask-Vite

[![image](https://img.shields.io/pypi/v/flask-tailwind.svg)](https://pypi.python.org/pypi/flask-tailwind)

Plugin to simplify use of Vite from Flask.

-   Status: Bêta.
-   Free software: MIT license


## Usage

Instantiate the Flask extension as you do for other Flask extensions:

```python
from flask_vite import Vite

app = Flask(...)
vite = Vite(app)

# or
vite = Vite()
vite.init_app(app)
```

Then you can use the following commands:

```text
$ flask vite
Usage: flask vite [OPTIONS] COMMAND [ARGS]...

Perform Vite operations.

Options:
--help  Show this message and exit.

Commands:
build          Build the Vite assets.
check-updates  Check outdated Vite dependencies.
init           Init the vite/ directory (if it doesn't exist)
install        Install the dependencies using npm.
start          Start watching source changes for dev.
update         Update Vite and its dependencies, if needed.
```

## Example Workflow
This section assumes you have already added Flask-Vite to your Flask app with the steps above.

### Step 1: Initialize your /vite subdirectory
```text
# First, create the /vite subdirectory in your Flask app's root folder
$ flask vite init

# Install any dependencies
$ flask vite install
```

### Step 2: Now you are ready to begin development
```text
# Start a local Vite dev server.
# This will hot-reload any changes in the /vite subdirectory, so it's suited for local development.
$ flask vite start

# Make any changes in vite/main.js, such as importing React/Vue components.
# Flask-Vite assumes you have a single entry point at vite/main.js, such as a React SPA (single page application).
```

**You should now be able to see any changes you have made in your Flask app. If not, try [Troubleshooting](#troubleshooting).**

### Step 3: Ready for production
Once you are ready for production, you need to build your assets.
```text
# Build assets based on /vite/vite.config.js
$ flask vite build
```

You should now see files like `/vite/dist/assets/index-f16ca036.js`.

**If you are running your Flask app in production mode (ie _without_ app.debug), you should see these asset files included in your Flask Jinja templates automatically. If not, try [Troubleshooting](#troubleshooting).**

## Features

- Manages a `vite` directory where you put your front-end source code.
- Auto-injects vite-generated assets into your HTML pages (if `VITE_AUTO_INSERT` is set in the Flask config).
- Use `{{ vite_tags() }}` in your Jinja templates otherwise.


## Configuration

The following (Flask) configuration variables are available:

- `VITE_AUTO_INSERT`: if set, the extension will auto-insert the Vite assets into your HTML pages.
- `NPM_BIN_PATH`: path to the `npm` binary. Defaults to `npm`.


## Demo

See the `demo/` directory for a working demo using TailwindCSS.

## Troubleshooting

### I can't see my vite output files (eg React/Vue components) in my Jinja templates
- Flask-Vite will automatically add these files to your templates if you either:
  - set `VITE_AUTO_INSERT=True` in your Flask config
  - OR, explicitly include `{{ vite_tags() }}` somewhere in your Jinja templates

Either of these options will insert &lt;script&gt; tags into your Jinja templates, which will be the output of your vite config.

### Script tags are included in my Jinja templates, but they're not loading
- If your Flask app is running in debug mode (ie app.debug):
  - your HTML should have a line like `<script type="module" src="http://localhost:3000/main.js"></script>`
  - If this file isn't loading it's because your local Vite dev server isn't running. Start it by using `flask vite start`
- If your Flask app is running in production mode (ie _not_ app.debug):
  - your HTML should have a line like `<script type="module" src="/_vite/index-f16ca036.js"></script>` (the hash in `index-[hash].js` will change every time)
  - you should find this file in `/vite/dist/assets/index-f16ca036.js`. If not, you can build for production again using `flask vite build`


## Credits

This project is inspired by the
[Django-Tailwind](https://github.com/timonweb/django-tailwind) project.

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter), using the
[abilian/cookiecutter-abilian-python](https://github.com/abilian/cookiecutter-abilian-python)
project template.
