"""Main module."""

import os
from pathlib import Path
from typing import Optional

from flask import Flask, Response, send_from_directory

from .npm import NPM
from .tags import make_tag

ONE_YEAR = 60 * 60 * 24 * 365


class Vite:
    app: Optional[Flask] = None
    npm: Optional[NPM] = None

    def __init__(self, app: Optional[Flask] = None):
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        if "vite" in app.extensions:
            raise RuntimeError(
                "This extension is already registered on this Flask app."
            )

        app.extensions["vite"] = self

        config = app.config
        if config.get("VITE_AUTO_INSERT", True):
            app.after_request(self.after_request)

        npm_bin_path = config.get("VITE_NPM_BIN_PATH", "npm")
        self.npm = NPM(cwd=str(self._get_root()), npm_bin_path=npm_bin_path)

        app.route("/_vite/<path:filename>")(self.vite_static)
        app.template_global("vite_tags")(make_tag)

    def after_request(self, response: Response):
        if response.status_code != 200:
            return response

        mimetype = response.mimetype or ""
        if not mimetype.startswith("text/html"):
            return response

        if not isinstance(response.response, list):
            return response

        body = b"".join(response.response).decode()
        tag = make_tag()
        body = body.replace("</head>", f"{tag}\n</head>")
        response.response = [body.encode("utf8")]
        response.content_length = len(response.response[0])
        return response

    def vite_static(self, filename):
        dist = str(self._get_root() / "dist" / "assets")
        return send_from_directory(dist, filename, max_age=ONE_YEAR)

    def _get_root(self) -> Path:
        return Path(os.getcwd()) / "vite"
