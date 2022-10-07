# DeepAffex APIv2 Python Client Library

`dfx-apiv2-client` is a Python 3 asyncio client library for the NuraLogix
DeepAffex API.

For usage examples, please see https://github.com/nuralogix/dfx-demo-py

For more information, please visit https://deepaffex.ai/developers-api

## Publishing

Install [wheel](https://github.com/pypa/wheel) and
[twine](https://twine.readthedocs.io/en/stable/) if you don't have them.

```shell
pip install --upgrade twine wheel
```

## Create distributions and check

```shell
rm dist/*                           # Clean dist folder, on Window use `del /s /q dist\*`
python setup.py bdist_wheel sdist   # Create wheel and source distribution
twine check --strict dist/*         # Check the created distributions and fix any issues if needed
```

## Publish on PyPI

You will need PyPI credentials

```shell
git checkout master                 # Releases should always be from main branch
git tag vX.Y.Z                      # Tag the release on the main branch
rm dist/*                           # Clean dist folder, on Window use `del /s /q dist/*`
python setup.py bdist_wheel sdist   # Create wheel and source distribution
twine upload --sign dist/*          # Sign and upload to PyPI
```
