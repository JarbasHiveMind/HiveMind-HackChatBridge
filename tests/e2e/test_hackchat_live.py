"""Live hack.chat loop — no account required (hack.chat is anonymous).

If outbound egress to ``wss://hack.chat`` is available, this connects the
bridge's *real* ``HackChat`` client to a real hack.chat channel (random nick in
a random channel so the test is isolated), posts a message from a second
anonymous WebSocket client, and asserts the bridge receives it and forwards it
on to the (faked) HiveMind side.

This proves the bridge's real hack.chat client code path end to end over the
live service. The HiveMind round-trip itself is proven unconditionally in
``test_hivemind_e2e.py``; here the HiveMind bus is faked so the test depends
only on the hack.chat link.

If egress is blocked (sandbox / CI without network), the test SKIPS with a clear
reason rather than failing — it is network-gated, not a dependency we dodge.
"""
import json
import random
import string
import threading
import time

import pytest
import websocket  # websocket-client, a real bridge dependency

from hackchat_bridge import JarbasHackChatBridge


HACKCHAT_WS = "wss://hack.chat/chat-ws"
CONNECT_TIMEOUT = 8


def _rand(prefix):
    return prefix + "".join(random.choices(string.ascii_lowercase + string.digits,
                                            k=10))


def _probe_hackchat():
    """Return a connected ws to hack.chat, or skip if egress is unavailable."""
    try:
        ws = websocket.create_connection(HACKCHAT_WS, timeout=CONNECT_TIMEOUT)
        return ws
    except Exception as e:  # network egress blocked / DNS / TLS / timeout
        pytest.skip(f"hack.chat egress unavailable ({type(e).__name__}: {e}); "
                    f"network-gated live test")


class FakeBus:
    """Minimal HiveMind bus stand-in — records utterances the bridge forwards."""

    def __init__(self):
        self.emitted = []
        self.event = threading.Event()

    def on_mycroft(self, msg_type, func):
        pass

    def emit(self, message):
        self.emitted.append(message)
        self.event.set()

    def run_forever(self):  # pragma: no cover - not called here
        pass


def test_live_hackchat_inbound_reaches_bridge():
    # fail fast (with skip) if we cannot reach the live service at all
    probe = _probe_hackchat()
    probe.close()

    channel = _rand("hcbridge-e2e-")
    bot_nick = _rand("Bot_")
    poster_nick = _rand("User_")

    bus = FakeBus()
    bridge = JarbasHackChatBridge(username=bot_nick, channel=channel, bus=bus)

    # connect the bridge's REAL HackChat client to the live channel
    try:
        bridge.connect_hackchat()
    except Exception as e:
        pytest.skip(f"could not join live hack.chat channel "
                    f"({type(e).__name__}: {e}); network-gated")

    poster = None
    try:
        # let the bridge fully join before a second client posts
        time.sleep(2)

        # second anonymous client joins the same channel and posts a message
        poster = websocket.create_connection(HACKCHAT_WS, timeout=CONNECT_TIMEOUT)
        poster.send(json.dumps({"cmd": "join", "channel": channel,
                                "nick": poster_nick}))
        time.sleep(1)
        poster.send(json.dumps({"cmd": "chat", "text": "what time is it"}))

        # the bridge should receive it and forward a recognizer_loop:utterance
        assert bus.event.wait(timeout=15), (
            "bridge did not forward the live hack.chat message to HiveMind "
            "within 15s"
        )
        assert bus.emitted, "no utterance was emitted"
        msg = bus.emitted[-1]
        assert msg.msg_type == "recognizer_loop:utterance"
        assert "what time is it" in msg.data["utterances"][0]
        assert msg.context["user"]["hackchat_username"] == poster_nick
    finally:
        if poster is not None:
            try:
                poster.close()
            except Exception:
                pass
        try:
            if bridge.hackchat is not None:
                bridge.hackchat.ws.close()
        except Exception:
            pass
