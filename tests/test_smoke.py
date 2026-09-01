"""Smoke tests: import the package and construct the bridge without networking.

These tests must not touch the live hack.chat service or a HiveMind hub. The
HiveMessageBusClient is replaced by a fake bus, and ``HackChat`` (which opens a
websocket in its constructor) is only exercised lazily via ``connect_hackchat``,
which we do not call here.
"""
import hackchat_bridge
from hackchat_bridge import JarbasHackChatBridge, platform
from hackchat_bridge.version import __version__


class FakeBus:
    """Minimal stand-in for HiveMessageBusClient — records emits/handlers."""

    def __init__(self):
        self.emitted = []
        self.mycroft_handlers = {}

    def on_mycroft(self, msg_type, func):
        self.mycroft_handlers[msg_type] = func

    def emit(self, message):
        self.emitted.append(message)

    def run_forever(self):  # pragma: no cover - never called in tests
        pass


def test_version():
    assert isinstance(__version__, str)
    assert __version__
    assert platform.startswith("JarbasHackChatBridge")
    assert __version__ in platform


def test_package_exports():
    assert hasattr(hackchat_bridge, "JarbasHackChatBridge")
    assert hasattr(hackchat_bridge, "HackChat")


def test_bridge_constructs_with_injected_bus():
    bus = FakeBus()
    bridge = JarbasHackChatBridge(username="Jarbas_BOT",
                                  channel="test_channel",
                                  bus=bus)
    assert bridge.status == "disconnected"
    assert bridge.hackchat is None
    assert bridge.online_users == []
    # speak/intent-failure handlers were registered on the bus
    assert "speak" in bus.mycroft_handlers
    assert "hive.complete_intent_failure" in bus.mycroft_handlers


def test_send_to_hivemind_emits_utterance():
    from ovos_bus_client import Message

    bus = FakeBus()
    bridge = JarbasHackChatBridge(username="Jarbas_BOT",
                                  channel="test_channel",
                                  bus=bus)
    bridge.send_to_hivemind("what time is it", "alice")
    assert len(bus.emitted) == 1
    msg = bus.emitted[0]
    assert isinstance(msg, Message)
    assert msg.msg_type == "recognizer_loop:utterance"
    assert msg.data["utterances"] == ["what time is it"]
    assert msg.context["user"]["hackchat_username"] == "alice"


def test_connect_uses_bounded_handshake_retries(monkeypatch):
    """connect() must be called with a non-None handshake_max_retries.

    hivemind-bus-client >=1.0.13a1 defaults handshake_max_retries=None on
    connect(), which retries the handshake forever if the hub is stalled,
    unreachable, or the password is wrong. The bridge must always pass a
    bounded value.
    """
    calls = []

    class FakeHiveMessageBusClient:
        def __init__(self, *args, **kwargs):
            pass

        def connect(self, *args, **kwargs):
            calls.append(kwargs)

        def on_mycroft(self, msg_type, func):
            pass

    monkeypatch.setattr(hackchat_bridge, "HiveMessageBusClient",
                        FakeHiveMessageBusClient)

    JarbasHackChatBridge(username="Jarbas_BOT", channel="test_channel")

    assert len(calls) == 1
    assert "handshake_max_retries" in calls[0]
    assert calls[0]["handshake_max_retries"] is not None


def test_handle_speak_routes_back_to_user(monkeypatch):
    from ovos_bus_client import Message

    bus = FakeBus()
    bridge = JarbasHackChatBridge(username="Jarbas_BOT",
                                  channel="test_channel",
                                  bus=bus)
    sent = []

    class FakeHackChat:
        def send_message(self, msg):
            sent.append(msg)

    bridge.hackchat = FakeHackChat()
    msg = Message("speak", {"utterance": "it is noon"},
                  {"user": {"hackchat_username": "alice"}})
    bus.mycroft_handlers["speak"](msg)
    assert sent == ["@alice , it is noon"]
