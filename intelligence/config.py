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

#: Recommended actions per state, taken verbatim from docs/PROJECT_MASTER.md's
#: "State behaviour" table (not invented here; only centralized so it is not
#: retyped independently by each future module).
STATE_ACTIONS: MappingProxyType[str, tuple[str, ...]] = MappingProxyType(
    {
        "NORMAL": ("BASELINE_LOGGING",),
        "WATCH": ("INCREASE_MONITORING",),
        "WARNING": ("HIGH_RATE_MONITORING", "CREATE_INCIDENT"),
        "CRITICAL": (
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
