set positional-arguments
set shell := ["bash", "-uc"]

default:
    @just --list

check:
    ruff format --check src
    ruff format --check tests

format:
    ruff check --select I --fix src
    ruff format src
    ruff check --select I --fix tests
    ruff format tests