# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

from setuptools import setup

setup(
    name='dfx-apiv2-client',
    version='1.0.0',
    packages=['dfx_apiv2_client'],
    install_requires=[
        'aiohttp[speedups]',
    ],
    setup_requires=['wheel'],
    description='dfx-apiv2-client is an async client for the DeepAffex API.',
)
