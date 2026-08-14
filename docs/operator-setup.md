# Operator setup: running the HackChat bridge

This bridge joins a **[hack.chat](https://hack.chat) channel** and relays each message to and from a HiveMind hub, turning any HiveMind hub, and the OVOS skills behind it, into a hack.chat bot. hack.chat is a minimal, **anonymous**, channel-based websocket chat. There is **no account or token** to get. As an operator you only pick a **nick** and a **channel**, plus a HiveMind hub to point it at.

```
hack.chat user  ⇄  hack.chat channel (wss://hack.chat)  ⇄  hivemind-hackchat-bridge  ⇄  HiveMind hub  ⇄  OVOS skills
```

## 1. "Get the account": there is none

hack.chat is **anonymous**: no signup, no credentials, no API key. You just choose:

- a **nickname** for the bot, shown in the channel, and
- a **channel name** to join, any string. Users reach it at `https://hack.chat/?<channel>`.

The bridge connects to the public server at `wss://hack.chat/chat-ws`. If you run your own [hack.chat](https://github.com/hack-chat/main) server, the same flags apply. Only the connection target differs.

## 2. Prerequisites

- A **channel name** and a **nickname**, from step 1.
- A running **HiveMind hub** (`hivemind-core`) you can reach.
- **Network egress** to `wss://hack.chat`, or your self-hosted hack.chat server.
- Python 3.10+. Deps: `hivemind-bus-client`, `ovos-bus-client`, `ovos-utils`, `websocket-client`, `click`.

## 3. Register the bridge on the hub

On the hub, create a client credential for this bridge:

```bash
hivemind-core add-client          # prints an ACCESS KEY and a PASSWORD
```

Note the **access key**, **password**, and the hub **host** and **port** (default WebSocket port `5678`). The bridge connects as a HiveMind *satellite* with these.

## 4. Install and run the bridge

```bash
pip install .          # provides the `hivemind-hackchat-bridge` command

hivemind-hackchat-bridge \
  --channel  your_channel \
  --username Jarbas_BOT \
  --access-key "your-access-key" \
  --password   "your-hivemind-password" \
  --host ws://your-hub-host \
  --port 5678
```

Flags (verify with `hivemind-hackchat-bridge --help`):

| Flag | Meaning | Default |
| --- | --- | --- |
| `--channel` | hack.chat channel to join (required) | none |
| `--username` | bot nickname shown in the channel | `Jarbas_BOT` |
| `--access-key` / `--password` | HiveMind credentials | `None` |
| `--host` / `--port` | HiveMind hub (`ws://`/`wss://`) | `ws://127.0.0.1` / `5678` |
| `--self-signed` | accept self-signed TLS | off |
| `--lang` | utterance language | `en-us` |

## 5. Talk to it

Open the same channel at `https://hack.chat/?your_channel` and type:

```
what time is it?
```

The bridge forwards every channel message, except its own, to the hub as a `recognizer_loop:utterance`, stripping a leading `@username` mention of the bot, and posts the hub's reply back as `@user , <answer>`.

## Security notes

- hack.chat is anonymous and public. **Anyone** who joins the channel can reach the hub. Use an obscure channel name and restrict access at the hub with client ACLs (`allowed_types`).
- The **HiveMind password** is the only secret here. Pass it through an environment variable or a secrets manager, never in shell history or a committed file.

## Testing (live e2e)

`tests/e2e/test_hackchat_live.py` runs a **real** hack.chat round-trip against the public service. Because hack.chat is anonymous it needs **no credentials and no env vars, only network egress**. It connects the bridge's real client to a random channel, posts from a second anonymous client, and checks that the bridge forwards the message. If egress to `wss://hack.chat` is unavailable it **skips** cleanly rather than failing:

```bash
pytest tests/e2e/test_hackchat_live.py
```

The HiveMind round-trip itself is proven unconditionally in `tests/e2e/test_hivemind_e2e.py`.

---
[← Setup walkthrough](setup.md) · [Home](../readme.md) · [Configuration →](configuration.md)
