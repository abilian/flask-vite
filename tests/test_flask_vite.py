#!/usr/bin/env python

"""Tests for `flask_vite` package."""

from click.testing import CliRunner
from flask import Flask

from flask_vite import Vite, cli


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


def test_npm_alt_path():
    app = Flask(__name__)
    app.config["VITE_NPM_BIN_PATH"] = "xxx"
    vite = Vite(app)
    npm = vite.npm
    assert npm.npm_bin_path == "xxx"
