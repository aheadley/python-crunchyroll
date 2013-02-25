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

from ..apis import ApiInterface
from .android import AndroidApi
from .ajax import AjaxApi
from ..constants import META, AJAX, ANDROID
from .errors import *

class MetaApi(ApiInterface):
    """High level interface to crunchyroll
    """

    def __init__(self, state=None):
        self._ajax_api = AjaxApi()
        self._android_api = AndroidApi()

    @property
    def logged_in(self):
        return self._ajax_api.logged_in and self._android_api.logged_in
