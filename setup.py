from setuptools import setup

setup(
    name='dfx-apiv2-client',
    version='0.0.1',
    packages=['dfx_apiv2_client'],
    install_requires=['aiohttp[speedups]'],
    setup_requires=['wheel'],
    description='dfx-apiv2-client is an async client for the DeepAffex API.',
    entry_points={
        'console_scripts': [
            'apiexample = apiexample:cmdline',
        ],
    },
)
