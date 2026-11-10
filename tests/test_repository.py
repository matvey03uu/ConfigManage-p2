import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from repository import find_package


class RepositoryTests(unittest.TestCase):
    @patch("repository.download_package_index")
    def test_find_exact_package_version(self, download_index):
        newline = bytes([10])
        download_index.return_value = (
            b"Package: demo" + newline
            + b"Version: 1.2.3-1ubuntu1" + newline
            + b"Depends: libc6 (>= 2.38), libssl3" + newline
        )
        depends = find_package(
            "https://example.org/ubuntu", "demo", "1.2.3-1ubuntu1"
        )
        self.assertEqual(depends, "libc6 (>= 2.38), libssl3")
        download_index.assert_called_once()

    @patch("repository.download_package_index")
    def test_missing_package_version(self, download_index):
        newline = bytes([10])
        download_index.return_value = (
            b"Package: demo" + newline + b"Version: 1.0" + newline
            + b"Depends: libc6" + newline
        )
        with self.assertRaises(LookupError):
            find_package("https://example.org/ubuntu", "demo", "2.0")


if __name__ == "__main__":
    unittest.main()
