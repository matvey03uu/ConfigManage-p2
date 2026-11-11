import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from repository_file import (
    get_test_dependencies,
    load_test_repository,
)


class RepositoryFileTests(unittest.TestCase):
    def create_repository_file(self, content):
        temporary_file = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".txt",
            delete=False,
        )
        temporary_file.write(content)
        temporary_file.close()
        self.addCleanup(Path(temporary_file.name).unlink)
        return temporary_file.name

    def test_load_repository(self):
        file_path = self.create_repository_file(
            "A: B, C\nB: D\nC: D\nD:\n"
        )

        graph = load_test_repository(file_path)

        self.assertEqual(
            graph,
            {
                "A": ["B", "C"],
                "B": ["D"],
                "C": ["D"],
                "D": [],
            },
        )

    def test_get_dependencies(self):
        graph = {"A": ["B", "C"], "B": []}

        self.assertEqual(
            get_test_dependencies(graph, "A"),
            ["B", "C"],
        )

    def test_unknown_package(self):
        graph = {"A": ["B"], "B": []}

        self.assertEqual(
            get_test_dependencies(graph, "C"),
            [],
        )

    def test_invalid_package_name(self):
        file_path = self.create_repository_file("abc: B\nB:\n")

        with self.assertRaises(ValueError):
            load_test_repository(file_path)

    def test_missing_dependency(self):
        file_path = self.create_repository_file("A: B\n")

        with self.assertRaises(ValueError):
            load_test_repository(file_path)

    def test_duplicate_package(self):
        file_path = self.create_repository_file("A: B\nA:\nB:\n")

        with self.assertRaises(ValueError):
            load_test_repository(file_path)


if __name__ == "__main__":
    unittest.main()
