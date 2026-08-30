"""I-09 Isolation Forest: supplementary anomaly evidence, NOT collapse prediction.

Consumes the flattened, already-validated feature dict returned by
intelligence.features.extract_features(). Reads tuning from
intelligence.config.PROTOTYPE_ANOMALY_TUNING.

Hard boundary (see intelligence/orchestrator.py for how this is enforced): this
module's output may only ever ADD the existing SENSOR_ANOMALY reason code to a
decision. It never computes Risk, Confidence, selects a state, or determines a
safety action on its own -- score_anomaly() returns a small evidence dict with no
"risk"/"confidence"/"state"/"action" key of any kind.

Isolation Forest scores "how statistically unusual is this reading compared to the
baseline it was trained on" -- nothing here claims to predict collapse, roof-fall, or
any future event. train() is entirely optional: the deterministic pipeline (I-02
through I-08) runs correctly whether or not this module is ever imported. If a model
fails to train or is not supplied, score_anomaly(features, bundle=None) returns a
safe, non-anomalous default and never raises.
"""

from __future__ import annotations

import random

import numpy as np
from sklearn.ensemble import IsolationForest

from intelligence import config


def generate_synthetic_baseline(n: int = 200, seed: int = 42) -> list[dict]:
    """Deterministic synthetic "normal" readings for training/testing only.

    Centred on contracts/examples/sensor-reading.normal.json's own values, with small
    Gaussian jitter. Fixed seed per docs/CODING_STANDARDS.md: "Fix random seeds in
    repeatable tests and synthetic-data generation." This is NOT real sensor data.
    """
    rng = random.Random(seed)
    return [
        {
            "tilt_x_deg": rng.gauss(0.4, 0.05),
            "tilt_y_deg": rng.gauss(0.2, 0.05),
            "vibration_g": max(0.0, rng.gauss(0.08, 0.02)),
            "displacement_mm": max(0.0, rng.gauss(1.2, 0.1)),
        }
        for _ in range(n)
    ]


def _feature_matrix(rows: list) -> list:
    return [[row[name] for name in config.SENSOR_FEATURES] for row in rows]


def train(
    baseline_features: list,
    tuning: config.PrototypeAnomalyTuning = config.PROTOTYPE_ANOMALY_TUNING,
) -> dict:
    """Fit an IsolationForest on baseline (normal) feature dicts.

    Returns a bundle {"model", "clip_low", "clip_high"}: the 0-1 rescaling range is
    calibrated from a held-out slice of the baseline (see config.py's tuning
    docstring for why in-sample calibration would be misleading).
    """
    if len(baseline_features) < tuning.min_baseline_rows:
        raise ValueError(
            f"train() needs at least {tuning.min_baseline_rows} baseline readings, "
            f"got {len(baseline_features)}"
        )

    X = _feature_matrix(baseline_features)
    split = int(len(X) * (1 - tuning.calibration_holdout_fraction))
    X_fit, X_calib = X[:split], X[split:]
    if len(X_calib) < tuning.min_calibration_rows or len(X_fit) < tuning.min_calibration_rows:
        X_fit = X_calib = X  # baseline too small to hold out a slice; fall back in-sample

    model = IsolationForest(
        n_estimators=tuning.n_estimators,
        contamination=tuning.contamination,
        random_state=tuning.random_state,
    )
    model.fit(X_fit)

    calib_scores = model.decision_function(X_calib)
    high = float(np.percentile(calib_scores, tuning.calib_high_percentile))
    low_pct = float(np.percentile(calib_scores, tuning.calib_low_percentile))
    spread = float(np.std(calib_scores)) or 1e-3
    low = low_pct - tuning.calib_low_margin_stds * spread
    if low >= high:
        low = high - 1e-3

    return {"model": model, "clip_low": low, "clip_high": high}


def score_anomaly(
    features: dict,
    bundle: dict | None,
    tuning: config.PrototypeAnomalyTuning = config.PROTOTYPE_ANOMALY_TUNING,
) -> dict:
    """Score one reading's statistical unusualness. Never raises, never blocks the pipeline.

    Args:
        bundle: train()'s return value, or None to mean "ML disabled" -- returns a
            safe, non-anomalous default in that case.

    Returns:
        {"anomalous": bool, "anomaly_score": float 0-1, "ml_enabled": bool}
        No "risk", "confidence", "state" or "action" key exists here by design.
    """
    if bundle is None:
        return {"anomalous": False, "anomaly_score": 0.0, "ml_enabled": False}

    row = [[features[name] for name in config.SENSOR_FEATURES]]
    raw = bundle["model"].decision_function(row)[0]
    low, high = bundle["clip_low"], bundle["clip_high"]
    clipped = max(low, min(high, raw))
    normalized = 1.0 - (clipped - low) / (high - low)
    anomaly_score = max(0.0, min(1.0, normalized))

    return {
        "anomalous": anomaly_score >= tuning.anomalous_threshold,
        "anomaly_score": round(anomaly_score, 4),
        "ml_enabled": True,
    }
