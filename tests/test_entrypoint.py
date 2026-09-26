"""Check the root launcher as well as the installed package."""

import os
from pathlib import Path
import subprocess
import sys
import unittest


class EntrypointTests(unittest.TestCase):
    def test_root_launcher_imports_without_pythonpath(self):
        launcher = Path(__file__).resolve().parents[1] / "app.py"
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        result = subprocess.run(
            [sys.executable, "-I", "-c",
             "import runpy, sys; runpy.run_path(sys.argv[1], run_name='launcher_test')",
             str(launcher)],
            cwd=launcher.parent.parent, env=environment,
            capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
