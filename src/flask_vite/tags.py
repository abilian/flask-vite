# Copyright (c) 2022-2024, Abilian SAS
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import glob
from textwrap import dedent

from flask import current_app


def make_tag(*, static: bool = False):
    if static or not current_app.debug:
        return make_static_tag()
    else:
        return make_debug_tag()


def make_static_tag():
    js_file = glob.glob("vite/dist/assets/*.js")[0].split("/")[-1]
    css_file = glob.glob("vite/dist/assets/*.css")[0].split("/")[-1]
    return dedent(
        f"""
            <!-- FLASK_VITE_HEADER -->
            <script type="module" src="/_vite/{js_file}"></script>
            <link rel="stylesheet" href="/_vite/{css_file}"></link>
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
