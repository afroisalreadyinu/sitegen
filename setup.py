import os

from setuptools import setup

setup(
    name = "sitegen",
    version = "0.4.0",
    author = "Ulas Turkmen",
    description = "Site generator",
    packages=['sitegen'],
    license = "MIT",
    entry_points = {'console_scripts': ['sitegen = sitegen.main:main']}
)
