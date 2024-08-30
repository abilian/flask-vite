# Copyright (c) 2022-2024, Abilian SAS
#
# SPDX-License-Identifier: MIT
"""Main module."""

from __future__ import annotations

import os
from http.client import OK
from pathlib import Path

from flask import Flask, Response, request, send_from_directory

from .npm import NPM
from .tags import make_tag

ONE_YEAR = 60 * 60 * 24 * 365
VITE_ROUTES_HOST_WILDCARD_VARIABLE = "<vite_routes_host>"


class ViteError(ValueError):
    pass


class Vite:
    app: Flask | None = None
    npm: NPM | None = None
    vite_folder_path: str = "vite"

    def __init__(self, app: Flask | None = None, vite_routes_host: str | None = None):
        self.app = app
        self.vite_routes_host = vite_routes_host

        if app is not None:
            self.init_app(app, vite_routes_host=vite_routes_host)

    def init_app(self, app: Flask, vite_routes_host: str | None = None):
        if "vite" in app.extensions:
            raise ViteError("This extension is already registered on this Flask app.")

        self._validate_and_configure_vite_routes_host(app, vite_routes_host)

        app.extensions["vite"] = self

        config = app.config

        vite_folder_path = config.get("VITE_FOLDER_PATH", "vite")
        self.vite_folder_path = vite_folder_path

        if config.get("VITE_AUTO_INSERT", False):
            app.after_request(self.after_request)

        npm_bin_path = config.get("VITE_NPM_BIN_PATH", "npm")
        self.npm = NPM(cwd=str(self._get_root()), npm_bin_path=npm_bin_path)

        app.route(
            "/_vite/<path:filename>", endpoint="vite.static", host=self.vite_routes_host
        )(self.vite_static)
        app.template_global("vite_tags")(make_tag)

    def _validate_and_configure_vite_routes_host(
        self, app, vite_routes_host: str | None
    ) -> None:
        if (
            vite_routes_host
            and self.vite_routes_host
            and vite_routes_host != self.vite_routes_host
        ):
            raise ViteError(
                "`vite_routes_host` has been configured differently in two places; use either "
                "`Vite(vite_routes_host=...)` or `Vite().init_app(vite_routes_host=...)`, not both."
            )

        vite_routes_host = vite_routes_host or self.vite_routes_host
        if vite_routes_host:
            if not app.url_map.host_matching:
                raise ViteError(
                    "`vite_routes_host` should only be set if your Flask app is using `host_matching`."
                )

            if vite_routes_host.strip() == "*":
                vite_routes_host = VITE_ROUTES_HOST_WILDCARD_VARIABLE

            elif "<" in vite_routes_host and ">" in vite_routes_host:
                raise ViteError(
                    "`vite_routes_host` must either be a host name with no variables, to serve all "
                    "vite assets from a single host, or the wildcard value `*` to serve from the same host as the "
                    "current request."
                )

            @app.url_defaults
            def inject_vite_routes_host_if_required(endpoint, values) -> None:
                if app.url_map.is_endpoint_expecting(endpoint, "vite_routes_host"):
                    values.setdefault("vite_routes_host", request.host)

        self.vite_routes_host = vite_routes_host

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

    def vite_static(
        self,
        filename,
        vite_routes_host: str | None = None,  # noqa: ARG002
    ):
        dist = str(self._get_root() / "dist" / "assets")
        return send_from_directory(dist, filename, max_age=ONE_YEAR)

    def _get_root(self) -> Path:
        return Path(os.getcwd()) / self.vite_folder_path
