# Setup Walkthrough

From nothing to a working hack.chat bot backed by a HiveMind hub.

## How the bridge fits together

The bridge is a HiveMind satellite with two connections:

- **To hack.chat** — it opens a websocket to `wss://hack.chat/chat-ws` and joins a channel with a nickname. hack.chat is anonymous, so no credentials are needed.
- **To the HiveMind hub** — it connects as a HiveMind terminal using an access key.

Each channel message (other than the bot's own) becomes a `recognizer_loop:utterance` sent to the hub. The sender's nickname travels in the message context, so the hub's `speak` reply is posted back to the channel addressed to that user.

```
hack.chat channel  ⇄  bridge  ⇄  HiveMind hub  ⇄  OVOS pipeline / skills
```

## Step 1 — Stand up a HiveMind hub

Install and run [hivemind-core](https://github.com/JarbasHiveMind/HiveMind-core):

```bash
pip install hivemind-core
hivemind-core listen
```

The hub listens on port `5678` by default.

## Step 2 — Register the bridge as a client

On the hub machine:

```bash
hivemind-core add-client --name hackchat-bridge \
  --access-key "your-access-key" --password "your-password"
```

Keep the access key. List clients with `hivemind-core list-clients`.

## Step 3 — Pick a channel and nickname

hack.chat channels are created on the fly — just choose a name. Anyone who opens `https://hack.chat/?<channel>` is in that channel. Pick a nickname for the bot.

## Step 4 — Install the bridge

```bash
git clone https://github.com/JarbasHiveMind/HiveMind-HackChatBridge
cd HiveMind-HackChatBridge
pip install -r requirements.txt
pip install websocket-client
```

`websocket-client` is imported by `hackchat.py` but not pinned in `requirements.txt`; install it explicitly.

## Step 5 — Configure and run

Edit the call to `connect_hackchat_to_hivemind(...)` at the bottom of `hackchat_bridge/__main__.py` with your `channel`, bot `username`, and HiveMind `host`/`port`/`key`. Then:

```bash
python -m hackchat_bridge
```

## Step 6 — Talk to it

Open `https://hack.chat/?<channel>` in a browser, join with any nickname, and type a message. The bridge forwards it to the hub and posts the spoken answer back as `@user , <answer>`.
