# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information
import pathlib

from setuptools import setup

long_description = (pathlib.Path(__file__).parent / "README.md").read_text()

setup(
    name='dfx-apiv2-client',
    author="NuraLogix Corporation",
    url='https://github.com/nuralogix/dfx-apiv2-client-py',
    version='0.11.0',
    packages=['dfx_apiv2_client'],
    install_requires=[
        'aiohttp<4',
    ],
    setup_requires=['wheel'],
    description='dfx-apiv2-client is a Python 3 asyncio client library for the Nuralogix DeepAffex API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license_file='LICENSE.txt',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
)
