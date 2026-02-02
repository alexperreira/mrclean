from __future__ import annotations

import unittest

from mrclean.paths import (
    is_windows_path,
    is_wsl_mnt_path,
    normalize_input_path,
    windows_to_wsl,
    wsl_to_windows,
)


class PathsTestCase(unittest.TestCase):
    def test_windows_to_wsl(self) -> None:
        self.assertEqual(windows_to_wsl("C:\\Users\\Alex"), "/mnt/c/Users/Alex")
        self.assertEqual(windows_to_wsl("D:\\") , "/mnt/d")

    def test_wsl_to_windows(self) -> None:
        self.assertEqual(wsl_to_windows("/mnt/c/Users/Alex"), "C:\\Users\\Alex")
        self.assertEqual(wsl_to_windows("/mnt/d"), "D:\\")

    def test_path_detection(self) -> None:
        self.assertTrue(is_windows_path("C:\\Windows"))
        self.assertTrue(is_windows_path("d:/data"))
        self.assertTrue(is_wsl_mnt_path("/mnt/c/Users/Alex"))
        self.assertFalse(is_wsl_mnt_path("/home/alex"))

    def test_normalize_input_path_windows(self) -> None:
        normalized = normalize_input_path("C:\\Temp\\file.txt")
        self.assertEqual(normalized.os_path.as_posix(), "/mnt/c/Temp/file.txt")
        self.assertEqual(normalized.style, "windows")

    def test_normalize_input_path_posix(self) -> None:
        normalized = normalize_input_path("/home/alex")
        self.assertEqual(normalized.os_path.as_posix(), "/home/alex")
        self.assertEqual(normalized.style, "posix")
