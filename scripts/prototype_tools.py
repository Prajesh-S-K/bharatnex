"""Cross-platform checks and maintenance helpers for the local prototype."""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import socket
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = REPO_ROOT / "data" / "smart_mine.db"


def local_ip() -> str:
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        connection.connect(("192.0.2.1", 80))
        return str(connection.getsockname()[0])
    except OSError:
        return "127.0.0.1"
    finally:
        connection.close()


def check() -> int:
    requirements = {
        "Python 3.11+": sys.version_info >= (3, 11),
        "FastAPI": importlib.util.find_spec("fastapi") is not None,
        "JSON Schema": importlib.util.find_spec("jsonschema") is not None,
        "Node.js": shutil.which("node") is not None,
        "npm": shutil.which("npm") is not None,
        "Dashboard dependencies": (REPO_ROOT / "apps/dashboard/node_modules").is_dir(),
    }
    for name, available in requirements.items():
        print(f"{'PASS' if available else 'MISSING':7} {name}")
    print(f"\nOperator dashboard: http://{local_ip()}:5173/")
    print(f"Inspection phones:  http://{local_ip()}:5173/inspection")
    return 0 if all(requirements.values()) else 1


def reset() -> int:
    sys.path.insert(0, str(REPO_ROOT))
    from apps.api.storage import Database

    database = Database(DATABASE_PATH)
    database.initialize()
    database.reset_demo()
    print("Prototype readings, incidents, assignments and audit events were reset.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "network", "reset"))
    arguments = parser.parse_args()
    if arguments.command == "check":
        return check()
    if arguments.command == "reset":
        return reset()
    print(f"Operator dashboard: http://{local_ip()}:5173/")
    print(f"Inspection phones:  http://{local_ip()}:5173/inspection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
