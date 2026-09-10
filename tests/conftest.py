"""
Shared pytest setup.

The project root (parent of tests/) is put on sys.path so tests can import
the `src` package (`from src.core import generator`, etc.). Tests must
never touch the real user's config — SIMS4_RLS_CONFIG_DIR is pointed at a
throwaway temp directory for the whole test session, which
common/paths.py::resolve_config_path() checks before any OS-specific or
portable-mode location.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ["SIMS4_RLS_CONFIG_DIR"] = tempfile.mkdtemp(prefix="s4rls_test_config_")
