"""
Shared pytest setup.

The scripts under test load ``config.json`` (their real, user-specific
configuration) as soon as they are imported. That file is gitignored, so a
fresh checkout (e.g. CI) won't have one. We create a throwaway config.json
from config.example.json ONLY if one doesn't already exist -- an existing
config.json (the user's real one) is never touched or overwritten.
"""
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")

if SRC not in sys.path:
    sys.path.insert(0, SRC)

_config_path = os.path.join(ROOT, "config.json")
_example_path = os.path.join(ROOT, "config.example.json")

if not os.path.isfile(_config_path) and os.path.isfile(_example_path):
    shutil.copy(_example_path, _config_path)
