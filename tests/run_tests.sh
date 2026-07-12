#!/usr/bin/env sh
set -eu

python3 "$(dirname "$0")/run_tests.py" "$@"
