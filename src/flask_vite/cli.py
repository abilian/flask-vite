# Copyright (c) 2022-2024, Abilian SAS
#
# SPDX-License-Identifier: MIT
"""Console script for flask_vite."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import click
from click import secho
from flask import current_app
from flask.cli import with_appcontext


@click.group()
def vite():
    """Perform Vite operations."""


command = vite.command


@command()
@with_appcontext
def init():
    """Init the vite/ directory (if it doesn't exist)"""
    source_dir = Path(__file__).parent / "starter"
    dest_dir = Path("vite")
    if dest_dir.exists():
        secho(f"Target directory '{dest_dir}' exists, aborting.", fg="red")
        sys.exit(1)

    shutil.copytree(source_dir, dest_dir)
    secho(
        f"Vite source directory and starter content installed in '{dest_dir}'.",
        fg="green",
    )


@command()
@with_appcontext
def install():
    """Install the dependencies using npm."""
    npm = current_app.extensions["vite"].npm
    npm.run("install")


@command()
@with_appcontext
def build():
    """Build the Vite assets."""
    npm = current_app.extensions["vite"].npm
    npm.run("run", "build")


@command()
@with_appcontext
def start():
    """Start watching source changes for dev."""
    npm = current_app.extensions["vite"].npm
    npm.run("run", "dev")


@command()
@with_appcontext
def check_updates():
    """Check outdated Vite dependencies."""
    npm = current_app.extensions["vite"].npm
    npm.run("outdated")


@command()
@with_appcontext
def update():
    """Update Vite and its dependencies, if needed."""
    npm = current_app.extensions["vite"].npm
    npm.run("update")
