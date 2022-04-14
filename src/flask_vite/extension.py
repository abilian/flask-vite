"""Main module."""

import os
from pathlib import Path
from typing import Union

from flask import Flask, Response, send_from_directory

from .tags import make_vite_css_tag


class Vite(object):
    def __init__(self, app: Union[Flask, None] = None):
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
        app.template_global("vite_css")(make_vite_css_tag)

    def after_request(self, response: Response):
        if not response.mimetype.startswith("text/html"):
            return response

        if response.status_code != 200:
            return response

        if not isinstance(response.response, list):
            return response

        body = b"".join(response.response).decode()
        tag = make_vite_css_tag()
        body = body.replace("</head>", f"{tag}\n</head>")
        response.response = [body.encode("utf8")]
        response.content_length = len(response.response[0])
        return response

    def vite_static(self, filename):
        dist = str(Path(os.getcwd()) / "vite" / "dist")
        return send_from_directory(dist, filename)
