from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys


FEATURES = ("all", "volume", "fieldlines", "pointcloud", "annotations", "latex")


def find_blender(explicit: str | None) -> str:
    explicit_path = shutil.which(explicit) if explicit else None
    env_value = os.environ.get("BLENDER_BIN")
    env_path = shutil.which(env_value) if env_value else None
    candidates = [explicit, explicit_path, env_value, env_path, shutil.which("blender")]
    if sys.platform == "win32":
        candidates.extend(
            str(path)
            for path in Path(r"C:\Program Files\Blender Foundation").glob(
                r"Blender *\blender.exe"
            )
        )
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    raise SystemExit(
        "Blender was not found. Pass --blender PATH or set the BLENDER_BIN environment variable."
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run BlendET integration tests in Blender"
    )
    parser.add_argument("--blender", help="Path to the Blender executable")
    parser.add_argument("--feature", choices=FEATURES, default="all")
    parser.add_argument("--keep-artifacts", action="store_true")
    args = parser.parse_args()

    tests_dir = Path(__file__).resolve().parent
    addon_root = tests_dir.parent
    artifacts = tests_dir / "artifacts"
    if artifacts.exists() and not args.keep_artifacts:
        shutil.rmtree(artifacts)
    artifacts.mkdir(parents=True, exist_ok=True)

    command = [
        find_blender(args.blender),
        "--background",
        "--factory-startup",
        "--python-exit-code",
        "1",
        "--python",
        str(tests_dir / "blender_runner.py"),
        "--",
        "--addon-root",
        str(addon_root),
        "--feature",
        args.feature,
        "--artifacts",
        str(artifacts),
    ]
    if args.keep_artifacts:
        command.append("--keep-artifacts")
    print(
        "Running:", " ".join(f'"{part}"' if " " in part else part for part in command)
    )
    return subprocess.run(command, cwd=addon_root).returncode


if __name__ == "__main__":
    raise SystemExit(main())
