"""Morphological feature extraction via regionprops."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from skimage.measure import regionprops_table

from backend.utils.serialization import sanitize_row


def relabel_sequential(masks: np.ndarray) -> np.ndarray:
    output = np.zeros_like(masks)
    new_id = 1
    for old_id in np.unique(masks):
        if old_id == 0:
            continue
        output[masks == old_id] = new_id
        new_id += 1
    return output


def compute_circularity(area: float, perimeter: float) -> float | None:
    if perimeter <= 0 or area <= 0:
        return None
    value = 4 * math.pi * area / (perimeter ** 2)
    return min(value, 1.0)


def extract_features(
    masks: np.ndarray, intensity_image: np.ndarray
) -> list[dict[str, Any]]:
    if masks.max() == 0:
        return []

    props = regionprops_table(
        masks,
        intensity_image=intensity_image,
        properties=(
            "label",
            "area",
            "perimeter",
            "eccentricity",
            "solidity",
            "extent",
            "major_axis_length",
            "minor_axis_length",
            "mean_intensity",
            "min_intensity",
            "max_intensity",
            "centroid",
        ),
    )

    cells: list[dict[str, Any]] = []
    for idx in range(len(props["label"])):
        area = float(props["area"][idx])
        perimeter = float(props["perimeter"][idx])
        circularity = compute_circularity(area, perimeter)
        centroid_y = float(props["centroid-0"][idx])
        centroid_x = float(props["centroid-1"][idx])
        row = {
            "cell_id": int(props["label"][idx]),
            "area": area,
            "perimeter": perimeter,
            "circularity": circularity,
            "eccentricity": float(props["eccentricity"][idx]),
            "solidity": float(props["solidity"][idx]),
            "extent": float(props["extent"][idx]),
            "major_axis_length": float(props["major_axis_length"][idx]),
            "minor_axis_length": float(props["minor_axis_length"][idx]),
            "mean_intensity": float(props["mean_intensity"][idx]),
            "min_intensity": float(props["min_intensity"][idx]),
            "max_intensity": float(props["max_intensity"][idx]),
            "centroid_x": centroid_x,
            "centroid_y": centroid_y,
        }
        cells.append(sanitize_row(row))
    return cells


def compute_summary_metrics(cells: list[dict[str, Any]], image_shape: tuple[int, int]) -> dict[str, Any]:
    if not cells:
        return {
            "cell_count": 0,
            "mean_area": 0,
            "median_area": 0,
            "mean_circularity": 0,
            "mean_intensity": 0,
            "mean_perimeter": 0,
            "mean_eccentricity": 0,
            "cell_density": 0,
        }

    areas = [c["area"] for c in cells if c.get("area")]
    circularities = [c["circularity"] for c in cells if c.get("circularity")]
    intensities = [c["mean_intensity"] for c in cells if c.get("mean_intensity")]
    perimeters = [c["perimeter"] for c in cells if c.get("perimeter")]
    eccentricities = [c["eccentricity"] for c in cells if c.get("eccentricity")]

    height, width = image_shape
    pixel_area = max(1, height * width)

    return {
        "cell_count": len(cells),
        "mean_area": float(np.mean(areas)) if areas else 0,
        "median_area": float(np.median(areas)) if areas else 0,
        "mean_circularity": float(np.mean(circularities)) if circularities else 0,
        "mean_intensity": float(np.mean(intensities)) if intensities else 0,
        "mean_perimeter": float(np.mean(perimeters)) if perimeters else 0,
        "mean_eccentricity": float(np.mean(eccentricities)) if eccentricities else 0,
        "cell_density": len(cells) / pixel_area * 1e6,
    }
