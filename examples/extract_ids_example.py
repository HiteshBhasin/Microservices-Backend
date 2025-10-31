"""Small example showing how to use utils.extract_ids."""
import os
import sys

# Ensure the repository root is on sys.path so `utils` is importable when running
# this example from the examples/ directory.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from utils.extract_ids import extract_ids, get_all_ids, get_unique_ids


SAMPLE = {
    "tenants": [
        {"id": 101, "name": "Alice", "meta": {"id": "m-1"}},
        {"id": 102, "name": "Bob", "meta": {"id": "m-2"}},
    ],
    "properties": {
        "count": 2,
        "items": [
            {"id": "prop-1", "address": "1 Main St"},
            {"id": "prop-2", "address": "2 Main St"},
        ],
    },
}


def main():
    print("All (path, value) matches:")
    for p, v in extract_ids(SAMPLE):
        print(p, "=>", v)

    print("\nAll values:")
    print(get_all_ids(SAMPLE))

    print("\nUnique values:")
    print(get_unique_ids(SAMPLE))


if __name__ == "__main__":
    main()
