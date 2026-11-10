from config import parse_config


def main() -> None:
    config = parse_config()
    print(f"package: {config.package}")
    print(f"repository: {config.repository}")
    print(f"test_mode: {config.test_mode}")
    print(f"version: {config.version}")
    print(f"output: {config.output}")
    print(f"max_depth: {config.max_depth}")


if __name__ == "__main__":
    main()
