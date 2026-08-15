"""Real end-to-end test of the HiveMind side of the bridge.

This boots a REAL hivemind-core hub (via hivescope's loopback topology — an
actual localhost WebSocket server) and drives the bridge's *production* code
path through a real ``HiveMessageBusClient``. Nothing on the HiveMind side is
mocked: the bridge speaks the real protocol (handshake, encryption, BUS message
admission, whitelist ACL, reverse routing) to a real hub.

Only the hack.chat side is faked — an injected inbound chat message and a
captured-outbound stand-in — because that is the part this test deliberately
isolates from the network. The live hack.chat path is covered separately in
``test_hackchat_live.py``.

Round-trip proven here::

    fake inbound hackchat msg
        → bridge.on_hack_message()
        → bridge.send_to_hivemind()  → real client.emit(recognizer_loop:utterance)
        → real hivemind-core hub admits it (ACL: recognizer_loop:utterance)
        → hub agent bus responder emits `speak` addressed at the satellite peer
        → hub reverse-routes `speak` over the WebSocket to the real client
        → client.internal_bus fires `speak`
        → bridge.handle_speak()  → bridge.speak()
        → captured as an outbound hackchat message "@<user> , <reply>"
"""
import time

import pytest
from ovos_bus_client.message import Message

from hivemind_bus_client.client import HiveMessageBusClient
from hivemind_bus_client.identity import NodeIdentity
from hivescope.topology import TopologyBuilder

from hackchat_bridge import JarbasHackChatBridge


def _host_port(url: str):
    """Split ``ws://127.0.0.1:PORT/`` into (``ws://127.0.0.1``, PORT)."""
    rest = url.replace("ws://", "").replace("wss://", "").rstrip("/")
    host, port = rest.split(":")
    return f"ws://{host}", int(port)


def _make_real_client(url: str, key: str, password: str,
                      name: str = "hackchat-bridge") -> HiveMessageBusClient:
    """Build the production HiveMessageBusClient pointed at the loopback hub."""
    host, port = _host_port(url)
    identity = NodeIdentity()
    identity.access_key = key
    identity.password = password
    identity.default_master = host
    identity.default_port = port
    identity.name = name
    identity.site_id = f"{name}-site"
    return HiveMessageBusClient(
        key=key,
        password=password,
        host=host,
        port=port,
        useragent=name,
        self_signed=False,
        identity=identity,
    )


def _install_speak_responder(master, answer="it is noon"):
    """Make the hub's agent reply with ``speak`` to every utterance.

    When the real client injects ``recognizer_loop:utterance``, hivemind-core
    forwards it onto the agent bus stamping ``context["source"]`` /
    ``context["peer"]`` with the originating satellite peer (see
    ``hivemind_core.protocol.handle_inject_agent_msg``). To get the reply routed
    *back* to that satellite, the responder re-emits a ``speak`` carrying
    ``context["destination"] = <peer>``; the hub's reverse-routing
    (``handle_internal_mycroft``) then ships it down the WebSocket to the client.

    The original ``user`` context (the bridge's ``hackchat_username``) rides
    along on the injected message, so we copy the incoming context and only set
    the destination — proving the bridge gets its user back across the wire.
    """
    bus = master.agent_protocol.bus

    def _responder(msg: Message):
        peer = msg.context.get("source") or msg.context.get("peer")
        ctxt = dict(msg.context)
        ctxt["destination"] = peer
        bus.emit(Message("speak", {"utterance": answer}, ctxt))

    bus.on("recognizer_loop:utterance", _responder)


class FakeHackChat:
    """Stand-in for ``HackChat`` — captures outbound channel messages."""

    def __init__(self):
        self.sent = []
        self.online_users = []

    def send_message(self, msg):
        self.sent.append(msg)


def test_real_hivemind_round_trip():
    b = TopologyBuilder()
    m = b.add_master("M0", use_loopback=True)
    # hivemind-core is deny-by-default / whitelist-only: grant exactly the type
    # the bridge injects.
    m.register_satellite("hackchat-key", password="hackchat-pass",
                         allowed_types=["recognizer_loop:utterance"])
    b.start_all()

    client = None
    try:
        client = _make_real_client(m.network_protocol.url,
                                   "hackchat-key", "hackchat-pass")
        client.connect(site_id="hackchat-site")
        client.wait_for_handshake(timeout=10)
        assert client.handshake_event.is_set(), "handshake did not complete"

        # give the encrypted HELLO time to register the client on the hub
        time.sleep(1)
        assert len(m.connected_peers()) == 1, \
            f"expected the bridge satellite to be connected, got {m.connected_peers()}"

        # the hub agent answers utterances with a spoken reply
        _install_speak_responder(m, answer="it is noon")

        # REAL bridge, wired to the REAL hivemind client; fake hack.chat side
        bridge = JarbasHackChatBridge(username="Jarbas_BOT",
                                      channel="e2e-channel",
                                      bus=client)
        fake_chat = FakeHackChat()
        bridge.hackchat = fake_chat

        # inject an inbound hack.chat message from user "alice"
        bridge.on_hack_message(fake_chat, "what time is it", "alice")

        # wait for the full network round-trip back into the bridge
        deadline = time.time() + 10
        while time.time() < deadline and not fake_chat.sent:
            time.sleep(0.1)

        assert fake_chat.sent, (
            "bridge never produced an outbound hack.chat message — the "
            "HiveMind round-trip did not complete"
        )
        assert fake_chat.sent[0] == "@alice , it is noon", (
            f"unexpected outbound message: {fake_chat.sent!r}"
        )
    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass
        b.stop_all()
