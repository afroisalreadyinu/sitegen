"""
Console entry points of sitegen
"""
import os

import click
import toml
from schema import And, Regex, Schema, SchemaError

from sitegen.content import generate_site
from sitegen.monitor import monitor


@click.group()
def main():
    pass


ConfigSchema = Schema(
    {
        "site": {
            "url": And(str, len, Regex(r"^https?://\w*")),
            "title": And(str, len),
            "author": And(str, len),
            "locale": And(str, len),
        }
    }
)


class SitegenConfigurationError(Exception):
    pass


def load_config():
    config = toml.load("site.toml")
    try:
        validated = ConfigSchema.validate(config)
    except SchemaError as schema_error:
        raise SitegenConfigurationError(schema_error.code) from None
    return validated


@main.command()
def generate():
    config = load_config()
    generate_site(os.getcwd(), config)


@main.command()
def watch():
    config = load_config()
    monitor(os.getcwd(), config)
