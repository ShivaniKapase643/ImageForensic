"""Start the ImageGuard Streamlit app using Render's assigned port."""

import os
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent


def main() -> int:
    port = os.environ.get("PORT", "10000")
    try:
        port_number = int(port)
    except ValueError as error:
        raise SystemExit("PORT must be an integer between 1 and 65535.") from error

    if not 1 <= port_number <= 65535:
        raise SystemExit("PORT must be an integer between 1 and 65535.")

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(PROJECT_DIR / "app.py"),
        "--server.address=0.0.0.0",
        f"--server.port={port_number}",
        "--server.headless=true",
    ]
    if os.name != "nt":
        # On Render, replace the launcher process so signals reach Streamlit directly.
        os.chdir(PROJECT_DIR)
        os.execv(command[0], command)

    try:
        return subprocess.run(command, cwd=PROJECT_DIR, check=False).returncode
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
