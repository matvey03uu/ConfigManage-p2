from urllib.error import URLError
from config import parse_config
from package_parser import extract_direct_dependencies
from repository import find_package


def main() -> None:
    config = parse_config()

    if config.test_mode == "true":
        raise SystemExit(
            "Для этапа 2 требуется URL APT-репозитория; "
            "режим тестового файла будет использоваться на этапе 3."
        )

    try:
        depends_value = find_package(
            config.repository,
            config.package,
            config.version,
        )
    except (LookupError, URLError, OSError, ValueError) as error:
        raise SystemExit(f"Ошибка получения данных: {error}") from error

    dependencies = extract_direct_dependencies(depends_value)
    print(f"Пакет: {config.package}")
    print(f"Версия: {config.version}")
    print("Прямые зависимости:")

    if not dependencies:
        print("  Нет зависимостей, указанных в поле Depends.")
        return

    for number, dependency in enumerate(dependencies, start=1):
        print(f"  {number}. {dependency}")


if __name__ == "__main__":
    main()
