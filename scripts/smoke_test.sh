#!/usr/bin/env bash
set -euo pipefail
python -m pip install -e .
contextpack --help
contextpack profiles
contextpack summarize .
