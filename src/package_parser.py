import re

DEPENDENCY_NAME = re.compile(r"^\s*([a-z0-9][a-z0-9+.-]*)", re.IGNORECASE)


def split_dependency_groups(value: str) -> list[str]:
    groups = []
    current = []
    parentheses_depth = 0

    for character in value:
        if character == "(":
            parentheses_depth += 1
        elif character == ")":
            parentheses_depth = max(0, parentheses_depth - 1)

        if character == "," and parentheses_depth == 0:
            group = "".join(current).strip()
            if group:
                groups.append(group)
            current = []
        else:
            current.append(character)

    final_group = "".join(current).strip()
    if final_group:
        groups.append(final_group)
    return groups


def extract_direct_dependencies(depends_value: str) -> list[str]:
    return split_dependency_groups(depends_value)


def dependency_package_names(depends_value: str) -> list[str]:
    names = []
    for group in split_dependency_groups(depends_value):
        for alternative in group.split("|"):
            match = DEPENDENCY_NAME.match(alternative)
            if match:
                names.append(match.group(1))
    return names
