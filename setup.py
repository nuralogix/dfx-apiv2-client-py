from setuptools import setup

setup(
    name='dfxapi',
    version='0.0.1',
    packages=['dfx_apiv2_client'],
    install_requires=['aiohttp[speedups]'],
    setup_requires=['wheel'],
    description='dfx_apiv2_client is an async client for the DeepAffex API.',
    entry_points={
        'console_scripts': [
            'apiexample = apiexample:cmdline',
        ],
    },
)
