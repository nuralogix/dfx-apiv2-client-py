# Publishing

If you wish to publish to a private instance of PyPI:

Install [build](https://github.com/pypa/build) and
[twine](https://twine.readthedocs.io/en/stable/) if you don't have them.

```shell
pip install --upgrade build twine
```

## Create distributions and check

```shell
rm dist/*                           # Clean dist folder, on Window use `del /s /q dist\*`
python -m build                     # Create wheel and source distribution using `build` tool
twine check --strict dist/*         # Check the created distributions and fix any issues if needed
```

## Publish on private PyPI

You will need to set `TWINE_REPOSITORY`, `TWINE_REPOSITORY_URL` and other
necessary environment variables or use the
[register command](https://twine.readthedocs.io/en/stable/#twine-register)
documented here.

```shell
git checkout master                 # Releases should always be from main branch
git tag vX.Y.Z                      # Tag the release on the main branch
rm dist/*                           # Clean dist folder, on Window use `del /s /q dist/*`
python -m build                     # Create wheel and source distribution
twine upload --sign dist/*          # Sign and upload to PyPI
```
