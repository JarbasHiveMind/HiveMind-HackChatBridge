# HiveMind HackChat Bridge

Relay a [hack.chat](https://hack.chat) channel to a [HiveMind](https://github.com/JarbasHiveMind/HiveMind-core) hub.

[hack.chat](https://hack.chat) is a minimal, anonymous, channel-based websocket chat. This bridge is a HiveMind **satellite** whose input and output are a hack.chat channel instead of a microphone. Channel messages become utterances sent to the hub. The hub's spoken reply goes back into the channel, addressed to the user. Any HiveMind hub, and the OVOS skills behind it, becomes a hack.chat bot.

```
hack.chat channel  ⇄  HiveMind-HackChatBridge  ⇄  HiveMind hub  ⇄  OVOS skills
```

![](./hackchat.png)
![](./hackchat_bridge.png)

## Prerequisites

- A running **HiveMind hub** ([hivemind-core](https://github.com/JarbasHiveMind/HiveMind-core)) reachable over the network, and a **HiveMind access key** for this bridge (`hivemind-core add-client`).
- A **hack.chat channel name** to join, and a **nickname** for the bot. hack.chat is anonymous, so no account or token is needed.

## Install

```bash
pip install HiveMind-HackChatBridge
```

Or from a checkout:

```bash
git clone https://github.com/JarbasHiveMind/HiveMind-HackChatBridge
cd HiveMind-HackChatBridge
pip install .
```

Declared dependencies: `hivemind-bus-client`, `ovos-bus-client`, `ovos-utils`, `websocket-client`, `click`.

## Quickstart

1. Register the bridge on the hub, where `hivemind-core` is installed:

```bash
hivemind-core add-client --name hackchat-bridge \
  --access-key "your-access-key" --password "your-password"
```

2. Run the bridge. Pass the configuration on the command line, using the `hivemind-hackchat-bridge` console script (or `python -m hackchat_bridge`):

```bash
hivemind-hackchat-bridge \
  --channel your_channel \
  --username Jarbas_BOT \
  --access-key "your-access-key" \
  --password "your-password" \
  --host ws://127.0.0.1 \
  --port 5678
```

3. Send a message. Open the same channel at `https://hack.chat/?your_channel` and type:

```
what time is it?
```

The bridge forwards the message to the hub and posts the reply back as `@user , <answer>`.

## Configuration

`hivemind-hackchat-bridge` options:

| Option | Description | Default |
| --- | --- | --- |
| `--channel` | hack.chat channel name to join | required |
| `--username` | Bot nickname shown in the channel | `Jarbas_BOT` |
| `--host` | HiveMind hub host (`wss://` / `ws://`) | `ws://127.0.0.1` |
| `--port` | HiveMind hub port | `5678` |
| `--access-key` | HiveMind access key | `None` |
| `--password` | HiveMind password | `None` |
| `--self-signed` | Accept self-signed SSL certificates | off |
| `--lang` | Language code for utterances | `en-us` |

The bridge forwards every channel message except its own, and strips a leading `@username` mention of the bot before sending it.

## Troubleshooting

- **Bot joins but never answers.** Confirm the hub is reachable and the access key and password are registered (`hivemind-core list-clients`), and that the hub produces a `speak` for the answer.
- **Wrong channel.** The bot and the user must join the same hack.chat channel name. Open `https://hack.chat/?<channel>`.

## Documentation

- [Setup walkthrough](docs/setup.md): install a hub, register the bridge, and run it end to end.
- [Operator setup](docs/operator-setup.md): the anonymous hack.chat model, security notes, and live end-to-end testing.
- [Configuration reference](docs/configuration.md): every command-line option and how message handling works.
- [Examples](docs/examples.md): running the bridge, embedding it in code, and a sample conversation.

## Related projects

- [HiveMind-core](https://github.com/JarbasHiveMind/HiveMind-core): the HiveMind hub this bridge connects to.

## License

Apache License 2.0. See [LICENSE](LICENSE).
