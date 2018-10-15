#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Custom exceptions used by libastr.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from requests import HTTPError


# - [ Exceptions ] -----------------------------------------------------------

class ConfigurationError(Exception):
    """ConfigurationError Exception."""
    pass


class AuthenticationFailure(HTTPError):
    """Authentication Failure Exception."""
    pass


class ResourceNotFound(Exception):
    pass


class PermissionDenied(Exception):
    pass


class APIError(Exception):
    pass


class ArchiveError(Exception):
    """ArchiveError Exception."""
    pass


class PathError(Exception):
    """PathError Exception."""
    pass


class DownloadError(Exception):
    """Error raised when download encountered an issue."""
    pass

