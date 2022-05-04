import click
import logging
from typing import List
from importlib import import_module

import labbot.bot
import labbot.config
import labbot.logger

DEFAULT_ADDONS = [
    "merge-label",
    "approve-merge"
]

@click.group()
def main():
    pass

@main.command(help="Create a new instance")
@click.option("--name", prompt=True, help="Name the instance will be given")
@click.option("--access_token", prompt="Access Token for the Bot account", hide_input=True, help="Access Token to interact with the API")
@click.option("--secret", prompt="Webhook Secret (can be empty)", default="", help="Secret to receive webhook requests (can be empty)")
def setup(**data):
    instance_name = data.pop("name", "").replace(" ", "_").lower()
    data["addons"] = DEFAULT_ADDONS
    data["addon_path"] = ""

    if not labbot.config.read_instance_config(instance_name):
        labbot.config.write_instance_config(instance_name, data)
        click.echo(f"You can start your instance by running `lab-bot run {instance_name}`")
    else:
        click.echo(f"an instance with the name {instance_name} already exists")

@main.command(help="Configure an existing instance")
@click.argument('name')
@click.option("--access_token", required=False)
@click.option("--secret", required=False)
def config(name, **data):

    data = {k:v for k,v in data.items() if v}

    conf = labbot.config.read_instance_config(name)
    if conf:
        if data:
            conf.update(data)
            labbot.config.write_instance_config(name, conf)
            click.echo("configured")
        else:
            click.echo(f"nothing to change")
    else:
        click.echo(f"{name} is not an instance")
    pass


@main.command(help="Run an instance")
@click.option("--port", default=8080, show_default=True, help="change the webhook port")
@click.option("--debug", is_flag=True, default=False, help="enable debug logging")
@click.argument('name')
def run(name, port, debug: bool):
    conf = labbot.config.read_instance_config(name)

    if not conf:
        click.echo(f"{name} is not an instance")
        return

    if debug:
        logger_level = logging.DEBUG
    else:
        logger_level = logging.INFO

    labbot.logger.init(logger_level)

    instance = labbot.bot.Bot(
            name=name,
            config=conf,
            secret=conf["secret"],
            access_token=conf["access_token"]
        )

    instance.run(
        port=port
    )

@main.command(name="list", help="List all available instances")
def list_instances():
    print("Available Instances:")
    for ins in labbot.config.list_instances():
        print(f"- {ins}")

if __name__ == "__main__":
    main()