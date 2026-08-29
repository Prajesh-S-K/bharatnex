# Prototype acceptance tests

| ID | Scenario | Expected result |
|---|---|---|
| A01 | Stable Node A and B | NORMAL, low Risk, valid Confidence |
| A02 | Gradual displacement at Node B | rising trend, state escalates according to thresholds |
| A03 | Sudden vibration spike only | anomaly recorded; persistence/fusion prevents unsupported certainty |
| A04 | A and B correlated deformation | Confidence increases and correlation reason appears |
| A05 | Node B near active face | geometry contributes to Risk and reason output |
| A06 | Invalid sensor value | rejected/quarantined and health degraded |
| A07 | Duplicate sequence | idempotent handling; no duplicate decision |
| A08 | Missing heartbeat | node becomes offline; absence is not treated as safe |
| A09 | CRITICAL transition | safety recommendation, incident, buzzer and Alpha/Bravo dispatch |
| A10 | Recovery | controlled de-escalation; incident history retained |

