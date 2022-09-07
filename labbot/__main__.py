import click
import logging
from typing import List
from importlib import import_module
import json
import shutil

import labbot.bot
import labbot.config
import labbot.logger

DEFAULT_ADDONS = [
    "merge-label",
    "approve-merge",
    "merge-stable",
    "dashboard"
]

@click.group()
def main():
    pass

@main.command(help="Create a new instance")
@click.option("--name", prompt=True, help="Name the instance will be given")
@click.option("--access_token", prompt="Access Token for the Bot account", hide_input=True, help="Access Token to interact with the API")
@click.option("--secret", prompt="Webhook Secret (optional)", default="", help="Secret to receive webhook requests (optional)")
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
@click.option("--access_token", required=False, help="Access Token to interact with the API")
@click.option("--secret", required=False, help="Secret to receive webhook requests (can be empty)")
@click.option("--addons", multiple=True, required=False, help="List of addons to load")
@click.option("--addon_path", required=False, help="Path to load custom addons from")
@click.option("--print", is_flag=True, required=False, help="Print the current config with redacted values")
def config(name, **data):

    data = {k:v for k,v in data.items() if v}
    print_config = data.pop("print", False)

    conf = labbot.config.read_instance_config(name)
    if conf:
        if data:
            conf.update(data)
            labbot.config.write_instance_config(name, conf)
            click.echo("configured")
        elif print_config:
            conf["access_token"] = (round(len(conf["access_token"]) / 4) * 4) * "*"
            conf["secret"] = (round(len(conf["secret"]) / 4) * 4) * "*"
            click.echo(json.dumps(conf, indent=4))
        else:
            click.echo("run with `--help` to show usage")
    else:
        click.echo(f"{name} is not an instance")
    pass


@main.command(help="Run an instance")
@click.option("--port", default=8080, show_default=True, help="change the webhook port")
@click.option("--debug", is_flag=True, default=False, help="enable debug logging")
@click.argument('name')
def run(name, port: str, debug: bool):
    conf = labbot.config.read_instance_config(name)

    if not conf:
        click.echo(f"{name} is not an instance")
        return

    if debug:
        logger_level = logging.DEBUG
    else:
        logger_level = logging.INFO

    labbot.logger.init(logger_level)

    access_token = conf.pop("access_token")
    secret = conf.pop("secret", "")

    instance = labbot.bot.Bot(
            name=name,
            config=conf,
            access_token=access_token,
            secret=secret,
        )

    instance.run(
        port=port
    )

@main.command(name="list", help="List all available instances")
def list_instances():
    print("Available Instances:")
    for ins in labbot.config.list_instances():
        print(f"- {ins}")

@main.command(name="remove", help="Remove an instance")
@click.argument('name')
@click.option('--yes', is_flag=True, expose_value=False,
              prompt='Are you sure you want to remove the instance?')
def remove_instance(name):
    try:
        shutil.rmtree(labbot.config.instance_config_dir(name))
    except FileNotFoundError:
        print("Instance not found")

if __name__ == "__main__":
    main()