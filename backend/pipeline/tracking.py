"""Simple centroid-based tracking for time-lapse sequences."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.optimize import linear_sum_assignment


def track_centroids(frame_cells: list[list[dict[str, Any]]]) -> dict[str, Any]:
    """Associate cells across frames using Hungarian matching on centroids."""
    if not frame_cells:
        return {"tracks": [], "metrics": {}}

    tracks: list[dict[str, Any]] = []
    active: dict[int, dict[str, Any]] = {}
    next_track_id = 1
    max_distance = 40.0

    for frame_idx, cells in enumerate(frame_cells):
        centroids = [
            (c["cell_id"], c["centroid_x"], c["centroid_y"], c.get("area", 0))
            for c in cells
        ]
        if frame_idx == 0:
            for cell_id, cx, cy, area in centroids:
                active[cell_id] = {
                    "track_id": next_track_id,
                    "points": [(frame_idx, cx, cy, area)],
                }
                next_track_id += 1
            continue

        prev_items = list(active.items())
        if not prev_items or not centroids:
            for cell_id, cx, cy, area in centroids:
                active[cell_id] = {
                    "track_id": next_track_id,
                    "points": [(frame_idx, cx, cy, area)],
                }
                next_track_id += 1
            continue

        cost = np.zeros((len(prev_items), len(centroids)))
        for i, (_, state) in enumerate(prev_items):
            _, px, py, _ = state["points"][-1]
            for j, (_, cx, cy, _) in enumerate(centroids):
                cost[i, j] = np.hypot(cx - px, cy - py)

        row_idx, col_idx = linear_sum_assignment(cost)
        matched_prev = set()
        matched_curr = set()
        new_active: dict[int, dict[str, Any]] = {}

        for r, c in zip(row_idx, col_idx):
            if cost[r, c] > max_distance:
                continue
            prev_cell_id, state = prev_items[r]
            curr_cell_id, cx, cy, area = centroids[c]
            state["points"].append((frame_idx, cx, cy, area))
            new_active[curr_cell_id] = state
            matched_prev.add(r)
            matched_curr.add(c)

        for j, (cell_id, cx, cy, area) in enumerate(centroids):
            if j not in matched_curr:
                new_active[cell_id] = {
                    "track_id": next_track_id,
                    "points": [(frame_idx, cx, cy, area)],
                }
                next_track_id += 1

        active = new_active

    for state in active.values():
        points = state["points"]
        displacements = []
        speeds = []
        area_changes = []
        for i in range(1, len(points)):
            f0, x0, y0, a0 = points[i - 1]
            f1, x1, y1, a1 = points[i]
            dt = max(1, f1 - f0)
            disp = float(np.hypot(x1 - x0, y1 - y0))
            displacements.append(disp)
            speeds.append(disp / dt)
            if a0:
                area_changes.append((a1 - a0) / a0)
        tracks.append(
            {
                "track_id": state["track_id"],
                "points": [
                    {"frame": p[0], "x": p[1], "y": p[2], "area": p[3]} for p in points
                ],
                "total_displacement": float(sum(displacements)),
                "mean_speed": float(np.mean(speeds)) if speeds else 0.0,
                "max_displacement": float(max(displacements)) if displacements else 0.0,
                "mean_area_change": float(np.mean(area_changes)) if area_changes else 0.0,
            }
        )

    metrics = {
        "tracked_cells": len(tracks),
        "average_displacement": float(
            np.mean([t["total_displacement"] for t in tracks]) if tracks else 0
        ),
        "mean_speed": float(np.mean([t["mean_speed"] for t in tracks]) if tracks else 0),
        "maximum_displacement": float(
            max([t["max_displacement"] for t in tracks], default=0)
        ),
        "average_area_change": float(
            np.mean([t["mean_area_change"] for t in tracks]) if tracks else 0
        ),
    }
    return {"tracks": tracks, "metrics": metrics}
