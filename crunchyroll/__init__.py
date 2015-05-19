#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013  Alex Headley  <aheadley@waysaboutstuff.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
Crunchyroll Library
-------------------

A library to interface with Crunchyroll's various APIs and utilites to work
with the returned data

Set environment var CRUNCHYROLL_DEBUG to '1' to enable debug logging to
stderr

:copyright: (c) 2013 by Alex Headley
:license: GNU General Public License v2+, see LICENCE for more details
"""

__title__           = 'crunchyroll'
__version__         = '1.0.1'
__author__          = 'Alex Headley'
__author_email__    = 'aheadley@waysaboutstuff.com'
__license__         = 'GNU General Public License v2+'
__copyright__       = 'Copyright 2013 Alex Headley'
__url__             = 'https://github.com/aheadley/python-crunchyroll'
__description__     = """
A library to interface with Crunchyroll's various APIs and utilites to work
with the returned data
""".strip()

# set default logging handler
import os
import logging

from crunchyroll.util import NullHandler, LOG_FORMAT

logger = logging.getLogger(__title__)

if os.environ.get('CRUNCHYROLL_DEBUG', False):
    _log_handler = logging.StreamHandler()
    _log_handler.setFormatter(LOG_FORMAT)
    _log_level = logging.DEBUG
else:
    _log_handler = NullHandler()
    _log_level = logging.WARN

logger.setLevel(_log_level)
logger.addHandler(_log_handler)

logger.debug('%s module init finished', __title__)
