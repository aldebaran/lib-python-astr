#!/usr/bin/env python
# coding: utf-8

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")
else:
    try:
        from .resources import Browser, Archive, ArchiveCategory
        from .client import AstrClient
    except ImportError as e:
        errmsg = "Can't import the library"
        raise Exception(errmsg).with_traceback(e.__traceback__)

name = "lib-python-astr"
