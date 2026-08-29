"""Small SQLite repository used by the laptop prototype."""

import json
import sqlite3
from pathlib import Path


class Database:
    def __init__(self, path: Path | str):
        self.path = str(path)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
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
                """
            )

    def save(self, packet: dict, decision: dict) -> tuple[int, bool]:
        with self.connect() as connection:
            existing = connection.execute(
                "SELECT id FROM readings WHERE node_id = ? AND sequence = ?",
                (packet["node_id"], packet["sequence"]),
            ).fetchone()
            if existing:
                return int(existing["id"]), False
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
        with self.connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [self._reading(row) for row in rows]

    def latest_by_node(self) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for reading in self.latest():
            result.setdefault(reading["packet"]["node_id"], reading)
        return result

    def open_incident(self, decision: dict) -> None:
        if "CREATE_INCIDENT" not in decision["actions"]:
            return
        with self.connect() as connection:
            row = connection.execute(
                "SELECT id FROM incidents WHERE node_id = ? AND status != 'RESOLVED'",
                (decision["node_id"],),
            ).fetchone()
            if row:
                connection.execute(
                    "UPDATE incidents SET state = ? WHERE id = ?", (decision["state"], row["id"])
                )
            else:
                connection.execute(
                    "INSERT INTO incidents(node_id, state, opened_at) VALUES (?, ?, ?)",
                    (decision["node_id"], decision["state"], decision["timestamp"]),
                )

    def incidents(self) -> list[dict]:
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM incidents ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]

    def assign(self, incident_id: int, unit: str) -> dict | None:
        with self.connect() as connection:
            connection.execute(
                "UPDATE incidents SET assigned_unit = ?, status = 'DISPATCHED' WHERE id = ?",
                (unit, incident_id),
            )
            row = connection.execute(
                "SELECT * FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def _reading(row: sqlite3.Row) -> dict:
        return {
            "id": row["id"],
            "packet": json.loads(row["packet"]),
            "decision": json.loads(row["decision"]),
        }
