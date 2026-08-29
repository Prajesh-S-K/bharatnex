"""Transparent deterministic fallback until the intelligence service is integrated."""


def evaluate(packet: dict, previous: dict | None = None, neighbour: dict | None = None) -> dict:
    sensors = packet["sensors"]
    health = packet["health"]
    tilt = max(abs(sensors["tilt_x_deg"]), abs(sensors["tilt_y_deg"]))
    displacement = sensors["displacement_mm"]
    vibration = sensors["vibration_g"]
    risk = min(100.0, displacement * 10 + tilt * 8 + vibration * 35)
    reasons: list[str] = []
    if displacement >= 3:
        reasons.append("DISPLACEMENT_RISING")
    if tilt >= 2:
        reasons.append("TILT_CHANGE")
    if vibration >= 0.35:
        reasons.append("VIBRATION_SPIKE")
    if risk >= 45:
        reasons.insert(0, "SENSOR_ANOMALY")

    trend = "INSUFFICIENT_DATA"
    if previous:
        old = previous["packet"]["sensors"]["displacement_mm"]
        delta = displacement - old
        trend = "RISING" if delta > 0.3 else "FALLING" if delta < -0.3 else "STABLE"

    confidence = 88.0
    if not all(health.values()):
        confidence = 42.0
        reasons.append("LOW_SENSOR_HEALTH")
    if neighbour and neighbour["decision"]["risk"] >= 45 and risk >= 45:
        confidence = min(100.0, confidence + 8)
        risk = min(100.0, risk + 6)
        reasons.append("NEIGHBOUR_CORRELATION")

    if risk < 25:
        state, actions = "NORMAL", ["BASELINE_LOGGING"]
    elif risk < 50:
        state, actions = "WATCH", ["INCREASE_MONITORING"]
    elif risk < 78:
        state, actions = "WARNING", ["HIGH_RATE_MONITORING", "CREATE_INCIDENT"]
    else:
        state = "CRITICAL"
        actions = [
            "HIGH_RATE_MONITORING",
            "CREATE_INCIDENT",
            "SAFETY_RECOMMENDATION",
            "ACTIVATE_BUZZER",
            "DISPATCH_INSPECTION",
        ]

    return {
        "schema_version": "1.0",
        "node_id": packet["node_id"],
        "timestamp": packet["timestamp"],
        "state": state,
        "risk": round(risk, 1),
        "confidence": round(confidence, 1),
        "trend": trend,
        "reason_codes": list(dict.fromkeys(reasons)),
        "actions": actions,
    }
