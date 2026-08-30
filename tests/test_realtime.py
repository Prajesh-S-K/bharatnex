"""Tests for apps/api/realtime.py: EventHub must survive a dropped WebSocket client."""

import asyncio

import pytest
from fastapi import WebSocketDisconnect

from apps.api.realtime import EventHub


class _FakeSocket:
    """Stands in for a fastapi.WebSocket without opening a real connection."""

    def __init__(self, fail: bool = False):
        self.fail = fail
        self.received: list[dict] = []

    async def send_json(self, message: dict) -> None:
        if self.fail:
            raise WebSocketDisconnect(code=1006)
        self.received.append(message)


def test_publish_removes_a_disconnected_client_without_raising():
    hub = EventHub()
    dropped = _FakeSocket(fail=True)
    hub.connections.append(dropped)

    asyncio.run(hub.publish("decision", {"node_id": "NODE_A"}))  # must not raise

    assert dropped not in hub.connections


def test_publish_still_reaches_healthy_clients_after_a_dropped_one():
    hub = EventHub()
    dropped = _FakeSocket(fail=True)
    healthy = _FakeSocket(fail=False)
    hub.connections.extend([dropped, healthy])

    asyncio.run(hub.publish("decision", {"node_id": "NODE_A"}))

    assert dropped not in hub.connections
    assert healthy in hub.connections
    assert healthy.received == [{"type": "decision", "payload": {"node_id": "NODE_A"}}]


def test_publish_reaches_a_healthy_client_even_when_it_is_ahead_of_a_dropped_one():
    """Order matters: a dropped connection earlier in the list must not stop delivery
    to connections later in the list (the bug this guards against would raise mid-loop
    and skip every remaining connection)."""
    hub = EventHub()
    healthy = _FakeSocket(fail=False)
    dropped = _FakeSocket(fail=True)
    hub.connections.extend([dropped, healthy])

    asyncio.run(hub.publish("decision", {"node_id": "NODE_B"}))

    assert healthy.received == [{"type": "decision", "payload": {"node_id": "NODE_B"}}]


def test_publish_with_no_connections_does_nothing():
    hub = EventHub()
    asyncio.run(hub.publish("decision", {}))  # must not raise
    assert hub.connections == []


@pytest.mark.parametrize("exception", [RuntimeError("closed"), WebSocketDisconnect(code=1006)])
def test_both_known_disconnect_exceptions_are_treated_as_stale(exception):
    class _RaisingSocket:
        async def send_json(self, message: dict) -> None:
            raise exception

    hub = EventHub()
    socket = _RaisingSocket()
    hub.connections.append(socket)

    asyncio.run(hub.publish("decision", {}))  # must not raise either exception type

    assert socket not in hub.connections
