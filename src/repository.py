from gzip import GzipFile
from io import BytesIO
from urllib.error import HTTPError
from urllib.request import Request, urlopen

UBUNTU_RELEASE = "noble"
ARCHITECTURE = "amd64"
COMPONENTS = ("main", "universe", "restricted", "multiverse")
REQUEST_TIMEOUT = 30


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


def find_package(
    repository_url: str,
    package_name: str,
    package_version: str,
) -> str:
    for component in COMPONENTS:
        try:
            index_data = download_package_index(repository_url, component)
        except HTTPError as error:
            if error.code == 404:
                continue
            raise
        text = index_data.decode("utf-8", errors="replace")
        for paragraph in text.split("\n\n"):
            fields = {}
            current_field = None
            for line in paragraph.splitlines():
                if line.startswith((" ", "\t")) and current_field:
                    fields[current_field] += " " + line.strip()
                elif ": " in line:
                    current_field, value = line.split(": ", 1)
                    fields[current_field] = value
            if (
                fields.get("Package") == package_name
                and fields.get("Version") == package_version
            ):
                return fields.get("Depends", "")
    raise LookupError(
        f"Пакет {package_name} версии {package_version} "
        "не найден в индексах выбранного репозитория"
    )
