import math

from backend.pipeline.features import compute_circularity, extract_features
from backend.pipeline.preprocessing import PreprocessConfig, preprocess_image
import numpy as np


def test_circularity_handles_zero_perimeter():
    assert compute_circularity(100, 0) is None


def test_circularity_valid():
    value = compute_circularity(100, 40)
    assert value is not None
    assert 0 < value <= 1


def test_preprocess_runs():
    gray = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
    result = preprocess_image(gray, PreprocessConfig())
    assert result.preprocessed.shape == gray.shape
    assert len(result.steps) > 0


def test_extract_features_from_labels():
    masks = np.zeros((64, 64), dtype=np.int32)
    masks[10:20, 10:20] = 1
    masks[30:45, 30:45] = 2
    intensity = np.full((64, 64), 120, dtype=np.uint8)
    cells = extract_features(masks, intensity)
    assert len(cells) == 2
    assert all(c["area"] > 0 for c in cells)


def test_sanitize_no_nan_in_cells():
    masks = np.zeros((32, 32), dtype=np.int32)
    masks[5:15, 5:15] = 1
    intensity = np.full((32, 32), 100, dtype=np.uint8)
    cells = extract_features(masks, intensity)
    for cell in cells:
        for key, value in cell.items():
            if isinstance(value, float):
                assert not math.isnan(value)
