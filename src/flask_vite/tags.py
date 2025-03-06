# Copyright (c) 2022-2024, Abilian SAS
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import glob
from pathlib import Path
from textwrap import dedent

from flask import current_app, url_for
from markupsafe import Markup


def make_tag(*, static: bool = False):
    if static or not current_app.debug:
        tag = make_static_tag()
    else:
        tag = make_debug_tag()
    return Markup(tag)  # noqa: RUF035


def make_static_tag():
    vite_folder_path = current_app.extensions["vite"].vite_folder_path
    js_file = Path(glob.glob(f"{vite_folder_path}/dist/assets/*.js")[0]).name
    css_file = Path(glob.glob(f"{vite_folder_path}/dist/assets/*.css")[0]).name

    js_file_url = url_for("vite.static", filename=js_file)
    css_file_url = url_for("vite.static", filename=css_file)

    return dedent(
        f"""
            <!-- FLASK_VITE_HEADER -->
            <script type="module" src="{js_file_url}"></script>
            <link rel="stylesheet" href="{css_file_url}"></link>
        """
    ).strip()


def make_debug_tag():
    return dedent(
        """
            <!-- FLASK_VITE_HEADER -->
            <script type="module" src="http://localhost:3000/@vite/client"></script>
            <script type="module" src="http://localhost:3000/main.js"></script>
        """
    ).strip()
