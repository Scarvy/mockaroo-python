# Changelog

## [2.0.0] - 2023-10-17

### New

- ✨ New CLI using 🌈 `rich-click` to easily execute Mockaroo API commands in the terminal:
  - `types` - See list of Mockaroo data types in a `rich` styled table
  - `upload` and `delete` - datasets from Mockaroo 🦘

### Added

- Additional unit tests for increase code coverage to ~98% 💪

### Changed

- Switch linter to `ruff`

### Fixed

- Fix `types` method "Returns" docstring
- Fix `types` method unit test

## [1.1.0] - 2023-10-15

### Added

- Add an attribute `last_response` to the `Client` class. Help diagnose client requests to the API.

  - ```python
        self.last_reponse = {
            "method": method,
            "url": url,
            "request": kwargs, 
            "error": None,
        }
    ```

- Add two new unit tests for the `generate` method. Test for different formats (eg. ‘csv’, ‘txt’).
- Add more parameters to `test_get_url`.
- Add unit test `test_warning_for_no_api_key` for `api_key` property
- Add more detail to the "Usage" section of the README

### Removed

- Remove the `count` key in the `_get_url` method.
- Remove `raise_for_status` function in `__http_request` method. The function was preventing `MockarooExceptions` from being raised properly.

### Fixed

- Fix `__htttp_request` not raising `MockarooExceptions`.
- Fix the mistake in the `generate` method when returning JSON data. Keyword argument using the wrong keyword “fields” instead of “json”.

## [1.0.0] - 2023-10-11

### Added

- Initial release
