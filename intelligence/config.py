"""Central Intelligence configuration.

This is the one authoritative place Risk, Confidence and state/scoring parameters live
for the Agentic AI + ML/LLM workstream, so future modules (risk.py, confidence.py,
decision.py, trend.py, geometry.py, ...) read from here instead of duplicating names or
numbers per file.

This module contains NO logic:
    - no ML, no Isolation Forest
    - no Risk calculation
    - no Confidence calculation
    - no state-selection function
    - no LLM
    - no hardware/network code
Only names, enums and immutable constants.

IMPORTANT -- numeric thresholds below are explicitly PROTOTYPE / SYNTHETIC / TEST-ONLY.
The project does not yet have validated industrial mine-safety data. Every numeric value
here exists only to let future modules be written and tested end-to-end; none of them may
be described as a safe mine limit, collapse threshold, roof-fall threshold or certified
warning threshold. Replace them once real calibration/geotechnical data is available.

Sources cross-checked before writing this file: contracts/sensor-reading.schema.json,
contracts/decision.schema.json, docs/PROJECT_MASTER.md ("State behaviour" table and
"Threshold values are provisional and must be recorded in the intelligence configuration"
rule), docs/workstreams/intelligence.md.

Threshold calibration note: the sensor thresholds below were revised from an initial
arbitrary round-number draft to align with the ranges the shared simulator and Full
Stack prototype actually demonstrate (normal/warning/critical bands supplied by
integration review). They are still demonstration/synthetic calibration values, not
validated mine-safety limits -- see PROTOTYPE_STATUS.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import NamedTuple

# ---------------------------------------------------------------------------
# Frozen contract vocabulary -- mirrors contracts/*.schema.json exactly.
# No numbers in this section; just centrally-named strings so no module has to
# retype/misspell an enum value that already exists in the schemas.
# ---------------------------------------------------------------------------

#: The four frozen v1 ground-instability sensor features (contracts/sensor-reading.schema.json).
SENSOR_FEATURES: tuple[str, ...] = (
    "tilt_x_deg",
    "tilt_y_deg",
    "vibration_g",
    "displacement_mm",
)

#: The three frozen v1 sensor-health flags (contracts/sensor-reading.schema.json).
HEALTH_FLAGS: tuple[str, ...] = (
    "mpu6050_ok",
    "displacement_input_ok",
    "connection_ok",
)

#: Allowed node identities (both schemas).
NODE_IDS: tuple[str, ...] = ("NODE_A", "NODE_B")

#: Decision schema_version this configuration targets (contracts/decision.schema.json).
DECISION_SCHEMA_VERSION = "1.0"

#: Supervisory states (contracts/decision.schema.json "state" enum).
STATES: tuple[str, ...] = ("NORMAL", "WATCH", "WARNING", "CRITICAL")

#: Trend labels (contracts/decision.schema.json "trend" enum).
TRENDS: tuple[str, ...] = ("STABLE", "RISING", "FALLING", "INSUFFICIENT_DATA")

#: Deterministic reason codes (contracts/decision.schema.json "reason_codes" enum).
REASON_CODES: tuple[str, ...] = (
    "SENSOR_ANOMALY",
    "DISPLACEMENT_RISING",
    "TILT_CHANGE",
    "VIBRATION_SPIKE",
    "NEIGHBOUR_CORRELATION",
    "NEAR_ACTIVE_FACE",
    "PERSISTENT_EVENT",
    "LOW_SENSOR_HEALTH",
    "MISSING_DATA",
)

#: Supervisory actions (contracts/decision.schema.json "actions" enum).
ACTIONS: tuple[str, ...] = (
    "BASELINE_LOGGING",
    "INCREASE_MONITORING",
    "HIGH_RATE_MONITORING",
    "CREATE_INCIDENT",
    "SAFETY_RECOMMENDATION",
    "ACTIVATE_BUZZER",
    "DISPATCH_INSPECTION",
)

#: Recommended actions per state, taken from docs/PROJECT_MASTER.md's "State
#: behaviour" table and aligned with the already-shipped Full Stack fallback
#: adapter (apps/api/decision.py) so replacing the fallback doesn't change what
#: actions a CRITICAL reading recommends -- CRITICAL keeps HIGH_RATE_MONITORING
#: in addition to the safety-specific actions, matching that prior behaviour.
STATE_ACTIONS: MappingProxyType[str, tuple[str, ...]] = MappingProxyType(
    {
        "NORMAL": ("BASELINE_LOGGING",),
        "WATCH": ("INCREASE_MONITORING",),
        "WARNING": ("HIGH_RATE_MONITORING", "CREATE_INCIDENT"),
        "CRITICAL": (
            "HIGH_RATE_MONITORING",
            "SAFETY_RECOMMENDATION",
            "CREATE_INCIDENT",
            "ACTIVATE_BUZZER",
            "DISPATCH_INSPECTION",
        ),
    }
)

# ---------------------------------------------------------------------------
# PROTOTYPE / SYNTHETIC / TEST-ONLY numeric configuration.
#
# Every value below is a round, arbitrarily-chosen development number, NOT derived
# from the contract example packets, NOT derived from the abnormal-candidate fixture,
# and NOT derived from any physical or geotechnical model. See module docstring.
# ---------------------------------------------------------------------------

#: Label every prototype numeric value below must carry. Tests assert this string
#: is present so the "not a safety threshold" status is explicit, not just prose.
PROTOTYPE_STATUS = "PROTOTYPE / SYNTHETIC / TEST-ONLY"


class SensorThresholdSet(NamedTuple):
    """One sensor feature's development watch/warning/critical tiers.

    NOT a validated safety limit -- see `status`. Values only need to be ordered
    watch < warning < critical so future state logic has something monotonic to
    exercise in tests; the specific numbers carry no physical meaning yet.
    """

    watch: float
    warning: float
    critical: float
    unit: str
    status: str = PROTOTYPE_STATUS


#: Calibrated to align with the ranges the shared simulator and Full Stack prototype
#: currently demonstrate for each state (per integration review, 2026-08-30):
#:   displacement -- normal ~1.0-1.2mm, warning ~2.8-3.2mm, critical ~6.8-7.4mm
#:   tilt         -- warning ~2.1-2.3deg, critical ~4.9-5.8deg
#:   vibration    -- warning ~0.27-0.30g, critical ~0.62-0.75g
#: An earlier draft used arbitrary round numbers (3/8/20 deg, 8/20/60mm) that were
#: NOT calibrated against the demo and would have kept the shared Critical scenario
#: below WATCH for displacement. tilt_x/tilt_y still share the same tiers because the
#: schema treats both axes identically (no documented reason to weight one differently).
#: Still demonstration/synthetic calibration, not a validated mine-safety limit.
PROTOTYPE_SENSOR_THRESHOLDS: MappingProxyType[str, SensorThresholdSet] = MappingProxyType(
    {
        "tilt_x_deg": SensorThresholdSet(watch=1.5, warning=2.0, critical=4.0, unit="deg"),
        "tilt_y_deg": SensorThresholdSet(watch=1.5, warning=2.0, critical=4.0, unit="deg"),
        "vibration_g": SensorThresholdSet(watch=0.15, warning=0.25, critical=0.55, unit="g"),
        "displacement_mm": SensorThresholdSet(watch=2.0, warning=3.0, critical=6.0, unit="mm"),
    }
)


class ConfidenceWeight(NamedTuple):
    """One health flag's development contribution toward a future confidence score.

    NOT a validated weighting -- see `status`.
    """

    points: float
    status: str = PROTOTYPE_STATUS


#: Equal three-way split of a 0-100 confidence scale (100 / 3 each). Chosen only
#: because there is no evidence yet that any one health flag matters more than
#: another; replace with a justified weighting once available.
PROTOTYPE_CONFIDENCE_WEIGHTS: MappingProxyType[str, ConfidenceWeight] = MappingProxyType(
    {
        "mpu6050_ok": ConfidenceWeight(points=100.0 / 3),
        "displacement_input_ok": ConfidenceWeight(points=100.0 / 3),
        "connection_ok": ConfidenceWeight(points=100.0 / 3),
    }
)


# ---------------------------------------------------------------------------
# Named profile indirection.
#
# Risk/Confidence/state modules should import ACTIVE_PROFILE (or its fields) rather
# than the module-level PROTOTYPE_* constants directly, so a future calibrated or
# industrial profile can be swapped in later by changing ACTIVE_PROFILE here -- not
# by editing risk.py/confidence.py/decision.py.
# ---------------------------------------------------------------------------


class IntelligenceProfile(NamedTuple):
    """One named, swappable bundle of sensor thresholds and confidence weights."""

    name: str
    status: str
    sensor_thresholds: MappingProxyType[str, SensorThresholdSet]
    confidence_weights: MappingProxyType[str, ConfidenceWeight]


#: The only profile that exists today. References the same PROTOTYPE_* objects above
#: (no copying), so there is exactly one source for each number.
PROTOTYPE_PROFILE = IntelligenceProfile(
    name="prototype-synthetic-v1",
    status=PROTOTYPE_STATUS,
    sensor_thresholds=PROTOTYPE_SENSOR_THRESHOLDS,
    confidence_weights=PROTOTYPE_CONFIDENCE_WEIGHTS,
)

#: The profile future Intelligence modules should read. Swapping to a calibrated or
#: industrial profile later means changing this one line, not any consuming module.
ACTIVE_PROFILE: IntelligenceProfile = PROTOTYPE_PROFILE


# ---------------------------------------------------------------------------
# Risk-score scale anchors (I-03).
#
# The 0-100 per-feature Risk scale is a transparent piecewise-linear mapping through
# these five calibration points: physical zero -> 0, the profile's WATCH threshold ->
# 25, WARNING -> 50, CRITICAL -> 80, and one more WATCH-WARNING-sized band above
# CRITICAL -> 100 (capped beyond that). These are scale anchors, not sensor thresholds
# -- they apply identically to every feature regardless of its physical units -- so
# they live here once instead of being retyped as 25/50/80/100 in risk.py, trend.py
# and any later module that needs to reason about the same 0-100 scale.
# ---------------------------------------------------------------------------

RISK_SCALE_ANCHORS: MappingProxyType[str, float] = MappingProxyType(
    {
        "physical_zero": 0.0,
        "watch": 25.0,
        "warning": 50.0,
        "critical": 80.0,
        "cap": 100.0,
    }
)


# ---------------------------------------------------------------------------
# Confidence evidence-gap penalty (I-04).
#
# Confidence is built primarily from the three health flags (PROTOTYPE_CONFIDENCE_
# WEIGHTS above). This penalty is the second Confidence input the checkpoint calls
# for: "missing/delayed evidence". A caller (a future temporal/orchestration module)
# marks a reading as stale/gapped; this many points are deducted, floored at 0. Not
# derived from Risk in any way -- Confidence must never be derived from Risk.
# ---------------------------------------------------------------------------


class StaleEvidencePenalty(NamedTuple):
    """Points deducted from Confidence when a reading is flagged as stale/delayed.

    NOT a validated weighting -- see `status`.
    """

    points: float
    status: str = PROTOTYPE_STATUS


#: Round number: roughly one health flag's worth of weight (100/3 ~= 33), chosen so a
#: single stale reading meaningfully lowers Confidence without being able to swing an
#: otherwise fully-healthy reading below the halfway point on its own.
PROTOTYPE_STALE_EVIDENCE_PENALTY = StaleEvidencePenalty(points=30.0)


# ---------------------------------------------------------------------------
# Temporal evidence tuning (I-05).
# ---------------------------------------------------------------------------


class PrototypeTrendTuning(NamedTuple):
    """Tuning for the deterministic trend/persistence evaluator.

    NOT a validated calibration -- see `status`.
    """

    min_points_for_trend: int
    flat_slope_per_step: float
    persistent_min_streak: int
    status: str = PROTOTYPE_STATUS


#: min_points_for_trend=3: the least a straight-line slope can mean anything from;
#: fewer than that reports INSUFFICIENT_DATA rather than guessing a direction.
#: flat_slope_per_step=3.0: a Risk-points-per-reading-step dead zone below which
#: reading-to-reading noise should not be reported as RISING/FALLING.
#: persistent_min_streak=3: consecutive readings at/above the WARNING risk anchor
#: before PERSISTENT_EVENT is raised, so one noisy spike doesn't count as persistent.
PROTOTYPE_TREND_TUNING = PrototypeTrendTuning(
    min_points_for_trend=3,
    flat_slope_per_step=3.0,
    persistent_min_streak=3,
)


# ---------------------------------------------------------------------------
# Neighbour correlation tuning (I-06).
# ---------------------------------------------------------------------------


class PrototypeCorrelationTuning(NamedTuple):
    """Tuning for Node A / Node B neighbour-correlation evaluation.

    NOT a validated calibration -- see `status`.
    """

    window_seconds: float
    min_trustworthy_confidence: float
    status: str = PROTOTYPE_STATUS


#: window_seconds=30.0: round default "nearby in time" window for two independent
#: node readings to be considered part of the same event.
#: min_trustworthy_confidence=50.0: reuses the 0-100 Confidence scale's natural
#: midpoint -- below it, a neighbour's own evidence is not trusted enough to count
#: as independent corroboration, regardless of what its Risk score says.
PROTOTYPE_CORRELATION_TUNING = PrototypeCorrelationTuning(
    window_seconds=30.0,
    min_trustworthy_confidence=50.0,
)


# ---------------------------------------------------------------------------
# State machine hysteresis (I-07).
#
# State bucket boundaries are NOT redeclared here -- they reuse RISK_SCALE_ANCHORS
# ("watch"=25, "warning"=50, "critical"=80) so there is exactly one place a reading's
# Risk score maps to a severity tier. This section only adds the anti-flapping rule:
# escalation (toward a more severe state) is immediate on any single reading, but
# de-escalation (recovery) requires `deescalation_streak` consecutive, sufficiently
# confident calmer readings before the state actually steps down.
# ---------------------------------------------------------------------------


class PrototypeStateTuning(NamedTuple):
    """Tuning for the NORMAL/WATCH/WARNING/CRITICAL state machine's hysteresis.

    NOT a validated calibration -- see `status`.
    """

    deescalation_streak: int
    status: str = PROTOTYPE_STATUS


#: deescalation_streak=3: matches the same round "three in a row" bar used for
#: PERSISTENT_EVENT detection (I-05) -- distinct mechanism, same defensible round
#: number, chosen only so a single calmer reading can never immediately erase a
#: CRITICAL/WARNING state (the classic flapping failure mode at a boundary).
#: De-escalation also requires confidence >= PROTOTYPE_CORRELATION_TUNING.
#: min_trustworthy_confidence (reused, not redeclared) -- an untrustworthy "calm"
#: reading must not count toward recovery.
PROTOTYPE_STATE_TUNING = PrototypeStateTuning(deescalation_streak=3)


# ---------------------------------------------------------------------------
# Isolation Forest tuning (I-09).
#
# Supplementary anomaly evidence only -- see intelligence/anomaly.py module docstring
# for the hard boundary: it can only ever ADD the SENSOR_ANOMALY reason code; it never
# computes Risk, Confidence, state, or an action on its own.
# ---------------------------------------------------------------------------


class PrototypeAnomalyTuning(NamedTuple):
    """Tuning for the Isolation Forest anomaly-evidence model.

    NOT a validated calibration -- see `status`.
    """

    n_estimators: int
    contamination: float
    random_state: int
    calibration_holdout_fraction: float
    min_calibration_rows: int
    min_baseline_rows: int
    calib_high_percentile: float
    calib_low_percentile: float
    calib_low_margin_stds: float
    anomalous_threshold: float
    status: str = PROTOTYPE_STATUS


#: contamination=0.01 (not "auto"): the baseline is pure normal data by construction,
#: so contamination should reflect "how many baseline points are borderline", not an
#: assumed outlier rate -- "auto" would push ~10% of the baseline itself negative.
#: calibration_holdout_fraction=0.3 / min_calibration_rows=5: the 0-1 rescaling range
#: is calibrated on a held-out slice of the baseline the model was NOT fit on, because
#: a model scores its own training points more favourably than fresh normal data
#: (isolation trees partition tightly around exactly what they saw).
#: calib_high_percentile=40 / calib_low_percentile=5 / calib_low_margin_stds=1.5:
#: "high" anchors what typical unseen-but-normal data looks like; "low" extends a
#: margin below the held-out low tail so genuinely novel readings can reach ~1.0.
#: anomalous_threshold=0.5: the midpoint of the calibrated 0-1 scale -- the simplest
#: defensible cut point until real calibration data exists.
#: min_baseline_rows=10: the least data train() will fit a model on at all.
PROTOTYPE_ANOMALY_TUNING = PrototypeAnomalyTuning(
    n_estimators=100,
    contamination=0.01,
    random_state=42,
    calibration_holdout_fraction=0.3,
    min_calibration_rows=5,
    min_baseline_rows=10,
    calib_high_percentile=40.0,
    calib_low_percentile=5.0,
    calib_low_margin_stds=1.5,
    anomalous_threshold=0.5,
)
