import re
from pathlib import Path

PACKAGE_NAME_PATTERN = re.compile(r"^[A-Z]+$")


def load_test_repository(file_path: str) -> dict[str, list[str]]:
    """Загружает описание графа зависимостей из тестового файла."""
    path = Path(file_path)
    graph = {}

    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue

        if ":" not in line:
            raise ValueError(
                f"Строка {line_number}: отсутствует разделитель ':'"
            )

        package, dependencies_text = line.split(":", 1)
        package = package.strip()

        if not PACKAGE_NAME_PATTERN.fullmatch(package):
            raise ValueError(
                f"Строка {line_number}: неверное имя пакета {package}"
            )

        if package in graph:
            raise ValueError(
                f"Строка {line_number}: пакет {package} уже описан"
            )

        dependencies = [
            item.strip()
            for item in dependencies_text.split(",")
            if item.strip()
        ]

        for dependency in dependencies:
            if not PACKAGE_NAME_PATTERN.fullmatch(dependency):
                raise ValueError(
                    f"Строка {line_number}: "
                    f"неверное имя зависимости {dependency}"
                )

        graph[package] = dependencies

    for package, dependencies in graph.items():
        for dependency in dependencies:
            if dependency not in graph:
                raise ValueError(
                    f"Пакет {package} зависит от неописанного пакета "
                    f"{dependency}"
                )

    return graph


def get_test_dependencies(
    graph: dict[str, list[str]],
    package_name: str,
) -> list[str]:
    """Возвращает прямые зависимости пакета из тестового графа."""
    return graph.get(package_name, [])
