"""Small SQLite repository used by the laptop prototype."""

import contextlib
import json
import sqlite3
from collections.abc import Iterator
from pathlib import Path


class Database:
    def __init__(self, path: Path | str):
        self.path = str(path)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    @contextlib.contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        """Open a connection that both commits/rolls back (like `with connect()`)
        and is always closed afterward. Relying on CPython refcounting to close the
        bare `sqlite3.connect()` result was leaving file handles open long enough to
        fail same-process cleanup on Windows; every query path now goes through this."""
        connection = self.connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    packet TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    UNIQUE(node_id, sequence)
                );
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id TEXT NOT NULL,
                    state TEXT NOT NULL,
                    opened_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'OPEN',
                    assigned_unit TEXT,
                    UNIQUE(node_id, opened_at)
                );
                CREATE TABLE IF NOT EXISTS units (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL DEFAULT 'AVAILABLE',
                    position_x REAL NOT NULL,
                    position_y REAL NOT NULL,
                    active_incident_id INTEGER,
                    last_assigned_at TEXT,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS inspection_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id INTEGER NOT NULL,
                    unit_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    notes TEXT,
                    severity TEXT,
                    checklist TEXT NOT NULL DEFAULT '{}',
                    photos TEXT NOT NULL DEFAULT '[]',
                    rejection_reason TEXT
                );
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    incident_id INTEGER,
                    details TEXT NOT NULL DEFAULT '{}'
                );
                """
            )
            self._ensure_incident_columns(connection)
            now = self._now()
            connection.executemany(
                "INSERT OR IGNORE INTO units(id, position_x, position_y, updated_at) "
                "VALUES (?, ?, ?, ?)",
                [("ALPHA", 12, 82, now), ("BRAVO", 88, 18, now)],
            )

    @staticmethod
    def _ensure_incident_columns(connection: sqlite3.Connection) -> None:
        existing = {row[1] for row in connection.execute("PRAGMA table_info(incidents)")}
        additions = {
            "zone": "TEXT NOT NULL DEFAULT 'PANEL-01'",
            "acknowledged_at": "TEXT",
            "acknowledged_by": "TEXT",
            "resolved_at": "TEXT",
            "resolved_by": "TEXT",
            "resolution_notes": "TEXT",
            "recommendation": (
                "TEXT NOT NULL DEFAULT 'Inspect the affected zone using approved mine safety "
                "procedures.'"
            ),
        }
        for name, definition in additions.items():
            if name not in existing:
                connection.execute(f"ALTER TABLE incidents ADD COLUMN {name} {definition}")

    def save(self, packet: dict, decision: dict) -> tuple[int, bool]:
        with self._connection() as connection:
            existing = connection.execute(
                "SELECT id FROM readings WHERE node_id = ? AND sequence = ?",
                (packet["node_id"], packet["sequence"]),
            ).fetchone()
            if existing:
                return int(existing["id"]), False
            # `latest()` orders by insertion id, not by the packet's own sequence, so
            # a late-arriving OLDER sequence must be rejected here too -- otherwise it
            # gets inserted as a new row and is then read back as the "latest" state,
            # silently reverting an already-escalated node back to stale sensor data.
            newest = connection.execute(
                "SELECT MAX(sequence) AS max_sequence FROM readings WHERE node_id = ?",
                (packet["node_id"],),
            ).fetchone()["max_sequence"]
            if newest is not None and packet["sequence"] < newest:
                return -1, False
            cursor = connection.execute(
                "INSERT INTO readings(node_id, sequence, timestamp, packet, decision) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    packet["node_id"],
                    packet["sequence"],
                    packet["timestamp"],
                    json.dumps(packet),
                    json.dumps(decision),
                ),
            )
            return int(cursor.lastrowid), True

    def latest(self, node_id: str | None = None) -> list[dict]:
        query = "SELECT * FROM readings"
        params: tuple[str, ...] = ()
        if node_id:
            query += " WHERE node_id = ?"
            params = (node_id,)
        query += " ORDER BY id DESC LIMIT 100"
        with self._connection() as connection:
            rows = connection.execute(query, params).fetchall()
        return [self._reading(row) for row in rows]

    def latest_by_node(self) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for reading in self.latest():
            result.setdefault(reading["packet"]["node_id"], reading)
        return result

    def open_incident(self, decision: dict) -> int | None:
        if "CREATE_INCIDENT" not in decision["actions"]:
            return None
        with self._connection() as connection:
            row = connection.execute(
                "SELECT id FROM incidents WHERE node_id = ? AND status != 'RESOLVED'",
                (decision["node_id"],),
            ).fetchone()
            if row:
                connection.execute(
                    "UPDATE incidents SET state = ? WHERE id = ?", (decision["state"], row["id"])
                )
                return int(row["id"])
            else:
                cursor = connection.execute(
                    "INSERT INTO incidents(node_id, state, opened_at) VALUES (?, ?, ?)",
                    (decision["node_id"], decision["state"], decision["timestamp"]),
                )
                incident_id = int(cursor.lastrowid)
                self._audit_with_connection(
                    connection,
                    "SYSTEM",
                    "INCIDENT_CREATED",
                    incident_id,
                    {"state": decision["state"]},
                )
                return incident_id

    def incidents(self) -> list[dict]:
        with self._connection() as connection:
            rows = connection.execute("SELECT * FROM incidents ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]

    def incident(self, incident_id: int) -> dict | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
        return dict(row) if row else None

    def assign(self, incident_id: int, unit: str) -> dict | None:
        with self._connection() as connection:
            incident = connection.execute(
                "SELECT * FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
            if not incident:
                return None
            old_unit = incident["assigned_unit"]
            now = self._now()
            if old_unit and old_unit != unit:
                connection.execute(
                    "UPDATE units SET status = 'AVAILABLE', active_incident_id = NULL, "
                    "updated_at = ? WHERE id = ?",
                    (now, old_unit),
                )
            connection.execute(
                "UPDATE incidents SET assigned_unit = ?, status = 'DISPATCHED' WHERE id = ?",
                (unit, incident_id),
            )
            connection.execute(
                "UPDATE units SET status = 'DISPATCHED', active_incident_id = ?, "
                "last_assigned_at = ?, updated_at = ? WHERE id = ?",
                (incident_id, now, now, unit),
            )
            self._audit_with_connection(
                connection,
                "OPERATOR",
                "INCIDENT_REASSIGNED" if old_unit and old_unit != unit else "UNIT_DISPATCHED",
                incident_id,
                {"from": old_unit, "to": unit},
            )
            row = connection.execute(
                "SELECT * FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
        return dict(row) if row else None

    def auto_assign(self, incident_id: int, target: tuple[float, float]) -> dict | None:
        units = [unit for unit in self.units() if unit["status"] == "AVAILABLE"]
        if not units:
            self.audit("SYSTEM", "DISPATCH_UNAVAILABLE", incident_id, {})
            return None
        unit = min(
            units,
            key=lambda item: (
                (item["position_x"] - target[0]) ** 2 + (item["position_y"] - target[1]) ** 2,
                item["last_assigned_at"] or "",
            ),
        )
        return self.assign(incident_id, unit["id"])

    def units(self) -> list[dict]:
        with self._connection() as connection:
            rows = connection.execute("SELECT * FROM units ORDER BY id").fetchall()
        return [dict(row) for row in rows]

    def unit_assignment(self, unit_id: str) -> dict | None:
        with self._connection() as connection:
            row = connection.execute(
                """SELECT incidents.* FROM incidents
                JOIN units ON units.active_incident_id = incidents.id
                WHERE units.id = ? AND incidents.status != 'RESOLVED'""",
                (unit_id,),
            ).fetchone()
        return dict(row) if row else None

    def update_inspection(self, incident_id: int, unit_id: str, payload: dict) -> dict | None:
        allowed = {
            "ACCEPTED",
            "EN_ROUTE",
            "ON_SITE",
            "INSPECTION_STARTED",
            "COMPLETED",
            "REJECTED",
            "ASSISTANCE_REQUESTED",
        }
        status = payload["status"]
        if status not in allowed:
            raise ValueError("Unsupported inspection status")
        with self._connection() as connection:
            incident = connection.execute(
                "SELECT * FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
            if not incident or incident["assigned_unit"] != unit_id:
                return None
            now = self._now()
            cursor = connection.execute(
                """INSERT INTO inspection_updates(
                    incident_id, unit_id, status, timestamp, notes, severity,
                    checklist, photos, rejection_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    incident_id,
                    unit_id,
                    status,
                    now,
                    payload.get("notes"),
                    payload.get("severity"),
                    json.dumps(payload.get("checklist", {})),
                    json.dumps(payload.get("photos", [])),
                    payload.get("rejection_reason"),
                ),
            )
            unit_status = status
            incident_status = status
            active_incident: int | None = incident_id
            if status == "REJECTED":
                unit_status, incident_status, active_incident = "AVAILABLE", "OPEN", None
                connection.execute(
                    "UPDATE incidents SET assigned_unit = NULL WHERE id = ?", (incident_id,)
                )
            elif status == "COMPLETED":
                unit_status, incident_status, active_incident = (
                    "AVAILABLE",
                    "INSPECTION_COMPLETED",
                    None,
                )
            connection.execute(
                "UPDATE incidents SET status = ? WHERE id = ?", (incident_status, incident_id)
            )
            connection.execute(
                "UPDATE units SET status = ?, active_incident_id = ?, updated_at = ? WHERE id = ?",
                (unit_status, active_incident, now, unit_id),
            )
            self._audit_with_connection(connection, unit_id, status, incident_id, payload)
            row = connection.execute(
                "SELECT * FROM inspection_updates WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        return self._inspection(row)

    def inspection_updates(self, incident_id: int) -> list[dict]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM inspection_updates WHERE incident_id = ? ORDER BY id", (incident_id,)
            ).fetchall()
        return [self._inspection(row) for row in rows]

    def acknowledge(self, incident_id: int, actor: str) -> dict | None:
        with self._connection() as connection:
            now = self._now()
            connection.execute(
                "UPDATE incidents SET acknowledged_at = ?, acknowledged_by = ? WHERE id = ?",
                (now, actor, incident_id),
            )
            self._audit_with_connection(connection, actor, "INCIDENT_ACKNOWLEDGED", incident_id, {})
            row = connection.execute(
                "SELECT * FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
        return dict(row) if row else None

    def resolve(self, incident_id: int, actor: str, notes: str) -> dict | None:
        with self._connection() as connection:
            incident = connection.execute(
                "SELECT * FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
            if not incident:
                return None
            now = self._now()
            connection.execute(
                "UPDATE incidents SET status = 'RESOLVED', resolved_at = ?, resolved_by = ?, "
                "resolution_notes = ? WHERE id = ?",
                (now, actor, notes, incident_id),
            )
            if incident["assigned_unit"]:
                connection.execute(
                    "UPDATE units SET status = 'AVAILABLE', active_incident_id = NULL, "
                    "updated_at = ? WHERE id = ?",
                    (now, incident["assigned_unit"]),
                )
            self._audit_with_connection(
                connection, actor, "INCIDENT_RESOLVED", incident_id, {"notes": notes}
            )
            row = connection.execute(
                "SELECT * FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
        return dict(row)

    def audit(self, actor: str, event_type: str, incident_id: int | None, details: dict) -> None:
        with self._connection() as connection:
            self._audit_with_connection(connection, actor, event_type, incident_id, details)

    def audit_events(self, incident_id: int | None = None) -> list[dict]:
        query = "SELECT * FROM audit_events"
        params: tuple[int, ...] = ()
        if incident_id is not None:
            query += " WHERE incident_id = ?"
            params = (incident_id,)
        query += " ORDER BY id DESC LIMIT 200"
        with self._connection() as connection:
            rows = connection.execute(query, params).fetchall()
        return [{**dict(row), "details": json.loads(row["details"])} for row in rows]

    def reset_demo(self) -> None:
        with self._connection() as connection:
            connection.execute("DELETE FROM inspection_updates")
            connection.execute("DELETE FROM audit_events")
            connection.execute("DELETE FROM incidents")
            connection.execute("DELETE FROM readings")
            now = self._now()
            connection.execute(
                "UPDATE units SET status = 'AVAILABLE', active_incident_id = NULL, "
                "last_assigned_at = NULL, updated_at = ?",
                (now,),
            )

    @staticmethod
    def _audit_with_connection(
        connection: sqlite3.Connection,
        actor: str,
        event_type: str,
        incident_id: int | None,
        details: dict,
    ) -> None:
        connection.execute(
            "INSERT INTO audit_events(timestamp, actor, event_type, incident_id, details) "
            "VALUES (?, ?, ?, ?, ?)",
            (Database._now(), actor, event_type, incident_id, json.dumps(details)),
        )

    @staticmethod
    def _inspection(row: sqlite3.Row) -> dict:
        result = dict(row)
        result["checklist"] = json.loads(result["checklist"])
        result["photos"] = json.loads(result["photos"])
        return result

    @staticmethod
    def _now() -> str:
        from datetime import UTC, datetime

        return datetime.now(UTC).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _reading(row: sqlite3.Row) -> dict:
        return {
            "id": row["id"],
            "packet": json.loads(row["packet"]),
            "decision": json.loads(row["decision"]),
        }
