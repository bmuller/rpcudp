# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Version 5.0.1 (2025-03-30)
### Enhancements
 * Moved to `uv` for dependency management and `ruff` for formatting / styling / linting

## Version 5.0.0 (2023-11-26)
### Enhancements
 * Moved to Github Actions for tests, fixed co-routine issue in latest version of Python

## Version 4.0.2 (2021-02-05)
### Enhancements
 * Added a MANIFEST.in so the source distribution can retain necessary requirements.txt file

## Version 4.0.1 (2020-05-02)
### Bug Fixes
 * Fixed a few typos and incorrect docs

## Version 4.0.0 (2019-07-03)
### Enhancements
 * Updates to internal naming conventions

### Deprecations
 * No longer supporting version of Python before 3.5

## Version 2.0.0 (2015-11-22)

### Enhancements
 * Support for Python 3

### Deprecations
With version 2.0 compatibility is broken with previous versions. In version 2.0 the method name when making a remote call is always packed as a unicode string. In previous versions, the type of string that method name was depended on the Python version. In order to make instances running on Python 2 (only versions before 3.0 worked with Python 2) and Python 3 compatible with each other the method name is now encoded as a unicode string before being packed, which ensures that [u-msgpack-python](https://github.com/vsergeev/u-msgpack-python) will always pack the it the same way. See [u-msgpack-python#behaviour-notes](https://github.com/vsergeev/u-msgpack-python#behavior-notes) for more information.

If you intend to have instances running on both Python 2 and Python 3 communicating with each other make sure that all strings in the arguments you send are unicode encoded as well to ensure compatibility.
