from pathlib import Path

import pyanalyze
from pyanalyze.error_code import ErrorCode

import flask_vite


class Config(pyanalyze.config.Config):
    DEFAULT_DIRS = (str(Path(flask_vite.__file__).parent),)
    DEFAULT_BASE_MODULE = pyanalyze
    ENABLED_ERRORS = {
        ErrorCode.possibly_undefined_name,
        ErrorCode.use_fstrings,
        ErrorCode.value_always_true,
        ErrorCode.unused_ignore,
        ErrorCode.missing_f,
        ErrorCode.bare_ignore,
        ErrorCode.implicit_reexport,
        # Needs some code tweaks
        # ErrorCode.missing_return_annotation,
        # ErrorCode.missing_parameter_annotation,
        # ErrorCode.unused_variable,
    }
    DISABLED_ERRORS = {
        ErrorCode.incompatible_call,
        ErrorCode.incompatible_return_value,
        ErrorCode.internal_error,
        ErrorCode.undefined_attribute,
    }


class PyanalyzeVisitor(pyanalyze.name_check_visitor.NameCheckVisitor):
    config = Config()
    should_check_environ_for_files = False


def test_all() -> None:
    PyanalyzeVisitor.check_all_files()
