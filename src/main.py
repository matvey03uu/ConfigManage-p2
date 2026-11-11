from urllib.error import URLError
from config import parse_config
from dependency_graph import build_dependency_graph
from package_parser import dependency_package_names
from repository import find_package, find_package_dependencies
from repository_file import load_test_repository, get_test_dependencies


def get_real_graph(
    repository_url: str,
    package_name: str,
    package_version: str,
    max_depth: int,
) -> dict[str, list[str]]:
    """Строит граф для настоящего Ubuntu-репозитория."""
    root_depends = find_package(
        repository_url,
        package_name,
        package_version,
    )

    def get_dependencies(name: str) -> list[str]:
        if name == package_name:
            return dependency_package_names(root_depends)

        depends = find_package_dependencies(repository_url, name)
        return dependency_package_names(depends)

    return build_dependency_graph(
        package_name,
        get_dependencies,
        max_depth,
    )


def print_graph(graph: dict[str, list[str]]) -> None:
    """Выводит граф зависимостей в терминал."""
    print("Граф зависимостей:")

    for package, dependencies in graph.items():
        if dependencies:
            print(f"{package} -> {', '.join(dependencies)}")
        else:
            print(f"{package} -> нет зависимостей")


def main() -> None:
    """Запускает построение графа зависимостей."""
    config = parse_config()

    try:
        if config.test_mode == "true":
            repository = load_test_repository(config.repository)

            if config.package not in repository:
                raise LookupError(
                    f"Пакет {config.package} отсутствует "
                    "в тестовом репозитории"
                )

            graph = build_dependency_graph(
                config.package,
                lambda name: get_test_dependencies(repository, name),
                config.max_depth,
            )
        else:
            graph = get_real_graph(
                config.repository,
                config.package,
                config.version,
                config.max_depth,
            )

    except (LookupError, URLError, OSError, ValueError) as error:
        raise SystemExit(f"Ошибка получения данных: {error}") from error

    print(f"Пакет: {config.package}")
    print(f"Версия: {config.version}")
    print(f"Максимальная глубина: {config.max_depth}")
    print_graph(graph)


if __name__ == "__main__":
    main()
