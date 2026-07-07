"""LBC BEV + MORAI ROS diagnostics — collect a shareable text report."""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

import numpy as np

Lines = List[str]


def _section(title: str) -> List[str]:
    bar = "=" * 60
    return ["", bar, title, bar]


def _run(cmd: List[str], timeout: float = 5.0) -> str:
    try:
        out = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return (out.stdout or "") + (out.stderr or "")
    except Exception as exc:
        return f"(failed: {exc})"


def collect_env_lines() -> Lines:
    lines = _section("1. Environment")
    lines.append(f"timestamp       : {datetime.now().isoformat()}")
    lines.append(f"hostname        : {socket.gethostname()}")
    lines.append(f"hostname -I     : {_run(['hostname', '-I']).strip()}")
    for key in (
        "ROS_MASTER_URI",
        "ROS_IP",
        "MORAI_BRIDGE_IP",
        "MORAI_BRIDGE_PORT",
        "DISPLAY",
        "PYTHONPATH",
    ):
        lines.append(f"{key:16}: {os.environ.get(key, '(unset)')}")
    lines.append(f"python          : {sys.version.split()[0]} @ {sys.executable}")
    return lines


def collect_ros_lines(timeout_sec: float = 3.0) -> Lines:
    lines = _section("2. ROS / roscore")
    master = os.environ.get("ROS_MASTER_URI", "(unset)")
    lines.append(f"ROS_MASTER_URI  : {master}")

    listing = _run(["rostopic", "list"], timeout=timeout_sec).strip()
    if not listing or "ERROR" in listing:
        lines.append("[FAIL] rostopic list — is roscore running? (./bridge.sh)")
        return lines

    lines.append("[OK] roscore reachable")
    topics = [t.strip() for t in listing.splitlines() if t.strip().startswith("/")]
    lines.append(f"topic count     : {len(topics)}")

    lines.append("")
    lines.append("--- rosbridge /connected_clients ---")
    clients = _run(
        ["bash", "-lc", f"timeout {int(timeout_sec)} rostopic echo /connected_clients -n 1"],
        timeout=timeout_sec + 2,
    ).strip()
    lines.append(clients or "(no data)")
    if "clients: []" in clients:
        lines.append("[FAIL] MORAI WebSocket not connected to rosbridge")
    elif "clients:" in clients:
        lines.append("[OK] rosbridge has client(s)")

    morai_expected = (
        "/Ego_topic",
        "/Object_topic",
        "/IntscnTL_topic",
        "/GetTrafficLightStatus",
        "/TrafficLight_status",
        "/lbc_bev/image_full",
        "/lbc_bev/image_cropped",
    )
    lines.append("")
    lines.append("--- key topics ---")
    for t in morai_expected:
        mark = "OK" if t in topics else "--"
        lines.append(f"  [{mark}] {t}")

    lines.append("")
    lines.append("--- topic rates (3s sample) ---")
    for t in ("/Ego_topic", "/Object_topic", "/IntscnTL_topic", "/lbc_bev/image_full"):
        if t not in topics:
            lines.append(f"  [--] {t}")
            continue
        hz_out = _run(
            ["bash", "-lc", f"timeout 4 rostopic hz {t} 2>&1 | head -5"],
            timeout=6,
        )
        rate = "?"
        for row in hz_out.splitlines():
            if "average rate" in row:
                rate = row.strip()
                break
        lines.append(f"  [OK] {t}  {rate}")

    return lines


def collect_ego_sample(timeout_sec: float = 5.0) -> tuple:
    lines = _section("3. MORAI /Ego_topic sample")
    raw = _run(
        [
            "bash",
            "-lc",
            f"timeout {int(timeout_sec)} rostopic echo /Ego_topic -n 1 2>&1",
        ],
        timeout=timeout_sec + 2,
    )
    if not raw.strip() or "timeout" in raw.lower():
        lines.append("[FAIL] no /Ego_topic message (Play + Ego Network Connected?)")
        return lines, None

    lines.append(raw[:2000])
    x = y = yaw = None
    in_position = False
    for row in raw.splitlines():
        stripped = row.strip()
        if stripped.startswith("position:"):
            in_position = True
            continue
        if in_position and stripped.startswith("x:"):
            try:
                x = float(stripped.split(":")[-1])
            except ValueError:
                pass
        if in_position and stripped.startswith("y:"):
            try:
                y = float(stripped.split(":")[-1])
            except ValueError:
                pass
        if stripped.startswith("heading:"):
            try:
                yaw = float(stripped.split(":")[-1])
            except ValueError:
                pass
            in_position = False
    if x is not None and y is not None:
        lines.append(f"[OK] parsed ego: x={x:.3f} y={y:.3f} heading={yaw}")
    return lines, (x, y, yaw or 0.0) if x is not None and y is not None else None


