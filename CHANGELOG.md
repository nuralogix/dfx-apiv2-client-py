# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added endpoint `Auths.request_child_token`
- Added endpoint `Measurements.retrieve_intermediate`

### Changed

- Added `refresh_token_expires_sec` to `Auths.renew_token`, `Auths.renew_user_token`, and `Auths.renew_device_token`
- Added parameters to `Licenses.list`
- Made unnecessary parameters optional for `Measurements.add_data`
- Added `mode` to `Measurements.list`
- Removed unnecessary parameters from `Organizations.update`
- Removed `status_id` and added `region` to `Organizations.list_users`
- Added `refresh_token_expires_sec` and truncate `app_version` to 20 chars for `Organizations.register_license`
- Added `mode` and `region` to `Organizations.list_measurements`
- Added `date` and `end_date` and removed `created_date` from `Organizations.list_profiles`
- Added `token_expires_in_sec` and `refresh_token_expires_in_sec` to `Organizations.login`
- Added parameters to `Studies.list_templates` and `Studies.list`
- Added `status` to `Studies.update`
- Added `token_expires_in_sec` and `refresh_token_expires_in_sec` to `Users.login` and `Users.login_with_phone_code`

### Fixed

- Fixed parameters of `Devices.list`
- Fixed URL of `Devices.retrieve_license_id`
- Fixed URL of `Licenses.get`
- Fixed parameter `date` of `Organizations.list_users`-
- Fixed parameter `status` of `Studies.types`

## [0.14.0] - 2023-03-21

### Removed

- Removed experimental `streaming` mode from `Measurements.create`

## [0.13.0] - 2022-12-22

### Fixed

- Added missing `partner_id` parameter in `Organizations.list_measurements`
- `email` parameter in `Organizations.list_measurements`

## [0.12.0] - 2022-11-03

### Fixed

- `status` parameter in `Studies.list`

### Removed

- All `Meta` endpoints

### Changed

- Changed signatures of `Measurements.add_data` and `Measurements.ws_add_data`
- Deprecated the following endpoints:
  - `Devices.delete` and `Devices.delete_measurements`
  - `Measurements.delete`
  - `Organizations.delete_all_measurements` and `Organizations.delete_measurements_by_partnerid`
  - `Studies.delete_study_measurements`
  - `Users.delete_measurements_by_userid`

## [0.11.1] - 2022-10-07

### Fixed

- Fixed `ws_decode` not handling JSON responses

## [0.11.0] - 2022-09-23

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

[unreleased]: https://github.com/nuralogix/dfx-apiv2-client-py/compare/v0.14.0...HEAD
[0.14.0]: https://github.com/nuralogix/dfx-apiv2-client-py/compare/v0.13.0...v0.14.0
[0.13.0]: https://github.com/nuralogix/dfx-apiv2-client-py/compare/v0.12.0...v0.13.0
[0.12.0]: https://github.com/nuralogix/dfx-apiv2-client-py/compare/v0.11.1...v0.12.0
[0.11.1]: https://github.com/nuralogix/dfx-apiv2-client-py/compare/v0.11.0...v0.11.1
[0.11.0]: https://github.com/nuralogix/dfx-apiv2-client-py/compare/v0.10.0...v0.11.0
[0.10.0]:  https://github.com/nuralogix/dfx-apiv2-client-py/releases/tag/v0.10.0
