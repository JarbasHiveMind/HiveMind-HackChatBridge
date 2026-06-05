# Examples

## Run the bridge

Configure the call at the bottom of `hackchat_bridge/__main__.py`:

```python
from hackchat_bridge.__main__ import connect_hackchat_to_hivemind

connect_hackchat_to_hivemind(
    channel="your_channel",
    username="Jarbas_BOT",
    host="wss://127.0.0.1",
    port=5678,
    key="your-access-key",
)
```

Then start it:

```bash
python -m hackchat_bridge
```

## A conversation

Open `https://hack.chat/?your_channel` in a browser, join with any nickname, and chat:

```
alice> what time is it?
Jarbas_BOT> @alice , It is half past three.

alice> set a timer for five minutes
Jarbas_BOT> @alice , Timer set for five minutes.
```

The bot answers every message in the channel and addresses replies to the sender.

## Verify the hack.chat connection alone

To confirm the channel and websocket work before wiring HiveMind, use the `HackChat` client directly:

```python
from hackchat_bridge.hackchat import HackChat

chat = HackChat("EchoBot", channel="your_channel")

def echo(connector, message, sender):
    connector.send_message("@{} {}".format(sender, message))

chat.on_message += [echo]
chat.run()
```

If the echo bot mirrors messages in the channel, the hack.chat half is working and you can move on to wiring the HiveMind half.
