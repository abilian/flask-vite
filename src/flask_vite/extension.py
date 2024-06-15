# Copyright (c) 2022-2024, Abilian SAS
#
# SPDX-License-Identifier: MIT
"""Main module."""

from __future__ import annotations

import os
from http.client import OK
from pathlib import Path

from flask import Flask, Response, send_from_directory, request

from .npm import NPM
from .tags import make_tag

ONE_YEAR = 60 * 60 * 24 * 365
VITE_ASSET_HOST_WILDCARD_VARIABLE = '<vite_asset_host>'


class Vite:
    app: Flask | None = None
    npm: NPM | None = None

    def __init__(self, app: Flask | None = None, vite_asset_host: str | None = None):
        self.app = app
        self.vite_asset_host = vite_asset_host

        if app is not None:
            self.init_app(app, vite_asset_host=vite_asset_host)

    def init_app(self, app: Flask, vite_asset_host: str | None = None):
        if "vite" in app.extensions:
            raise RuntimeError(
                "This extension is already registered on this Flask app."
            )

        self._validate_and_configure_vite_asset_host(app, vite_asset_host)

        app.extensions["vite"] = self

        config = app.config
        if config.get("VITE_AUTO_INSERT", False):
            app.after_request(self.after_request)

        npm_bin_path = config.get("VITE_NPM_BIN_PATH", "npm")
        self.npm = NPM(cwd=str(self._get_root()), npm_bin_path=npm_bin_path)

        app.route("/_vite/<path:filename>", endpoint='vite.static', host=self.vite_asset_host)(self.vite_static)
        app.template_global("vite_tags")(make_tag)

    def _validate_and_configure_vite_asset_host(self, app, vite_asset_host: str | None) -> str | None:
        if vite_asset_host and self.vite_asset_host and vite_asset_host != self.vite_asset_host:
            raise ValueError(
                "`vite_asset_host` has been configured differently in two places; use either "
                "`Vite(vite_asset_host=...)` or `Vite().init_app(vite_asset_host=...)`, not both."
            )

        vite_asset_host = vite_asset_host or self.vite_asset_host
        if vite_asset_host:
            if not app.url_map.host_matching:
                raise ValueError("`vite_asset_host` should only be set if your Flask app is using `host_matching`.")

            if vite_asset_host.strip() == '*':
                vite_asset_host = VITE_ASSET_HOST_WILDCARD_VARIABLE

            elif '<' in vite_asset_host and '>' in vite_asset_host:
                raise ValueError(
                    "`vite_asset_host` must either be a host name with no variables, to serve all "
                    "vite assets from a single host, or the wildcard value `*` to serve from the same host as the "
                    "current request."
                )

            @app.url_defaults
            def inject_vite_asset_host_if_required(endpoint, values) -> None:
                if app.url_map.is_endpoint_expecting(endpoint, "vite_asset_host"):
                    values.setdefault("vite_asset_host", request.host)

        self.vite_asset_host = vite_asset_host

    def after_request(self, response: Response):
        if response.status_code != OK:
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

    def vite_static(self, filename, vite_asset_host: str | None = None):
        dist = str(self._get_root() / "dist" / "assets")
        return send_from_directory(dist, filename, max_age=ONE_YEAR)

    def _get_root(self) -> Path:
        return Path(os.getcwd()) / "vite"
