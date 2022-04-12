import click
import logging

import labbot.logger
from labbot.config import read_instance_config, write_instance_config
from labbot.bot import Bot

@click.group()
def main():
    pass

@main.command(help="Create a new instance")
@click.option("--name", prompt=True, help="Name the instance will be given")
@click.option("--access_token", prompt="Access Token for the Bot account", hide_input=True, help="Access Token to interact with the API")
@click.option("--secret", prompt="Webhook Secret (can be empty)", default="", help="Secret to receive webhook requests [can be empty]")
def setup(**data):
    instance_name = data.pop("name", "").replace(" ", "_").lower()

    if not read_instance_config(instance_name):
        write_instance_config(instance_name, data)
        click.echo(f"You can start your instance by running `lab-bot run {instance_name}`")
    else:
        click.echo(f"an instance with the name {instance_name} already exists")

@main.command(help="Configure an existing instance")
@click.argument('name')
@click.option("--access_token", required=False)
@click.option("--secret", required=False)
def config(name, **data):

    data = {k:v for k,v in data.items() if v}

    conf = read_instance_config(name)
    if conf:
        if data:
            conf.update(data)
            write_instance_config(name, conf)
            click.echo("configured")
        else:
            click.echo("nothing to change")
    else:
        click.echo(f"{name} is not an instance")
    pass

@main.command(help="Run an instance")
@click.option("--port", default=8080, show_default=True, help="change the webhook port")
@click.option("--debug", is_flag=True, default=False, help="enable debug logging")
@click.argument('name')
def run(name, port, debug):
    conf = read_instance_config(name)

    if not conf:
        click.echo(f"{name} is not an instance")
        return

    if debug:
        logger_level = logging.DEBUG
    else:
        logger_level = logging.INFO

    labbot.logger.init(logger_level)

    instance = Bot(
            name=name,
            secret=conf["secret"],
            access_token=conf["access_token"]
        )

    instance.run(
        port=port
    )


if __name__ == "__main__":
    # backup entrypoint for direct execution
    main()