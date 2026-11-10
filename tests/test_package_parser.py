import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from package_parser import (
    dependency_package_names,
    extract_direct_dependencies,
    split_dependency_groups,
)


class PackageParserTests(unittest.TestCase):
    def test_split_depends_groups(self):
        value = "libc6 (>= 2.38), libcurl4 (>= 8.0) | libcurl3"
        self.assertEqual(
            split_dependency_groups(value),
            ["libc6 (>= 2.38)", "libcurl4 (>= 8.0) | libcurl3"],
        )

    def test_extract_keeps_alternatives(self):
        value = "libc6 (>= 2.38), libssl3 | libssl1.1"
        self.assertEqual(
            extract_direct_dependencies(value),
            ["libc6 (>= 2.38)", "libssl3 | libssl1.1"],
        )

    def test_extract_package_names(self):
        value = "libc6 (>= 2.38), libssl3 | libssl1.1"
        self.assertEqual(
            dependency_package_names(value),
            ["libc6", "libssl3", "libssl1.1"],
        )

    def test_empty_depends(self):
        self.assertEqual(extract_direct_dependencies(""), [])


if __name__ == "__main__":
    unittest.main()
