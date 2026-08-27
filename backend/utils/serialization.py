"""JSON-safe serialization helpers."""

from __future__ import annotations

import math
from typing import Any


def sanitize_float(value: float | int | None) -> float | None:
    if value is None:
        return None
    try:
        num = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(num) or math.isinf(num):
        return None
    return num


def sanitize_row(row: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, (int, str, bool)) or value is None:
            cleaned[key] = value
        elif isinstance(value, float):
            cleaned[key] = sanitize_float(value)
        elif isinstance(value, (list, tuple)) and len(value) == 2:
            cleaned[key] = [sanitize_float(value[0]), sanitize_float(value[1])]
        else:
            cleaned[key] = value
    return cleaned
