# Flask-Vite

[![image](https://img.shields.io/pypi/v/flask-tailwind.svg)](https://pypi.python.org/pypi/flask-tailwind)

Plugin to simplify use of Vite from Flask.

-   Status: Alpha.
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

## Features

- Manages a `vite` directory where you put your front-end source code.
- Auto-injects vite-generated assets into your HTML pages.

## Credits

This project is inspired by the
[Django-Tailwind](https://github.com/timonweb/django-tailwind) project.

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter), using the
[abilian/cookiecutter-abilian-python](https://github.com/abilian/cookiecutter-abilian-python)
project template.
