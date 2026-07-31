# Configuration & Credentials Reference

hack.chat is anonymous, so the bridge needs no chat credentials, only a channel and a nickname, plus a HiveMind access key and password. All are passed as options to the `hivemind-hackchat-bridge` console script.

## hack.chat parameters

| Option | Meaning |
| --- | --- |
| `--channel` | The hack.chat channel name to join. Channels are created on demand. Anyone at `https://hack.chat/?<channel>` shares it. |
| `--username` | The nickname the bot uses in the channel. Default `Jarbas_BOT`. |

The bridge connects to `wss://hack.chat/chat-ws` and keeps the connection alive with a periodic ping.

## HiveMind credentials

| Option | Meaning | Default |
| --- | --- | --- |
| `--host` | HiveMind hub host (`wss://` or `ws://`). | `ws://127.0.0.1` |
| `--port` | HiveMind hub port. | `5678` |
| `--access-key` | HiveMind access key from `hivemind-core add-client`. | `None` |
| `--password` | HiveMind password from `hivemind-core add-client`. | `None` |
| `--self-signed` | Accept self-signed SSL certificates. | off |
| `--lang` | Language code for forwarded utterances. | `en-us` |

## Message handling

- The bridge forwards every channel message except its own to the hub.
- It strips a leading `@username` mention of the bot before forwarding.
- The sender's nickname travels as `user.hackchat_username` in the HiveMind context. The hub echoes it on the `speak` reply, so the answer can be addressed to the user.
- The bridge also handles `hive.complete_intent_failure`, replying with a fixed "I don't know how to answer that" message.

## Channel presence

On joining, and on user join and leave events, the bot posts greeting and presence messages to the channel, for example "Hello @user". The join and leave callbacks in `JarbasHackChatBridge` emit these.

---
[← Operator setup](operator-setup.md) · [Home](../readme.md) · [Examples →](examples.md)
