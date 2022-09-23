# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added `ws_connect` helper method
- Added a CHANGELOG

### Changed

- Removed dependency on `dfx-apiv2-protos` and thus `protobuf`
- Changed dependency `aiohttp[speedups]` to `aiohttp<4` to simplify installation.
  - Please manually install `aiohttp[speedups]` if needed.

## [0.10.0] - 2022-09-14

### Added

- First tagged release on PyPI

[unreleased]: https://github.com/nuralogix/dfx-apiv2-client-py/compare/v0.10.0...HEAD
[0.10.0]:  https://github.com/nuralogix/dfx-apiv2-client-py/releases/tag/v0.10.0