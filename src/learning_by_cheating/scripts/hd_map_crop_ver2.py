#!/usr/bin/env python3
"""Deprecated: use lbc_bev_collector.py (LBC 7-channel). Forwards to LBC collector."""
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_LBC_ROOT = _SCRIPT_DIR.parent
for p in (str(_SCRIPT_DIR), str(_LBC_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from lbc_bev_collector import main

if __name__ == "__main__":
    main()
