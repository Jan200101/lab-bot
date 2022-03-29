import click
from typing import List
from importlib import import_module

from labbot.config import read_config, write_config
from labbot.bot import Bot

@click.group()
def main():
    pass

@main.command(help="Create a new instance")
@click.option("--name", prompt=True, help="Name the instance will be given")
@click.option("--access_token", prompt=True, hide_input=True, help="Access Token to interact with the API")
@click.option("--secret", prompt=True, default="", help="Secret to receive webhook requests [can be empty]")
def setup(**data):
    instance_name = data.pop("name", "").replace(" ", "_").lower()

    if not read_config(instance_name):
        write_config(instance_name, data)
        click.echo(f"You can start your instance by running `lab-bot run {instance_name}`")
    else:
        click.echo(f"an instance with the name {instance_name} already exists")

@main.command(help="Configure an existing instance")
@click.argument('name')
@click.option("--access_token", required=False)
@click.option("--secret", required=False)
def config(name, **data):

    data = {k:v for k,v in data.items() if v}

    conf = read_config(name)
    if conf:
        if data:
            conf.update(data)
            write_config(name, conf)
            click.echo("configured")
        else:
            click.echo(f"nothing to change")
    else:
        click.echo(f"{name} is not an instance")
    pass


def load_addons(instance: Bot, addons: List[str]):
    for addon in addons:
        import_module(f"labbot.addons.{addon}").setup(instance)
        click.echo(f"Imported {addon}")

@main.command(help="Run an instance")
@click.option("--port", default=8080)
@click.argument('name')
def run(name, port):
    conf = read_config(name)

    if not conf:
        click.echo(f"{name} is not an instance")
        return

    instance = Bot(
            secret=conf["secret"],
            access_token=conf["access_token"]
        )

    load_addons(instance, [
            "merge-label"
        ])

    click.echo(f"Started {name}")

    instance.run(
        port=port
    )



if __name__ == "__main__":
    main()