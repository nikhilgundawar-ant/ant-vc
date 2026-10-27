#!/usr/bin/env python3
"""Entry point for the ant. engine. Run `python3 -I -S engine/instinct.py --help`.

Scheduled runs start it isolated (`-I -S`): no site packages, no environment variables, and neither the working folder
nor the script's folder on the import path. The engine adds its own folder after the standard library, so a stray
`json.py` beside it can never stand in for the real one."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)

from instinct.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
