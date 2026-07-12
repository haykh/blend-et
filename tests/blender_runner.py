from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import unittest


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--addon-root", required=True)
    parser.add_argument("--feature", default="all")
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--keep-artifacts", action="store_true")
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def main() -> int:
    args = _arguments()
    addon_root = Path(args.addon_root).resolve()
    if addon_root.name != "blend_et":
        raise RuntimeError(
            f"Expected add-on directory named 'blend_et', got {addon_root}"
        )

    sys.path.insert(0, str(addon_root.parent))
    sys.path.insert(0, str(addon_root))
    os.environ["BLEND_ET_TEST_ARTIFACTS"] = str(Path(args.artifacts).resolve())
    os.environ["BLEND_ET_TEST_KEEP_ARTIFACTS"] = "1" if args.keep_artifacts else "0"

    import blend_et

    blend_et.register()

    feature_modules = {
        "volume": "tests.test_volume",
        "fieldlines": "tests.test_fieldlines",
        "pointcloud": "tests.test_pointcloud",
        "annotations": "tests.test_annotations",
        "latex": "tests.test_latex",
    }
    selected = list(feature_modules) if args.feature == "all" else [args.feature]
    unknown = set(selected) - set(feature_modules)
    if unknown:
        raise ValueError(f"Unknown feature(s): {', '.join(sorted(unknown))}")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for feature in selected:
        suite.addTests(loader.loadTestsFromName(feature_modules[feature]))

    try:
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1
    finally:
        blend_et.unregister()


if __name__ == "__main__":
    raise SystemExit(main())
