# Copyright (c) Nuralogix. All rights reserved. Licensed under the MIT license.
# See LICENSE.txt in the project root for license information

from setuptools import setup

setup(
    name='dfx-apiv2-client',
    version='0.3.2',
    packages=['dfx_apiv2_client'],
    install_requires=[
        'aiohttp[speedups]',
        'dfx-apiv2-protos @ https://github.com/nuralogix/dfx-apiv2-protos-python/tarball/master',
    ],
    setup_requires=['wheel'],
    description='dfx-apiv2-client is an async client for the DeepAffex API.',
)
