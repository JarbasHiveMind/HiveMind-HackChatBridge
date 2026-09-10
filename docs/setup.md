# Setup Walkthrough

From nothing to a working hack.chat bot backed by a HiveMind hub.

## How the bridge fits together

The bridge is a HiveMind satellite with two connections:

- **To hack.chat.** It opens a websocket to `wss://hack.chat/chat-ws` and joins a channel with a nickname. hack.chat is anonymous, so no credentials are needed.
- **To the HiveMind hub.** It connects with a `HiveMessageBusClient`, using an access key and a password.

Each channel message, other than the bot's own, becomes a `recognizer_loop:utterance` sent to the hub. The sender's nickname travels in the message context, so the hub's `speak` reply is posted back to the channel, addressed to that user.

```
hack.chat channel  ⇄  bridge  ⇄  HiveMind hub  ⇄  OVOS pipeline / skills
```

## Step 1: stand up a HiveMind hub

Install and run [hivemind-core](https://github.com/JarbasHiveMind/HiveMind-core):

```bash
pip install hivemind-core
hivemind-core listen
```

The hub listens on port `5678` by default.

## Step 2: register the bridge as a client

On the hub machine, run:

```bash
hivemind-core add-client --name hackchat-bridge \
  --access-key "your-access-key" --password "your-password"
```

Keep the access key. List clients with `hivemind-core list-clients`.

A freshly registered client can connect, but the hub denies every message type until you whitelist it. Skipping this is the most common reason a bridge connects but never replies:

```bash
hivemind-core allow-msg recognizer_loop:utterance hackchat-bridge
hivemind-core allow-msg speak hackchat-bridge
```

## Step 3: pick a channel and nickname

hack.chat channels are created on the fly. Just choose a name. Anyone who opens `https://hack.chat/?<channel>` is in that channel. Pick a nickname for the bot.

## Step 4: install the bridge

```bash
pip install HiveMind-HackChatBridge
```

## Step 5: run

Pass your `channel`, bot `username`, and HiveMind `host`/`port`/`access-key`/`password` on the command line:

```bash
hivemind-hackchat-bridge \
  --channel your_channel \
  --username Jarbas_BOT \
  --access-key "your-access-key" \
  --password "your-password" \
  --host ws://127.0.0.1 \
  --port 5678
```

## Step 6: talk to it

Open `https://hack.chat/?<channel>` in a browser, join with any nickname, and type a message. The bridge forwards it to the hub and posts the spoken answer back as `@user , <answer>`.

---
[Home](../readme.md) · [Operator setup →](operator-setup.md)
