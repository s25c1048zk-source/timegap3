# SPDX-License-Identifier: BSD-3-Clause
import runpy
import unittest
from pathlib import Path


COMMAND = Path(__file__).resolve().parents[1] / "timegap"
seconds_since_midnight = runpy.run_path(str(COMMAND))["seconds_since_midnight"]


class ClockTests(unittest.TestCase):
    def test_seconds_since_midnight(self):
        for clock, expected in [("00:00:00", 0), ("01:02:03", 3723), ("23:59:59", 86399)]:
            with self.subTest(clock=clock):
                self.assertEqual(seconds_since_midnight(clock), expected)
