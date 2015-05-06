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

import unittest
import os

from crunchyroll.apis.meta import MetaApi
from crunchyroll.apis.errors import *

CRUNCHYROLL_USERNAME = os.environ.get('CRUNCHYROLL_USERNAME')
CRUNCHYROLL_PASSWORD = os.environ.get('CRUNCHYROLL_PASSWORD')

CREDS_AVAILABLE = CRUNCHYROLL_USERNAME and CRUNCHYROLL_PASSWORD

skip_if_no_creds = unittest.skipUnless(CREDS_AVAILABLE, 'Login credentials not available')

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.api = MetaApi()

    @skip_if_no_creds
    def test_login(self):
        self.api.login(username=CRUNCHYROLL_USERNAME, password=CRUNCHYROLL_PASSWORD)

    def test_login_fail(self):
        with self.assertRaises(ApiLoginFailure):
            self.api.login(username='example-bad-username', password='example-bad-password')

    def test_search(self):
        self._series = self.api.search_anime_series('Space Brothers')[0]
        self.assertEqual('Space Brothers', self._series.name)

    def test_list_media(self):
        self._media = self.api.list_media(self._series)
        self.assertEqual(99, len([ep for ep in self._media if not ep.clip]))
        self.assertEqual('Life Changes, Promises Don\'t')

if __name__ == '__main__':
    unittest.main()
