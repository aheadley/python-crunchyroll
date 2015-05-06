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

import json
import logging

import requests

from crunchyroll.apis import ApiInterface
from crunchyroll.constants import AJAX
from crunchyroll.apis.errors import *

logger = logging.getLogger('crunchyroll.apis.ajax')

def make_ajax_api_method(req_method, secure=False):
    def outer_func(func):
        def inner_func(self, **kwargs):
            kwargs['req'] = 'RpcApi' + func.__name__
            kwargs['current_page'] = AJAX.API_CURRENT_PAGE
            req_url = self._build_request_url(secure)
            req_func = self._build_request(req_method, req_url, secure, params=kwargs)
            try:
                response = func(self, req_func)
                self._last_response = response
            except ApiLoginFailure as err:
                raise err
            except Exception as err: # TODO: make this more specific
                logger.warn('Caught exception of class: %s', err.__class__.__name__)
                raise ApiNetworkException(err)
            if not (response.ok and response.headers['Content-Type'] == 'text/xml'):
                raise ApiBadResponseException(response)
            else:
                return response.content
        return inner_func
    return outer_func

class AjaxApi(ApiInterface):
    """AJAX call API
    """

    METHOD_POST = 'POST'
    METHOD_GET  = 'GET'

    def __init__(self, state=None):
        self._connector = requests.Session()
        self._last_response = None
        if state is not None:
            self.set_state(state)

    def _build_request_url(self, secure):
        proto = AJAX.PROTOCOL_SECURE if secure else AJAX.PROTOCOL_INSECURE
        return AJAX.API_URL.format(protocol=proto)

    def _build_request(self, req_method, req_url, secure, params):
        def req_func():
            logger.debug('Sending %s request to "%s" with params: %r',
                req_method, req_url, params)
            try:
                func = getattr(self._connector, req_method.lower())
            except AttributeError:
                raise ApiException('Invalid request method')
            try:
                if secure and req_method == self.METHOD_POST:
                    # wouldn't make sense to send data on a GET request
                    resp = func(req_url, data=params)
                else:
                    resp = func(req_url, params=params)
            except requests.RequestException as err:
                raise ApiNetworkException(err)
            logger.debug('Received response code: %d', resp.status_code)
            return resp
        return req_func

    @property
    def session_started(self):
        return True

    @property
    def logged_in(self):
        return AJAX.COOKIE_USERID in self._connector.cookies

    def get_state(self):
        state_string = json.dumps(dict(self._connector.cookies))
        logger.debug('Generated state: %s', state_string)
        return state_string

    def set_state(self, state):
        logger.debug('Loading state: %s', state)
        cookie_jar = json.loads(state)
        self._connector.cookies.update(cookie_jar)

    @make_ajax_api_method(METHOD_POST, True)
    def User_Login(self, req_func):
        """
        @param str name     username or email address
        @param str password user's password
        @param str fail_url (optional) URL to redirect to after login
        """
        response = req_func()
        if not self.logged_in:
            raise ApiLoginFailure(response)
        return response

    @make_ajax_api_method(METHOD_POST)
    def Subtitle_GetXml(self, req_func):
        """Get just the <subtitle/> tag info

        @param int subtitle_script_id
        """
        return req_func()

    @make_ajax_api_method(METHOD_POST)
    def Subtitle_GetListing(self, req_func):
        """
        @param int media_id
        """
        return req_func()

    @make_ajax_api_method(METHOD_POST)
    def VideoEncode_GetStreamInfo(self, req_func):
        """
        @param int video_encode_quality
        @param int video_format
        @param int media_id
        """
        return req_func()

    @make_ajax_api_method(METHOD_POST)
    def VideoPlayer_GetStandardConfig(self, req_func):
        """
        @param int media_id
        @param int video_format
        @param int video_quality
        @param int auto_play        (optional)
        @param str aff              (optional)
        @param int show_pop_out_controls    (optional)
        @param str pop_out_disable_message  (optional)
        """
        return req_func()

    @make_ajax_api_method(METHOD_POST)
    def VideoPlayer_GetChromelessConfig(self, req_func):
        """
        @param int media_id
        """
        return req_func()

    @make_ajax_api_method(METHOD_POST)
    def VideoPlayer_GetMediaMetadata(self, req_func):
        """
        @param int media_id
        @param str video_format
        @param str video_encode_quality
        """
        return req_func()

    @make_ajax_api_method(METHOD_GET)
    def VideoPlayer_GetAutoAdvanceTarget(self, req_func):
        """
        @param int media_id
        """
        return req_func()

    @make_ajax_api_method(METHOD_POST)
    def Media_GetRecommendedMedia(self, req_func):
        """
        @param int media_id
        """
        return req_func()
