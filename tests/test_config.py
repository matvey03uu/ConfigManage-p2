import sys
import unittest
from argparse import ArgumentTypeError
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from config import (
    parse_config,
    positive_or_zero_int,
    valid_output,
    valid_version,
)


class ConfigTests(unittest.TestCase):
    """Тесты проверки конфигурации приложения."""

    def valid_args(
        self,
        repository: str,
        test_mode: str = "false",
    ) -> list[str]:
        return [
            "--package", "demo",
            "--repository", repository,
            "--test-mode", test_mode,
            "--version", "1.2.3",
            "--output", "graph.svg",
            "--max-depth", "2",
        ]

    def test_valid_url_configuration(self) -> None:
        config = parse_config(
            self.valid_args("https://example.org/ubuntu")
        )

        self.assertEqual(config.package, "demo")
        self.assertEqual(config.max_depth, 2)

    def test_valid_test_repository(self) -> None:
        with TemporaryDirectory() as directory:
            repository = Path(directory) / "repo.txt"
            repository.write_text(
                "A: B\n",
                encoding="utf-8",
            )

            config = parse_config(
                self.valid_args(str(repository), "true")
            )

            self.assertEqual(config.test_mode, "true")

    def test_negative_depth_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            parse_config([
                "--package", "demo",
                "--repository", "https://example.org",
                "--test-mode", "false",
                "--version", "1.2.3",
                "--output", "graph.svg",
                "--max-depth", "-1",
            ])

    def test_non_integer_depth_rejected(self) -> None:
        with self.assertRaises(ArgumentTypeError):
            positive_or_zero_int("abc")

    def test_bad_version_rejected(self) -> None:
        with self.assertRaises(ArgumentTypeError):
            valid_version("latest")

    def test_ubuntu_version_accepted(self) -> None:
        version = "8.5.0-2ubuntu10.6"

        self.assertEqual(valid_version(version), version)

    def test_bad_output_rejected(self) -> None:
        with self.assertRaises(ArgumentTypeError):
            valid_output("graph.png")

    def test_invalid_url_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            parse_config(
                self.valid_args("not-a-url")
            )

    def test_missing_test_file_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            parse_config(
                self.valid_args(
                    "missing-repository.txt",
                    "true",
                )
            )

    def test_missing_parameter_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            parse_config(["--package", "demo"])


if __name__ == "__main__":
    unittest.main()
