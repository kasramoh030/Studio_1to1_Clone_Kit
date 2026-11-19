"""ReelForge - GPU motion graphics & video generation built for Claude Code.

    from reelforge import Project, Scene, ease, PALETTES
"""
import os as _os
_os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # before numpy loads: avoids OpenBLAS OOM on busy machines
__version__ = "1.0.0"
from .project import Project, Scene, PRESETS
from .ease import *            # noqa: F401,F403  (easing, colour helpers, PALETTES)
from . import audio, ease       # noqa: F401
