from textwrap import dedent

from flask import current_app


def make_vite_css_tag():
    tag = dedent(
        """
        <link rel="stylesheet" href="/_vite/styles.css">
        """
    )
    if current_app.debug:
        url = "//HOST:8383/browser-sync/browser-sync-client.js"
        tag += dedent(
            f"""
            <script id="__bs_script__">
                document.write(
                    "<script async src='{url}'><\\/script>"
                    .replace("HOST", location.hostname)
                );
            </script>
            """
        )
    return tag
