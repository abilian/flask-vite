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
from flask_vite.extension import ViteError
from flask_vite.npm import NPMError
from flask_vite.tags import make_static_tag


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
    app.config["VITE_AUTO_INSERT"] = True
    Vite(app)

    @app.route("/")
    def index():
        return "<html><head></head><body>OK</body></html>"

    mocker.patch("glob.glob", return_value=["path/to/file"])
    with (
        app.test_client() as client,
        app.app_context(),
    ):
        response = client.get("/")

        assert '<script type="module" src="/_vite/file">' in response.text
        assert '<link rel="stylesheet" href="/_vite/file">' in response.text


def test_vite_and_flask_host_mismatch():
    app = Flask(__name__, host_matching=False)
    app.config["VITE_AUTO_INSERT"] = True

    with pytest.raises(ViteError) as e:
        Vite(app, vite_routes_host="vite.domain.com")

    assert (
        str(e.value)
        == "`vite_routes_host` should only be set if your Flask app is using `host_matching`."
    )


def test_vite_conflicting_vite_routes_host_configuration():
    app = Flask(__name__, host_matching=True, static_host="static.domain.com")
    app.config["VITE_AUTO_INSERT"] = True
    vite = Vite(vite_routes_host="vite.domain.com")

    with pytest.raises(ViteError) as e:
        vite.init_app(app, vite_routes_host="*")

    assert str(e.value) == (
        "`vite_routes_host` has been configured differently in two places; use either "
        "`Vite(vite_routes_host=...)` or `Vite().init_app(vite_routes_host=...)`, not both."
    )


def test_vite_host_variables_rejected():
    app = Flask(__name__, host_matching=True, static_host="static.domain.com")
    app.config["VITE_AUTO_INSERT"] = True

    with pytest.raises(ViteError) as e:
        Vite(app, vite_routes_host="<my_host>.com")

    assert str(e.value) == (
        "`vite_routes_host` must either be a host name with no variables, to serve all "
        "vite assets from a single host, or the wildcard value `*` to serve from the same host as the "
        "current request."
    )


def test_vite_auto_inject_explicit_host(mocker):
    app = Flask(__name__, host_matching=True, static_host="static.domain.com")
    app.config["VITE_AUTO_INSERT"] = True
    Vite(app, vite_routes_host="vite.domain.com")

    @app.route("/", host="myapp.com")
    def index():
        return "<html><head></head><body>OK</body></html>"

    mocker.patch("glob.glob", return_value=["path/to/file"])
    with (
        app.test_client() as client,
        app.app_context(),
    ):
        response = client.get("/", headers={"Host": "myapp.com"})

        assert (
            '<script type="module" src="http://vite.domain.com/_vite/file">'
            in response.text
        )
        assert (
            '<link rel="stylesheet" href="http://vite.domain.com/_vite/file">'
            in response.text
        )


def test_vite_auto_inject_match_request_host(mocker):
    app = Flask(__name__, host_matching=True, static_host="static.domain.com")
    app.config["VITE_AUTO_INSERT"] = True
    Vite(app, vite_routes_host="*")

    @app.route("/", host="myapp.com")
    def index():
        return "<html><head></head><body>OK</body></html>"

    mocker.patch("glob.glob", return_value=["path/to/file"])
    with (
        app.test_client() as client,
        app.app_context(),
    ):
        response = client.get("/", headers={"Host": "myapp.com"})
        assert '<script type="module" src="/_vite/file">' in response.text
        assert '<link rel="stylesheet" href="/_vite/file">' in response.text


@pytest.mark.parametrize(
    ("vite_routes_host", "request_host", "expected_status_code"),
    [
        ("vite.domain.com", "vite.domain.com", 200),
        ("vite.domain.com", "myapp.com", 404),
        ("vite.domain.com", "static.domain.com", 404),
        ("*", "vite.domain.com", 200),
        ("*", "myapp.com", 200),
        ("*", "static.domain.com", 200),
    ],
)
def test_vite_serves_assets_from_explicit_host(
    mocker, request_host, expected_status_code, vite_routes_host
):
    app = Flask(__name__, host_matching=True, static_host="static.domain.com")
    app.config["VITE_AUTO_INSERT"] = True
    Vite(app, vite_routes_host=vite_routes_host)

    mocker.patch(
        "flask.helpers.werkzeug.utils.send_from_directory",
        return_value=Response(b"fake-file", mimetype="text/css", status=200),
    )
    with (
        app.test_client() as client,
        app.app_context(),
    ):
        response = client.get("/_vite/some-file", headers={"Host": request_host})
        assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    "vite_folder_path",
    (None, "vite", "app/vite"),
)
def test_vite_builds_static_tags_correctly_with_custom_folder_path(
    mocker, vite_folder_path
):
    app = Flask(__name__)

    if vite_folder_path is not None:
        app.config["VITE_FOLDER_PATH"] = vite_folder_path

    app.config["SERVER_NAME"] = "localhost:5000"
    Vite(app)

    mocker.patch(
        "flask_vite.tags.glob.glob", side_effect=[("index.js",), ("index.css",)]
    )

    with app.app_context():
        static_tags = make_static_tag()
        assert 'src="http://localhost:5000/_vite/index.js"' in static_tags
        assert 'href="http://localhost:5000/_vite/index.css"' in static_tags
