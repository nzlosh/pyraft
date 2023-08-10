# coding: utf-8

import setuptools
from setuptools import setup
from os import path

__version__ = "0.2.0"

requirements = [req.strip() for req in open("requirements.txt").readlines()]

short_description = "python raft implementation with resp interface"

setup(
    name="pyraft",
    packages=setuptools.find_packages(),
    version=__version__,
    description=short_description,
    long_description=short_description,
    author="PyRaft collaborators",
    author_email="nzlosh@yahoo.com",
    license="MIT",
    url="https://github.com/nzlosh/pyraft",
    keywords=["python", "raft", "replication", "pyraft"],
    install_requires=requirements,
    python_requires=">=3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
