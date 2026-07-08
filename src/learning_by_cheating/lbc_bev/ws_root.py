"""Resolve ASMC workspace root (host clone or /root/ws in Docker)."""
from __future__ import annotations

import os
from pathlib import Path


def asmc_ws_root() -> Path:
    for key in ("ASMC", "ASMC_WS_ROOT"):
        val = os.environ.get(key)
        if val:
            root = Path(val).expanduser().resolve()
            if (root / "src").is_dir():
                return root
    docker_ws = Path("/root/ws")
    if (docker_ws / "src").is_dir():
        return docker_ws
    # .../src/learning_by_cheating/lbc_bev/ws_root.py -> repo root
    return Path(__file__).resolve().parents[3]
