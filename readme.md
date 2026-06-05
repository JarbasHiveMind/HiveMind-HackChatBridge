# HiveMind HackChat Bridge

Relay a [hack.chat](https://hack.chat) channel to a [HiveMind](https://github.com/JarbasHiveMind/HiveMind-core) hub.

[hack.chat](https://hack.chat) is a minimal, anonymous, channel-based websocket chat. This bridge is a HiveMind **satellite** whose input and output are a hack.chat channel instead of a microphone. Channel messages become utterances sent to the hub; the hub's spoken reply is posted back into the channel, addressed to the user. Any HiveMind hub (and the OVOS skills behind it) becomes a hack.chat bot.

```
hack.chat channel  ⇄  HiveMind-HackChatBridge  ⇄  HiveMind hub  ⇄  OVOS skills
```

![](./hackchat.png)
![](./hackchat_bridge.png)

## Prerequisites

- A running **HiveMind hub** ([hivemind-core](https://github.com/JarbasHiveMind/HiveMind-core)) reachable over the network, and a **HiveMind access key** for this bridge (`hivemind-core add-client`).
- A **hack.chat channel name** to join, and a **nickname** for the bot. hack.chat is anonymous — no account or token is required.

## Install

This repo has no published package. Install the runtime dependencies and run from a checkout:

```bash
git clone https://github.com/JarbasHiveMind/HiveMind-HackChatBridge
cd HiveMind-HackChatBridge
pip install -r requirements.txt
pip install websocket-client   # imported by hackchat.py, not pinned in requirements.txt
```

Declared dependencies: `jarbas_hive_mind<=0.8.0`, `ovos_utils`.

## Quickstart

**1. Register the bridge on the hub** (where `hivemind-core` is installed):

```bash
hivemind-core add-client --name hackchat-bridge \
  --access-key "your-access-key" --password "your-password"
```

**2. Configure the bridge.** The entry point is `connect_hackchat_to_hivemind(...)` in `hackchat_bridge/__main__.py`. Edit the call at the bottom of that file:

```python
from hackchat_bridge.__main__ import connect_hackchat_to_hivemind

connect_hackchat_to_hivemind(
    channel="your_channel",                  # hack.chat channel to join
    username="Jarbas_BOT",                   # bot nickname
    host="wss://127.0.0.1",                  # HiveMind hub host
    port=5678,                               # HiveMind hub port
    key="your-access-key",                   # HiveMind access key
)
```

**3. Run it:**

```bash
python -m hackchat_bridge
```

**4. Send a message.** Open the same channel at `https://hack.chat/?your_channel` and type:

```
what time is it?
```

The bridge forwards the message to the hub and posts the reply back as `@user , <answer>`.

## Configuration

`connect_hackchat_to_hivemind(...)` parameters:

| Parameter | Description | Default |
| --- | --- | --- |
| `channel` | hack.chat channel name to join | — |
| `username` | Bot nickname shown in the channel | `Jarbas_BOT` |
| `host` | HiveMind hub host (`wss://` / `ws://`) | `wss://127.0.0.1` |
| `port` | HiveMind hub port | `5678` |
| `key` | HiveMind access key | `unsafe` |
| `crypto_key` | Optional HiveMind payload crypto key | `None` |

The bridge forwards every channel message except its own, stripping a leading `@username` mention of the bot before sending.

## Troubleshooting

- **`ModuleNotFoundError: websocket`** — install `websocket-client` (it is imported by `hackchat.py` but not pinned).
- **Bot joins but never answers** — confirm the hub is reachable and the access key is registered (`hivemind-core list-clients`), and that the hub produces a `speak` for the answer.
- **Wrong channel** — the bot and the user must be on the same hack.chat channel name; open `https://hack.chat/?<channel>`.

## Documentation

See [`docs/`](docs/) for a full setup walkthrough, a configuration reference, and worked examples.
