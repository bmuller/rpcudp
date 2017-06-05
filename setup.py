#!/usr/bin/env python
from setuptools import setup, find_packages
from rpcudp import version

setup(
    name="rpcudp",
    version=version,
    description="RPC via UDP",
    long_description=open("README.markdown").read(),
    author="Brian Muller",
    author_email="bamuller@gmail.com",
    license="MIT",
    url="http://github.com/bmuller/rpcudp",
    packages=find_packages(),
    requires=[
        "twisted.internet.protocol.DatagramProtocol", "umsgpack", "future"
    ],
    install_requires=['twisted>=12.0', "u-msgpack-python>=1.5", "future>=0.6"]
)
