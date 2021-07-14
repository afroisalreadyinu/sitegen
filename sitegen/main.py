import os

import toml
import click

@click.group()
def main():
    pass

@main.command()
def generate():
    config = toml.load("site.toml")
    context = {'title': config['site']['title']}
    from sitegen.content import generate_site
    generate_site(os.getcwd(), context)

@main.command()
def watch():
    config = toml.load("site.toml")
    context = {'title': config['site']['title']}
    from sitegen.monitor import monitor
    monitor(os.getcwd(), context)
