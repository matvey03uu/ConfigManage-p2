import argparse
import re
from pathlib import Path
from urllib.parse import urlparse


def positive_or_zero_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "должно быть целым числом"
        ) from exc
    if number < 0:
        raise argparse.ArgumentTypeError("не может быть отрицательным")
    return number


def non_empty(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise argparse.ArgumentTypeError("значение не должно быть пустым")
    return cleaned


def valid_version(value: str) -> str:
    cleaned = non_empty(value)
    if not re.fullmatch(r"(?=.*[0-9])[A-Za-z0-9.+:~_-]+", cleaned):
        raise argparse.ArgumentTypeError(
            "версия содержит недопустимые символы"
        )
    return cleaned


def valid_output(value: str) -> str:
    cleaned = non_empty(value)
    if Path(cleaned).name != cleaned:
        raise argparse.ArgumentTypeError(
            "укажите имя файла без пути; например, dependencies.svg"
        )
    if Path(cleaned).suffix.lower() != ".svg":
        raise argparse.ArgumentTypeError(
            "расширение выходного файла должно быть .svg"
        )
    return cleaned


def valid_repository(value: str) -> str:
    return non_empty(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Минимальный прототип визуализатора зависимостей пакетов."
    )
    parser.add_argument(
        "--package", required=True, type=non_empty,
        help="имя анализируемого пакета",
    )
    parser.add_argument(
        "--repository", required=True, type=valid_repository,
        help="URL репозитория или путь к файлу тестового репозитория",
    )
    parser.add_argument(
        "--test-mode", required=True, choices=("true", "false"),
        help="режим тестового репозитория: true или false",
    )
    parser.add_argument(
        "--version", required=True, type=valid_version,
        help="версия анализируемого пакета, например 1.2.3",
    )
    parser.add_argument(
        "--output", required=True, type=valid_output,
        help="имя выходного SVG-файла, например dependencies.svg",
    )
    parser.add_argument(
        "--max-depth", required=True, type=positive_or_zero_int,
        help="максимальная глубина анализа (целое число >= 0)",
    )
    return parser


def validate_repository_mode(
    parser: argparse.ArgumentParser, repository: str, test_mode: str
) -> None:
    if test_mode == "true":
        path = Path(repository).expanduser()
        if not path.exists():
            parser.error(
                "--repository: файл тестового репозитория не найден: "
                f"{repository}"
            )
        if not path.is_file():
            parser.error(
                "--repository: в тестовом режиме нужен путь к файлу: "
                f"{repository}"
            )
    else:
        parsed = urlparse(repository)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            parser.error(
                "--repository: в обычном режиме укажите корректный URL "
                "с http:// или https://"
            )


def parse_config(argv: list[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    config = parser.parse_args(argv)
    validate_repository_mode(parser, config.repository, config.test_mode)
    return config
