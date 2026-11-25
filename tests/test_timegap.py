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
            input=data.encode("utf-8"),
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, status)
        self.assertEqual(result.stdout.decode("utf-8").replace("\r\n", "\n"), output)
        self.assertEqual(result.stderr.decode("utf-8").replace("\r\n", "\n"), error)
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
    def test_out_of_range(self):
        for clock in ("24:00:00", "00:60:00", "00:00:60"):
            with self.subTest(clock=clock):
                self.assert_command(
                    "00:00:00\n" + clock,
                    error="2行目: 時刻の範囲が正しくありません\n",
                    status=1,
                )
    def test_backwards_and_midnight(self):
        for data in ("12:20:00\n12:19:59", "23:59:59\n00:00:00"):
            with self.subTest(data=data):
                self.assert_command(
                    data,
                    error="2行目: 時刻が逆戻りしています\n",
                    status=1,
                )

    def test_equal_times(self):
        self.assert_command("10:00:00\n10:00:00\n", "0\n")
    def test_arguments(self):
        for args in (("times.txt",), ("--help",), ("a", "b")):
            with self.subTest(args=args):
                self.assert_command(
                    "bad input",
                    error="使い方: timegap < times.txt\n",
                    status=1,
                    args=args,
                )

    def test_missing_final_newline(self):
        self.assert_command("01:59:59\n02:00:00", "1\n")

    def test_crlf_input(self):
        self.assert_command("00:00:00\r\n23:59:59\r\n", "86399\n")

    def test_valid_output_before_error(self):
        self.assert_command(
            "00:00:00\n00:01:00\nwrong\n00:02:00\n",
            output="60\n",
            error="3行目: 時刻はHH:MM:SS形式で入力してください\n",
            status=1,
        )