def collect_map_lines(ws_root: Path) -> Lines:
    lines = _section("4. HD map files")
    paths = [
        ws_root / "mgeo_toolkit/data/KATRI/road_mesh_out_line.json",
        ws_root / "R_KR_PG_KATRI/lane_boundary_set.json",
        ws_root / "R_KR_PG_KATRI/traffic_light_set.json",
        ws_root / "R_KR_PG_KATRI/global_info.json",
    ]
    for p in paths:
        if p.is_file():
            lines.append(f"  [OK] {p}  ({p.stat().st_size} bytes)")
        else:
            lines.append(f"  [FAIL] missing {p}")
    return lines


def collect_render_lines(ws_root: Path, ego_xyz: Optional[tuple]) -> Lines:
    lines = _section("5. LBC BEV render test")
    root = str(ws_root)
    try:
        t0 = time.time()
        from lbc_bev import LBCRenderer

        r = LBCRenderer(root)
        lines.append(f"[OK] LBCRenderer init  {time.time() - t0:.2f}s")

        if ego_xyz:
            ex, ey, yaw = ego_xyz
            lines.append(f"ego from ROS     : x={ex:.3f} y={ey:.3f} yaw={yaw:.3f}")
        else:
            d = r.default_ego()
            ex, ey, yaw = d.x, d.y, d.yaw_deg
            lines.append(f"ego (default)    : x={ex:.3f} y={ey:.3f} yaw={yaw:.3f}")

        t1 = time.time()
        out = r.render(ex, ey, yaw)
        lines.append(f"[OK] render         {time.time() - t1:.3f}s")
        bv = out["birdview"]
        cr = out["cropped"]
        lines.append(f"birdview shape   : {bv.shape} dtype={bv.dtype}")
        lines.append(f"cropped shape    : {cr.shape}")
        nz = [int(np.count_nonzero(bv[:, :, i])) for i in range(bv.shape[2])]
        names = ["road", "lane", "tl_r", "tl_y", "tl_g", "veh", "ped"]
        lines.append("channel nonzero  : " + ", ".join(f"{n}={v}" for n, v in zip(names, nz)))
        if nz[0] == 0 and nz[1] == 0:
            lines.append("[WARN] road/lane empty — check map path / ego position")
        else:
            lines.append("[OK] static layers present")
    except Exception as exc:
        lines.append(f"[FAIL] render test: {exc}")
        import traceback

        lines.append(traceback.format_exc())
    return lines


def collect_network_lines() -> Lines:
    lines = _section("6. Network (port 9090)")
    ss = _run(["bash", "-lc", "ss -tln 2>/dev/null | grep 9090 || netstat -tln 2>/dev/null | grep 9090"])
    if "9090" in ss:
        lines.append("[OK] port 9090 listening")
        lines.append(ss.strip())
    else:
        lines.append("[FAIL] port 9090 not listening — run ./bridge.sh")
    return lines


def build_report(
    ws_root: Optional[Path] = None,
    ego_timeout: float = 5.0,
) -> str:
    ws = Path(ws_root or os.path.expanduser("~/aim_ws"))
    all_lines: Lines = []
    all_lines.append("LBC BEV + MORAI Diagnostic Report")
    all_lines.append("(send this file to your mentor / agent)")
    all_lines.extend(collect_env_lines())
    all_lines.extend(collect_network_lines())
    all_lines.extend(collect_ros_lines())
    ego_lines, ego = collect_ego_sample(ego_timeout)
    all_lines.extend(ego_lines)
    all_lines.extend(collect_map_lines(ws))
    all_lines.extend(collect_render_lines(ws, ego))

    all_lines.extend(_section("7. Windows MORAI + Docker Desktop"))
    all_lines.append("  192.168.65.x is Docker VM internal — NOT reachable from Windows PowerShell.")
    all_lines.append("  PowerShell: Test-NetConnection 127.0.0.1 -Port 9090")
    all_lines.append("  Or WSL IP: wsl hostname -I  then Test-NetConnection <ip> -Port 9090")
    all_lines.append("  Fix: docker-compose -f docker-compose.pc.morai-ports.yaml (see show_morai_bridge_ip.sh)")
    all_lines.extend(_section("8. Next steps for RViz"))
    all_lines.append("  1) Terminal A: cd ~/aim_ws && ./bridge.sh")
    all_lines.append("  2) MORAI: Bridge IP per show_morai_bridge_ip.sh, PORT 9090, both tabs Connected")
    all_lines.append("  3) MORAI: Play -> Connect BOTH tabs")
    all_lines.append("  4) ./diagnose_morai_bridge.sh  (clients not [])")
    all_lines.append("  5) cd src/learning_by_cheating && python3 scripts/lbc_bev_diagnose.py")
    all_lines.append("  6) ./scripts/start_lbc_rviz.sh")
    all_lines.append("  RViz: Add Image -> /lbc_bev/image_full or use config/lbc_bev.rviz")
    return "\n".join(all_lines) + "\n"


def save_report(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
