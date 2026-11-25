#!/usr/bin/env bash
# SPDX-License-Identifier: BSD-3-Clause
set -eu
cd "$(dirname "$0")"
exec python3 -B -m unittest discover -s tests
