# Configuration & Credentials Reference

hack.chat is anonymous, so the bridge needs no chat credentials — only a channel and a nickname, plus a HiveMind access key. All are passed to `connect_hackchat_to_hivemind(...)` in `hackchat_bridge/__main__.py`.

## hack.chat parameters

| Parameter | Meaning |
| --- | --- |
| `channel` | The hack.chat channel name to join. Channels are created on demand; anyone at `https://hack.chat/?<channel>` shares it. |
| `username` | The nickname the bot uses in the channel. Default `Jarbas_BOT`. |

The bridge connects to `wss://hack.chat/chat-ws` and keeps the connection alive with a periodic ping.

## HiveMind credentials

| Parameter | Meaning | Default |
| --- | --- | --- |
| `host` | HiveMind hub host (`wss://` or `ws://`). | `wss://127.0.0.1` |
| `port` | HiveMind hub port. | `5678` |
| `key` | HiveMind access key from `hivemind-core add-client`. | `unsafe` |
| `crypto_key` | Optional pre-shared payload crypto key. | `None` |
| `name` | Terminal name reported to the hub. | `JarbasHackChatBridge` |

## Message handling

- Every channel message except the bot's own is forwarded to the hub.
- A leading `@username` mention of the bot is stripped before forwarding.
- The sender's nickname is carried as `user.hackchat_username` in the HiveMind context; the hub echoes it on the `speak` reply so the answer can be addressed to the user.
- The bridge also handles `hive.complete_intent_failure`, replying with a fixed "I don't know how to answer that" message.

## Channel presence

On joining and on user join/leave events the bot posts greeting and presence messages to the channel (for example "Hello @user"). These are emitted by the join/leave callbacks in `JarbasHackChatBridge`.
