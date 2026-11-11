import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dependency_graph import build_dependency_graph


class DependencyGraphTests(unittest.TestCase):
    def setUp(self):
        self.repository = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }

    def get_dependencies(self, package_name):
        return self.repository.get(package_name, [])

    def test_build_graph(self):
        graph = build_dependency_graph(
            "A", self.get_dependencies, 2
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

    def test_max_depth_zero(self):
        graph = build_dependency_graph(
            "A", self.get_dependencies, 0
        )
        self.assertEqual(graph, {"A": []})

    def test_max_depth_one(self):
        graph = build_dependency_graph(
            "A", self.get_dependencies, 1
        )
        self.assertEqual(
            graph,
            {"A": ["B", "C"], "B": [], "C": []},
        )

    def test_cyclic_dependencies(self):
        repository = {"A": ["B"], "B": ["C"], "C": ["A"]}

        graph = build_dependency_graph(
            "A", repository.get, 10
        )

        self.assertEqual(
            graph,
            {"A": ["B"], "B": ["C"], "C": ["A"]},
        )

    def test_package_without_dependencies(self):
        graph = build_dependency_graph(
            "D", self.get_dependencies, 5
        )
        self.assertEqual(graph, {"D": []})

    def test_negative_depth(self):
        with self.assertRaises(ValueError):
            build_dependency_graph(
                "A", self.get_dependencies, -1
            )


if __name__ == "__main__":
    unittest.main()
