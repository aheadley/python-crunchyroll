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

import locale
import json
import logging

import requests

from .android import AndroidApi
from ..constants import BOXEE
from .errors import *

logger = logging.getLogger('crunchyroll.apis.boxee')

class BoxeeApi(AndroidApi):
    """Boxee HTML5 API interface

    @link http://www.crunchyroll.com/boxee_app/
    This is pretty much exactly the Android API with an extra proxy URL between
    the Android API and the the Boxee app. There probably isn't anything
    this can get that the Android API can't so it's probably not worth it to
    finish this
    """

    def __init__(self, state=None):
        super(BoxeeApi, self).__init__(state)
        self._request_headers = None

    def _get_base_params(self):
        base_params = {
            'locale':       self._get_locale(),
            'device_id':    BOXEE.DEVICE_ID,
            'device_type':  BOXEE.APP_PACKAGE,
            'access_token': BOXEE.ACCESS_TOKEN,
            'version':      BOXEE.APP_CODE,
        }
        base_params.update(dict((k, v) \
            for k, v in self._state_params.iteritems() \
                if v is not None))
        return base_params

    def _build_request_url(self, secure, api_method, version):
        android_url = super(BoxeeApi, self)._build_request_url(
            secure, api_method, version)
        # TODO: this is wrong
        return android_url
