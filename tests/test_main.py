import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from contextlib import redirect_stdout
from io import StringIO

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import main


class MainTests(unittest.TestCase):
    @patch("main.parse_config")
    @patch("main.load_test_repository")
    def test_test_mode_builds_graph(
        self,
        load_repository,
        parse_configuration,
    ):
        parse_configuration.return_value = SimpleNamespace(
            test_mode="true",
            repository="repository.txt",
            package="A",
            version="1.0",
            max_depth=2,
        )
        load_repository.return_value = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }

        output = StringIO()

        with redirect_stdout(output):
            main.main()

        self.assertIn("Пакет: A", output.getvalue())
        self.assertIn("A -> B, C", output.getvalue())
        self.assertIn("B -> D", output.getvalue())
        self.assertIn("D -> нет зависимостей", output.getvalue())

    @patch("main.find_package_dependencies")
    @patch("main.find_package")
    def test_real_graph(
        self,
        find_root,
        find_dependency,
    ):
        find_root.return_value = "B, C"
        find_dependency.side_effect = ["D", "D", ""]

        graph = main.get_real_graph(
            "https://example.org/ubuntu",
            "A",
            "1.0",
            2,
        )

        self.assertEqual(
            graph,
            {
                "A": ["B", "C"],
                "B": ["D"],
                "C": ["D"],
                "D": [],
            },
        )

    @patch("main.parse_config")
    @patch("main.load_test_repository")
    def test_unknown_root_package(
        self,
        load_repository,
        parse_configuration,
    ):
        parse_configuration.return_value = SimpleNamespace(
            test_mode="true",
            repository="repository.txt",
            package="Z",
            version="1.0",
            max_depth=2,
        )
        load_repository.return_value = {"A": ["B"], "B": []}

        with self.assertRaises(SystemExit):
            main.main()


if __name__ == "__main__":
    unittest.main()
