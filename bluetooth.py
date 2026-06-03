import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class BlueutilError(RuntimeError):
    pass


def _candidate_blueutil_paths() -> List[Path]:
    candidates: List[Path] = []

    env_path = os.getenv("MAC_BLUEUTIL_PATH")
    if env_path:
        candidates.append(Path(env_path).expanduser())

    if getattr(sys, "frozen", False):
        exec_dir = Path(sys.executable).resolve().parent
        candidates.extend(
            [
                exec_dir / "blueutil",
                exec_dir.parent / "Resources" / "blueutil",
            ]
        )

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        base = Path(meipass)
        candidates.extend([base / "blueutil", base / "Resources" / "blueutil"])

    # GUI apps on macOS launch with a minimal PATH that excludes Homebrew.
    # Add both standard Homebrew prefixes explicitly before falling back to which().
    candidates.extend([
        Path("/opt/homebrew/bin/blueutil"),  # Apple Silicon
        Path("/usr/local/bin/blueutil"),     # Intel
    ])

    which_path = shutil.which("blueutil")
    if which_path:
        candidates.append(Path(which_path))

    # Preserve order while removing duplicates.
    deduped: List[Path] = []
    seen = set()
    for path in candidates:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(path)

    return deduped


def resolve_blueutil_path() -> Path:
    for candidate in _candidate_blueutil_paths():
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate

    raise BlueutilError(
        "blueutil binary not found. Install it or set MAC_BLUEUTIL_PATH."
    )


def _run_blueutil(args: List[str]) -> subprocess.CompletedProcess[str]:
    binary = resolve_blueutil_path()
    result = subprocess.run(
        [str(binary), *args],
        text=True,
        capture_output=True,
        check=False,
    )

    if result.returncode != 0:
        stderr = result.stderr.strip() or "Unknown blueutil error"
        raise BlueutilError(stderr)

    return result


def list_paired_devices() -> List[Dict[str, str]]:
    result = _run_blueutil(["--paired", "--format", "json"])
    output = result.stdout.strip()
    if not output:
        return []

    try:
        payload = json.loads(output)
    except json.JSONDecodeError as exc:
        raise BlueutilError(f"Failed to parse blueutil output: {exc}") from exc

    devices: List[Dict[str, str]] = []
    for item in payload:
        address = item.get("address")
        if not address:
            continue
        devices.append(
            {
                "name": item.get("name") or "Unknown Device",
                "address": address,
            }
        )
    return devices


def unpair_device(address: str) -> None:
    _run_blueutil(["--unpair", address])


def pair_device(address: str) -> None:
    _run_blueutil(["--pair", address])


def connect_device(address: str) -> None:
    _run_blueutil(["--connect", address])


def is_device_connected(address: str) -> bool:
    result = _run_blueutil(["--is-connected", address])
    return result.stdout.strip() == "1"


def _is_already_paired_error(message: str) -> bool:
    lowered = message.lower()
    return "already" in lowered and "pair" in lowered


def try_pair_and_connect_with_retries(
    address: str,
    attempts: int = 6,
    delay_seconds: float = 2.0,
) -> Tuple[bool, Optional[str]]:
    last_error: Optional[str] = None
    has_paired = False

    for _ in range(attempts):
        # Pair until it succeeds once; after that, keep retrying connect.
        try:
            if not has_paired:
                pair_device(address)
                has_paired = True
        except BlueutilError as exc:
            if _is_already_paired_error(str(exc)):
                has_paired = True
            else:
                last_error = str(exc)
                time.sleep(delay_seconds)
                continue

        try:
            connect_device(address)
            if is_device_connected(address):
                return True, None
            last_error = "Pair/connect command ran, but device is not connected yet"
        except BlueutilError as exc:
            last_error = str(exc)

        time.sleep(delay_seconds)

    return False, last_error


def is_blueutil_available() -> bool:
    try:
        resolve_blueutil_path()
        return True
    except BlueutilError:
        return False
