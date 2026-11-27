import click

from hackchat_bridge import JarbasHackChatBridge


def connect_hackchat_to_hivemind(channel,
                                 username="Jarbas_BOT",
                                 access_key=None,
                                 host="ws://127.0.0.1",
                                 port=5678,
                                 password=None,
                                 self_signed=False,
                                 lang="en-us"):
    """Connect a hack.chat channel to a HiveMind hub and block forever."""
    bridge = JarbasHackChatBridge(username=username,
                                  channel=channel,
                                  access_key=access_key,
                                  host=host,
                                  port=port,
                                  password=password,
                                  self_signed=self_signed,
                                  lang=lang)
    bridge.run()


@click.command()
@click.option("--channel", required=True, help="hack.chat channel name to join")
@click.option("--username", default="Jarbas_BOT", help="bot nickname shown in the channel")
@click.option("--access-key", default=None, help="HiveMind access key")
@click.option("--password", default=None, help="HiveMind password")
@click.option("--host", default="ws://127.0.0.1", help="HiveMind hub host (ws:// or wss://)")
@click.option("--port", default=5678, type=int, help="HiveMind hub port (default 5678)")
@click.option("--self-signed", is_flag=True, help="accept self signed ssl certificates")
@click.option("--lang", default="en-us", help="language code for utterances")
def main(channel, username, access_key, password, host, port, self_signed, lang):
    """Relay a hack.chat channel to a HiveMind hub."""
    connect_hackchat_to_hivemind(channel=channel,
                                 username=username,
                                 access_key=access_key,
                                 host=host,
                                 port=port,
                                 password=password,
                                 self_signed=self_signed,
                                 lang=lang)


if __name__ == '__main__':
    main()
