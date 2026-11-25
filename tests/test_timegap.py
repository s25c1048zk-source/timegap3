# SPDX-License-Identifier: BSD-3-Clause
import runpy
import subprocess
import sys
import unittest
from pathlib import Path


COMMAND = Path(__file__).resolve().parents[1] / "timegap"
seconds_since_midnight = runpy.run_path(str(COMMAND))["seconds_since_midnight"]


class ClockTests(unittest.TestCase):
    def test_seconds_since_midnight(self):
        for clock, expected in [("00:00:00", 0), ("01:02:03", 3723), ("23:59:59", 86399)]:
            with self.subTest(clock=clock):
                self.assertEqual(seconds_since_midnight(clock), expected)
class CommandTests(unittest.TestCase):
    def assert_command(self, data, output="", error="", status=0, args=()):
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(COMMAND), *args],
            input=data,
            capture_output=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, status)
        self.assertEqual(result.stdout, output)
        self.assertEqual(result.stderr, error)

    def test_consecutive_intervals(self):
        self.assert_command(
            "12:00:00\n12:00:03\n12:00:10\n12:01:00\n",
            "3\n7\n50\n",
        )

    def test_short_input(self):
        for data in ("", "09:00:00\n"):
            with self.subTest(data=data):
                self.assert_command(data)
    def test_malformed_clock(self):
        for clock in ("", "1:02:03", "12:00:00 ", "１２:００:００", "12-00-00", "ab:cd:ef"):
            with self.subTest(clock=clock):
                self.assert_command(
                    clock + "\n",
                    error="1行目: 時刻はHH:MM:SS形式で入力してください\n",
                    status=1,
                )
