"""Pytest bootstrap: make the ``app`` package importable.

Adds the ``backend/`` directory (this file's directory) to ``sys.path`` so
tests can ``import app`` regardless of the directory pytest is invoked from.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
