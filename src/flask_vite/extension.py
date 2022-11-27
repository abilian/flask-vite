"""Main module."""

import os
from pathlib import Path
from typing import Optional

from flask import Flask, Response, send_from_directory

from .tags import make_vite_header_tag

ONE_YEAR = 60 * 60 * 24 * 365


class Vite:
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

        app.after_request(self.after_request)
        app.route("/_vite/<path:filename>")(self.vite_static)
        app.template_global("vite_header_tags")(make_vite_header_tag)

    def after_request(self, response: Response):
        if response.status_code != 200:
            return response

        mimetype = response.mimetype or ""
        if not mimetype.startswith("text/html"):
            return response

        if not isinstance(response.response, list):
            return response

        body = b"".join(response.response).decode()
        tag = make_vite_header_tag()
        body = body.replace("</head>", f"{tag}\n</head>")
        response.response = [body.encode("utf8")]
        response.content_length = len(response.response[0])
        return response

    def vite_static(self, filename):
        dist = str(Path(os.getcwd()) / "vite" / "dist" / "assets")
        return send_from_directory(dist, filename, max_age=ONE_YEAR)
