import time

from ovos_utils import create_daemon
from ovos_utils.log import LOG

from hivemind_bus_client import HiveMessageBusClient
from ovos_bus_client import Message

from hackchat_bridge.hackchat import HackChat
from hackchat_bridge.version import __version__

platform = f"JarbasHackChatBridgeV{__version__}"


class JarbasHackChatBridge:
    """Relay a hack.chat channel to a HiveMind hub.

    Channel messages become ``recognizer_loop:utterance`` messages on the
    HiveMind bus; the hub's ``speak`` reply is posted back into the channel,
    addressed to the originating user.
    """

    def __init__(self, username, channel,
                 access_key=None,
                 host="ws://127.0.0.1",
                 port=5678,
                 password=None,
                 self_signed=False,
                 lang="en-us",
                 bus=None):
        self.status = "disconnected"
        self.username = username
        self.channel = channel
        self.lang = lang
        self.hackchat = None

        if bus:
            # got a connection already
            self.bus = bus
        else:
            # connect to hivemind
            self.bus = HiveMessageBusClient(access_key,
                                            host=host,
                                            port=port,
                                            password=password,
                                            self_signed=self_signed)
            self.bus.connect()

        self.bus.on_mycroft("speak", self.handle_speak)
        self.bus.on_mycroft("hive.complete_intent_failure",
                            self.handle_intent_failure)

    def connect_hackchat(self):
        """Join the hack.chat channel and start relaying messages."""
        self.hackchat = HackChat(self.username, self.channel)
        self.hackchat.on_message += [self.on_hack_message]
        self.hackchat.on_join += [self.on_hack_join]
        self.hackchat.on_open += [self.on_hack_open]
        self.hackchat.on_leave += [self.on_hack_leave]
        self.status = "connected"
        LOG.info("Channel: {0}".format(self.channel))
        LOG.info("Username: {0}".format(self.username))
        create_daemon(self.hackchat.run)

    @property
    def online_users(self):
        if self.hackchat is None:
            return []
        return self.hackchat.online_users

    # hack.chat callbacks
    def on_hack_open(self, connector, users):
        if len(users) == 1:
            self.hackchat.send_message("This channel belongs to me")
        else:
            self.hackchat.send_message("I see {} online users"
                                       .format(len(users) - 1))

    def on_hack_join(self, connector, user):
        self.hackchat.send_message("Hello @{}".format(user))

    def on_hack_leave(self, connector, user):
        self.hackchat.send_message("@{} vanished from cyberspace".format(user))

    def on_hack_message(self, connector, message, user):
        utterance = message.lower().strip()
        if user != self.username:
            utterance = utterance.replace("@" + self.username.lower(), "").strip()
            self.send_to_hivemind(utterance, user)

    # hivemind side
    def send_to_hivemind(self, utterance, user):
        """Forward a channel utterance to the HiveMind hub."""
        msg = Message("recognizer_loop:utterance",
                      {"utterances": [utterance], "lang": self.lang},
                      {"destination": "hive_mind",
                       "platform": platform,
                       "user": {"hackchat_username": user}})
        self.bus.emit(msg)

    def speak(self, utterance, user_data):
        user = user_data["hackchat_username"]
        utterance = "@{} , ".format(user) + utterance
        LOG.debug("Message: " + utterance)
        if self.hackchat is not None:
            self.hackchat.send_message(utterance)

    def handle_speak(self, message):
        assert isinstance(message, Message)
        user_data = message.context.get("user")
        if user_data:
            utterance = message.data["utterance"]
            self.speak(utterance, user_data)

    def handle_intent_failure(self, message):
        assert isinstance(message, Message)
        user_data = message.context.get("user")
        if user_data:
            LOG.error("complete intent failure")
            self.speak("I don't know how to answer that", user_data)

    def run(self):
        """Connect to hack.chat and block forever.

        ``self.bus.connect()`` (called from ``__init__``) already starts the
        HiveMind websocket reconnect lifecycle in a background thread, so the
        client is fully connected by the time ``run()`` is called. Calling
        ``self.bus.run_forever()`` here would try to claim that same
        lifecycle a second time and raise ``RuntimeError("HiveMind websocket
        reconnect worker is already running")``, causing the bridge to churn
        and never stabilize. Block this thread some other way instead of
        re-starting the worker.
        """
        self.connect_hackchat()
        while True:
            time.sleep(1)
