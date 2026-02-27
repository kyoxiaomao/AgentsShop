import argparse

from .service import build_ui_snapshot


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.parse_args()
    build_ui_snapshot()


if __name__ == "__main__":
    main()
