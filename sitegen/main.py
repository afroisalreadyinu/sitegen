import os

import toml
import click
from schema import Schema, And, SchemaError, Regex

@click.group()
def main():
    pass

ConfigSchema = Schema({'site': {'url': And(str, len, Regex(r"^https?://\w*")),
                                'title': And(str, len),
                                'author': And(str, len),
                                'locale': And(str, len)}})

class SitegenConfigurationError(Exception):
    pass

def load_config():
    config = toml.load("site.toml")
    try:
        validated = ConfigSchema.validate(config)
    except SchemaError as se:
        raise SitegenConfigurationError(se.code) from None
    return validated


@main.command()
def generate():
    config = load_config()
    from sitegen.content import generate_site
    generate_site(os.getcwd(), config)

@main.command()
def watch():
    config = load_config()
    from sitegen.monitor import monitor
    monitor(os.getcwd(), config)
