import subprocess
from textwrap import dedent

# Assume npm is in the path for now.
NPM_BIN_PATH = "npm"


class NPMException(Exception):
    pass


class NPM:
    cwd: str
    npm_bin_path: str

    def __init__(self, cwd="", npm_bin_path=None):
        self.npm_bin_path = npm_bin_path if npm_bin_path else NPM_BIN_PATH
        self.cwd = cwd

    def run(self, *args):
        try:
            subprocess.run([self.npm_bin_path] + list(args), cwd=self.cwd)
        except OSError:
            msg = """
            It looks like node.js and/or npm is not installed or cannot be found.
            Visit https://nodejs.org to download and install node.js for your system.
            """

            raise NPMException(dedent(msg))
