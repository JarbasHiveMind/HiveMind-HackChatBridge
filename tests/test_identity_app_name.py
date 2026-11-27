"""The bridge connects with its own identity (HIVEMIND-CRYPTO-1 §2)."""
from unittest.mock import MagicMock, patch

from hackchat_bridge import JarbasHackChatBridge
import hackchat_bridge


def test_the_bridge_builds_its_client_with_its_own_identity():
    identity = MagicMock()
    with patch.object(hackchat_bridge, "NodeIdentity", return_value=identity) as ctor, \
         patch.object(hackchat_bridge, "HiveMessageBusClient") as client:
        JarbasHackChatBridge("bot", "channel", access_key="k", password="p")
    ctor.assert_called_once_with(app_name="hackchat-bridge")
    assert client.call_args.kwargs["identity"] is identity


def test_a_given_identity_is_used_as_is():
    identity = MagicMock()
    with patch.object(hackchat_bridge, "NodeIdentity") as ctor, \
         patch.object(hackchat_bridge, "HiveMessageBusClient") as client:
        JarbasHackChatBridge("bot", "channel", identity=identity)
    ctor.assert_not_called()
    assert client.call_args.kwargs["identity"] is identity
