#!/usr/bin/env python
from setuptools import setup, find_packages
from rpcudp import version

setup(
    name="rpcudp",
    version=version,
    description="RPC via UDP",
    author="Brian Muller",
    author_email="bamuller@gmail.com",
    license="MIT",
    url="http://github.com/bmuller/rpcudp",
    packages=find_packages(),
    requires=["twisted.internet.protocol.DatagramProtocol"],
    install_requires=['twisted>=12.0']
)
