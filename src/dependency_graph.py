from collections.abc import Callable

ROOT_DEPTH = 0
MIN_DEPTH = 0


def process_queue(
    queue: list[tuple[str, int]],
    position: int,
    visited: set[str],
    graph: dict[str, list[str]],
    max_depth: int,
    get_dependencies: Callable[[str], list[str]],
) -> None:
    """Рекурсивно обрабатывает очередь пакетов в порядке BFS."""
    if position >= len(queue):
        return

    package_name, depth = queue[position]

    if package_name in visited:
        process_queue(
            queue, position + 1, visited, graph, max_depth, get_dependencies
        )
        return

    visited.add(package_name)

    if depth < max_depth:
        dependencies = get_dependencies(package_name)
    else:
        dependencies = []

    graph[package_name] = dependencies

    for dependency in dependencies:
        if dependency not in visited:
            queue.append((dependency, depth + 1))

    process_queue(
        queue, position + 1, visited, graph, max_depth, get_dependencies
    )


def build_dependency_graph(
    root_package: str,
    get_dependencies: Callable[[str], list[str]],
    max_depth: int,
) -> dict[str, list[str]]:
    """Строит граф зависимостей обходом BFS с рекурсией."""
    if max_depth < MIN_DEPTH:
        raise ValueError("Максимальная глубина не может быть отрицательной")

    graph = {}
    queue = [(root_package, ROOT_DEPTH)]
    visited = set()

    process_queue(
        queue,
        ROOT_DEPTH,
        visited,
        graph,
        max_depth,
        get_dependencies,
    )

    return graph