"""Helpers to extract id-like values from nested dict/list structures.

Functions:
 - extract_ids(data, key_names=("id",), pattern=None) -> List[(path, value)]
 - get_all_ids(data, key_names=("id",), pattern=None) -> List[value]
 - get_unique_ids(...)

Paths are returned as dotted strings; list indices are represented as [i].
"""
from __future__ import annotations

from typing import Any, Iterable, List, Optional, Sequence, Tuple
import re


def extract_ids(
    data: Any,
    key_names: Sequence[str] = ("id",),
    pattern: Optional[str] = None,
) -> List[Tuple[str, Any]]:
    """Recursively traverse ``data`` (dict/list) and return a list of
    (path, value) for entries whose key matches one of ``key_names``.

    - path is a dotted string (list indices show as [i]).
    - If ``pattern`` is provided it's treated as a regular expression and
      only matching values (stringified) are returned.

    Examples:
        >>> data = {"a": {"id": 1}, "items": [{"id": "x"}, {"id": "y"}]}
        >>> extract_ids(data)
        [("a.id", 1), ("items.[0].id", "x"), ("items.[1].id", "y")]
    """
    regex = re.compile(pattern) if pattern else None
    key_set = set(key_names)
    found: List[Tuple[str, Any]] = []

    def _traverse(obj: Any, path: List[str]) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                next_path = path + [str(k)]
                if k in key_set:
                    sval = v if not isinstance(v, (dict, list)) else v
                    # stringify for regex matching
                    sval_str = str(sval)
                    if regex is None or regex.search(sval_str):
                        found.append((".".join(next_path), v))
                # always traverse into value to find nested ids
                _traverse(v, next_path)

        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                next_path = path + [f"[{i}]"]
                _traverse(item, next_path)

        # primitives (str/int/float/bool/None) have no children

    _traverse(data, [])
    return found


def get_all_ids(data: Any, key_names: Sequence[str] = ("id",), pattern: Optional[str] = None) -> List[Any]:
    """Return only the values (not paths) discovered by ``extract_ids``."""
    return [v for (_p, v) in extract_ids(data, key_names=key_names, pattern=pattern)]


def get_unique_ids(data: Any, key_names: Sequence[str] = ("id",), pattern: Optional[str] = None) -> List[Any]:
    """Return unique values in discovered order."""
    seen = set()
    uniques: List[Any] = []
    for v in get_all_ids(data, key_names=key_names, pattern=pattern):
        if v not in seen:
            seen.add(v)
            uniques.append(v)
    return uniques
