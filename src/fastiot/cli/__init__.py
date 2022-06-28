"""
Methods and classes within this directory are mainly for setting up new projects and building exisiting ones
locally or with the Jenkins pipeline
"""
from fastiot.cli import version
from fastiot.cli.helper_fn import find_modules, import_module

try:
    from fastiot.cli.__version__ import __version__
except ImportError:
    __version__ = version.get_version(complete=True)
