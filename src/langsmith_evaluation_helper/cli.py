# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

import os
import subprocess
import sys


def evaluate(config_path: str) -> None:
    # Determine the absolute path of loader.py within the package
    package_dir = os.path.dirname(os.path.realpath(__file__))
    loader_path = os.path.join(package_dir, "loader.py")

    if not os.path.isfile(loader_path):
        print(f"Error: loader.py not found at {loader_path}")
        sys.exit(1)

    subprocess.run([sys.executable, loader_path, config_path])


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: langsmith-evaluation-helper evaluate /path/to/config")
        sys.exit(1)

    command = sys.argv[1]

    if command == "evaluate":
        if len(sys.argv) != 3:
            print("Usage: langsmith-evaluation-helper evaluate /path/to/config")
            sys.exit(1)
        config_path = sys.argv[2]
        evaluate(config_path)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
