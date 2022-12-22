"""Console script for flask_vite."""

import shutil
import sys
from pathlib import Path

import click
import rich
from flask.cli import with_appcontext

from .npm import NPM


@click.group()
def vite():
    """Perform Vite operations."""
    pass


command = vite.command


@command()
@with_appcontext
def init():
    """Init the vite/ directory (if it doesn't exist)"""
    source_dir = Path(__file__).parent / "starter"
    dest_dir = Path("vite")
    if dest_dir.exists():
        rich.print(f"[red]Target directory '{dest_dir}' exists, aborting.[/red]")
        sys.exit(1)

    shutil.copytree(source_dir, dest_dir)
    rich.print(
        f"[green]Vite source directory and starter content installed in "
        f"'{dest_dir}'.[/green]",
    )


@command()
@with_appcontext
def install():
    """Install the dependencies using npm."""
    npm_run("install")


@command()
@with_appcontext
def build():
    """Build the Vite assets."""
    npm_run("run", "build")


@command()
@with_appcontext
def start():
    """Start watching source changes for dev."""
    npm_run("run", "dev")


@command()
@with_appcontext
def check_updates():
    """Check outdated Vite dependencies."""
    npm_run("outdated")


@command()
@with_appcontext
def update():
    """Update Vite and its dependencies, if needed."""
    npm_run("update")


# @command()
# @with_appcontext
# def npm(*args):
#     """Call directly npm with given args."""
#     npm_run(*args)


def npm_run(*args):
    cwd = "vite"
    npm = NPM(cwd=cwd)
    npm.run(*args)
