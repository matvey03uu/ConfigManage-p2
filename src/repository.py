from gzip import GzipFile
from io import BytesIO
from urllib.error import HTTPError
from urllib.request import Request, urlopen

UBUNTU_RELEASE = "noble"
ARCHITECTURE = "amd64"
COMPONENTS = ("main", "universe", "restricted", "multiverse")
REQUEST_TIMEOUT = 30
HTTP_NOT_FOUND = 404


def download_package_index(
    repository_url: str,
    component: str,
    release: str = UBUNTU_RELEASE,
    architecture: str = ARCHITECTURE,
) -> bytes:
    base_url = repository_url.rstrip("/")
    index_url = (
        f"{base_url}/dists/{release}/{component}/"
        f"binary-{architecture}/Packages.gz"
    )
    request = Request(
        index_url,
        headers={"User-Agent": "Config-p2 dependency viewer"},
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        compressed_data = response.read()
    with GzipFile(fileobj=BytesIO(compressed_data)) as archive:
        return archive.read()


def parse_package_paragraph(paragraph: str) -> dict[str, str]:
    """Разбирает один блок информации о пакете."""
    fields = {}
    current_field = None

    for line in paragraph.splitlines():
        if line.startswith((" ", "\t")) and current_field:
            fields[current_field] += " " + line.strip()
        elif ": " in line:
            current_field, value = line.split(": ", 1)
            fields[current_field] = value

    return fields


def find_dependencies_in_index(
    index_data: bytes,
    package_name: str,
    package_version: str,
) -> str | None:
    """Ищет зависимости нужной версии пакета в индексе."""
    text = index_data.decode("utf-8", errors="replace")

    for paragraph in text.split("\n\n"):
        fields = parse_package_paragraph(paragraph)

        if fields.get("Package") != package_name:
            continue

        if fields.get("Version") != package_version:
            continue

        return fields.get("Depends", "")

    return None


def find_any_package_dependencies_in_index(
    index_data: bytes,
    package_name: str,
) -> str | None:
    """Ищет пакет по имени без ограничения версии."""
    text = index_data.decode("utf-8", errors="replace")

    for paragraph in text.split("\n\n"):
        fields = parse_package_paragraph(paragraph)

        if fields.get("Package") == package_name:
            return fields.get("Depends", "")

    return None


def find_package(
    repository_url: str,
    package_name: str,
    package_version: str,
) -> str:
    """Находит пакет заданной версии и возвращает его зависимости."""
    for component in COMPONENTS:
        try:
            index_data = download_package_index(repository_url, component)
        except HTTPError as error:
            if error.code == HTTP_NOT_FOUND:
                continue
            raise

        dependencies = find_dependencies_in_index(
            index_data,
            package_name,
            package_version,
        )

        if dependencies is not None:
            return dependencies

    raise LookupError(
        f"Пакет {package_name} версии {package_version} "
        "не найден в индексах выбранного репозитория"
    )


def find_package_dependencies(
    repository_url: str,
    package_name: str,
) -> str:
    """Получает зависимости пакета без ограничения его версии."""
    for component in COMPONENTS:
        try:
            index_data = download_package_index(repository_url, component)
        except HTTPError as error:
            if error.code == HTTP_NOT_FOUND:
                continue
            raise

        dependencies = find_any_package_dependencies_in_index(
            index_data,
            package_name,
        )

        if dependencies is not None:
            return dependencies

    raise LookupError(f"Пакет {package_name} не найден в репозитории")
