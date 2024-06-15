# Copyright (c) 2022-2024, Abilian SAS
#
# SPDX-License-Identifier: MIT

"""Tests for `flask_vite` package."""
from pathlib import Path

import pytest
from click.testing import CliRunner
from flask import Flask
from werkzeug import Response

from flask_vite import Vite, cli
from flask_vite.npm import NPMError


def test_extension():
    app = Flask(__name__)
    vite = Vite(app)
    assert "vite" in app.extensions
    assert app.extensions["vite"] == vite


def test_cli():
    runner = CliRunner()

    result = runner.invoke(cli.vite)
    assert result.exit_code == 0
    assert "Perform Vite operations" in result.output

    help_result = runner.invoke(cli.vite, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output
    assert "init" in help_result.output


def test_npm():
    app = Flask(__name__)
    vite = Vite(app)
    npm = vite.npm
    assert npm.npm_bin_path == "npm"

    Path("vite").mkdir(exist_ok=True)

    with app.app_context():
        npm.run("help")


def test_npm_alt_path():
    app = Flask(__name__)
    app.config["VITE_NPM_BIN_PATH"] = "xxx"
    vite = Vite(app)
    npm = vite.npm
    assert npm.npm_bin_path == "xxx"

    Path("vite").mkdir(exist_ok=True)

    with app.app_context():
        with pytest.raises(NPMError):
            npm.run()


def test_vite_auto_inject(mocker):
    app = Flask(__name__)
    app.config['VITE_AUTO_INSERT'] = True
    Vite(app)

    @app.route('/')
    def index():
        return '<html><head></head><body>OK</body></html>'

    with app.test_client() as client, app.app_context(), mocker.patch('glob.glob', return_value=['path/to/file']):
        response = client.get('/')

        assert response.text == (
            '<html><head><!-- FLASK_VITE_HEADER -->\n'
            '<script type="module" src="/_vite/file"></script>\n'
             '<link rel="stylesheet" href="/_vite/file"></link>\n'
             '</head><body>OK</body></html>'
        )


def test_vite_and_flask_host_mismatch():
    app = Flask(__name__, host_matching=False)
    app.config['VITE_AUTO_INSERT'] = True

    with pytest.raises(ValueError) as e:
        Vite(app, vite_asset_host='vite.domain.com')

    assert str(e.value) == "`vite_asset_host` should only be set if your Flask app is using `host_matching`."


def test_vite_conflicting_vite_asset_host_configuration():
    app = Flask(__name__, host_matching=True, static_host='static.domain.com')
    app.config['VITE_AUTO_INSERT'] = True
    vite = Vite(vite_asset_host='vite.domain.com')

    with pytest.raises(ValueError) as e:
        vite.init_app(app, vite_asset_host='*')

    assert str(e.value) == (
        "`vite_asset_host` has been configured differently in two places; use either "
        "`Vite(vite_asset_host=...)` or `Vite().init_app(vite_asset_host=...)`, not both."
    )


def test_vite_host_variables_rejected():
    app = Flask(__name__, host_matching=True, static_host='static.domain.com')
    app.config['VITE_AUTO_INSERT'] = True

    with pytest.raises(ValueError) as e:
        Vite(app, vite_asset_host='<my_host>.com')

    assert str(e.value) == (
        "`vite_asset_host` must either be a host name with no variables, to serve all "
        "vite assets from a single host, or the wildcard value `*` to serve from the same host as the "
        "current request."
    )


def test_vite_auto_inject_explicit_host(mocker):
    app = Flask(__name__, host_matching=True, static_host='static.domain.com')
    app.config['VITE_AUTO_INSERT'] = True
    Vite(app, vite_asset_host='vite.domain.com')

    @app.route('/', host="myapp.com")
    def index():
        return '<html><head></head><body>OK</body></html>'

    with app.test_client() as client, app.app_context(), mocker.patch('glob.glob', return_value=['path/to/file']):
        response = client.get('/', headers={"Host": "myapp.com"})

        assert response.text == (
            '<html><head><!-- FLASK_VITE_HEADER -->\n'
            '<script type="module" src="http://vite.domain.com/_vite/file"></script>\n'
             '<link rel="stylesheet" href="http://vite.domain.com/_vite/file"></link>\n'
             '</head><body>OK</body></html>'
        )


def test_vite_auto_inject_match_request_host(mocker):
    app = Flask(__name__, host_matching=True, static_host='static.domain.com')
    app.config['VITE_AUTO_INSERT'] = True
    Vite(app, vite_asset_host='*')

    @app.route('/', host="myapp.com")
    def index():
        return '<html><head></head><body>OK</body></html>'

    with app.test_client() as client, app.app_context(), mocker.patch('glob.glob', return_value=['path/to/file']):
        response = client.get('/', headers={"Host": "myapp.com"})

        assert response.text == (
            '<html><head><!-- FLASK_VITE_HEADER -->\n'
            '<script type="module" src="/_vite/file"></script>\n'
             '<link rel="stylesheet" href="/_vite/file"></link>\n'
             '</head><body>OK</body></html>'
        )


@pytest.mark.parametrize("vite_asset_host, request_host, expected_status_code", (
    ("vite.domain.com", "vite.domain.com", 200),
    ("vite.domain.com", "myapp.com", 404),
    ("vite.domain.com", "static.domain.com", 404),
    ("*", "vite.domain.com", 200),
    ("*", "myapp.com", 200),
    ("*", "static.domain.com", 200)
))
def test_vite_serves_assets_from_explicit_host(mocker, request_host, expected_status_code, vite_asset_host):
    app = Flask(__name__, host_matching=True, static_host='static.domain.com')
    app.config['VITE_AUTO_INSERT'] = True
    Vite(app, vite_asset_host=vite_asset_host)

    with (
        app.test_client() as client,
        app.app_context(),
        mocker.patch(
            'flask.helpers.werkzeug.utils.send_from_directory',
            return_value=Response(b'fake-file', mimetype='text/css', status=200)
        ),
    ):
        response = client.get('/_vite/some-file', headers={"Host": request_host})

        assert response.status_code == expected_status_code
