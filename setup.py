#!/usr/bin/env python
from setuptools import setup, find_packages
import rpcudp

setup(
    name="rpcudp",
    version=rpcudp.__version__,
    description="RPC via UDP",
    author="Brian Muller",
    author_email="bamuller@gmail.com",
    license="MIT",
    url="http://github.com/bmuller/rpcudp",
    packages=find_packages(),
    install_requires=["u-msgpack-python>=1.5"]
)
