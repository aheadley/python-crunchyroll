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
import functools

import requests

from crunchyroll.apis import ApiInterface
from crunchyroll.constants import ANDROID_MANGA
from crunchyroll.apis.errors import *
from crunchyroll.util import iteritems

logger = logging.getLogger('crunchyroll.apis.android_manga')

def build_api_method(req_method, secure=False, method_name=None):
    def outer_func(func):
        @functools.wraps(func)
        def inner_func(self, **kwargs):
            if method_name is not None:
                req_url = self._build_request_url(secure, method_name)
            else:
                req_url = self._build_request_url(secure, func.__name__)
            req_func = self._build_request(req_method, req_url, params=kwargs)
            response = req_func()
            func(self, response)
            return response
        return inner_func
    return outer_func

class AndroidMangaApi(ApiInterface):
    """
    """

    METHOD_GET          = 'GET'
    METHOD_POST         = 'POST'

    def __init__(self, state=None):
        """
        """

        self._connector = requests.Session()
        self._request_headers = {}
        self._state_params = {
            'session_id':   None,
            'auth':         None,
            'user':         None,
        }
        self._user_data = None
        self._last_response = None
        self._session_ops = []

        if state is not None:
            self.set_state(state)
        logger.info('Initialized state: %r', self._state_params)


    def _get_base_params(self):
        """
        """

        base_params = {
            # these two are required for every request
            'device_type':      ANDROID_MANGA.DEVICE_TYPE,
            'api_ver':          ANDROID_MANGA.API_VER,
            # these are only used for starting the session and should probably
            # not be in this list
            'device_id':        ANDROID_MANGA.DEVICE_ID,
            'access_token':     ANDROID_MANGA.ACCESS_TOKEN,
        }

        base_params.update(dict((k, v) \
            for k, v in iteritems(self._state_params) \
                if v is not None))

        return base_params

    def _do_post_request_tasks(self, response_data):
        """Handle actions that need to be done with every response

        I'm not sure what these session_ops are actually used for yet, seems to
        be a way to tell the client to do *something* if needed.
        """
        try:
            sess_ops = response_data.get('ops', [])
        except AttributeError:
            pass
        else:
            self._session_ops.extend(sess_ops)

    def _build_request(self, method, url, params=None):
        """Build a function to do an API request

        "We have to go deeper" or "It's functions all the way down!"
        """
        full_params = self._get_base_params()
        if params is not None:
            full_params.update(params)
        try:
            request_func = lambda u, d: \
                getattr(self._connector, method.lower())(u, params=d,
                    headers=self._request_headers)
        except AttributeError:
            raise ApiException('Invalid request method')
        # TODO: need to catch a network here and raise as ApiNetworkException

        def do_request():
            logger.debug('Sending %s request "%s" with params: %r',
                method, url, full_params)
            try:
                resp = request_func(url, full_params)
                logger.debug('Received response code: %d', resp.status_code)
            except requests.RequestException as err:
                raise ApiNetworkException(err)

            try:
                resp_json = resp.json()
            except TypeError:
                resp_json = resp.json

            method_returns_list = False
            try:
                resp_json['error']
            except TypeError:
                logger.warn('Api method did not return map: %s', method)
                method_returns_list = True
            except KeyError:
                logger.warn('Api method did not return map with error key: %s', method)

            if method_returns_list is None:
                raise ApiBadResponseException(resp.content)
            elif method_returns_list:
                data = resp_json
            else:
                try:
                    if resp_json['error']:
                        raise ApiError('%s: %s' % (resp_json['code'], resp_json['message']))
                except KeyError:
                    data = resp_json
                else:
                    data = resp_json['data']
                    self._do_post_request_tasks(data)
            self._last_response = resp
            return data
        return do_request

    def _build_request_url(self, secure, api_method):
        """Build a URL for a API method request
        """
        if secure:
            proto = ANDROID_MANGA.PROTOCOL_SECURE
        else:
            proto = ANDROID_MANGA.PROTOCOL_INSECURE
        req_url = ANDROID_MANGA.API_URL.format(
            protocol=proto,
            api_method=api_method
        )
        return req_url

    @property
    def session_started(self):
        return self._state_params.get('session_id', None) is not None

    @property
    def logged_in(self):
        return self._state_params['auth'] is not None

    def get_state(self):
        state = {
            'state_params': self._state_params,
            'cookies': dict(self._connector.cookies),
            'user_data': self._user_data,
        }
        return json.dumps(state)

    def set_state(self, state):
        loaded_state = json.loads(state)
        self._state_params.update(loaded_state['state_params'])
        self._connector.cookies.update(loaded_state['cookies'])
        self._user_data = loaded_state['user_data']

    @build_api_method(METHOD_POST)
    def android_register_gcm_token(self, response):
        """
        This appears to be related to Google's cloud notification service

        @param int android_sdk_version
        @param str registration_id
        @param int user_id
        @param str hash_id (optional)
        """
        pass

    @build_api_method(METHOD_POST)
    def bookmark(self, response):
        """
        NYI
        """
        pass

    def bookmark_get(self): pass # get
    def bookmark_set(self): pass # post
    def bookmark_remove(self): pass # post

    @build_api_method(METHOD_POST)
    def cr_authenticate(self, response):
        """
        Not sure what this does, possibly refreshes/re-issues the auth token

        @param str hash_id (optional)
        """
        self._state_params['auth'] = response['auth']

    @build_api_method(METHOD_POST)
    def cr_contact(self, response):
        """
        Send an email to CR I guess? Probably not terribly useful

        @param str email
        @param str subject
        @param str message
        """
        pass

    @build_api_method(METHOD_POST)
    def cr_forgot_password(self, response):
        """
        Trigger the forgotten password email, probably

        @param str email
        """
        pass

    @build_api_method(METHOD_POST)
    def cr_login(self, response):
        """
        Login using email/username and password, used to get the auth token

        @param str account
        @param str password
        @param str hash_id (optional)
        """
        self._state_params['auth'] = response['auth']
        self._user_data = response['user']
        if not self.logged_in:
            raise ApiLoginFailure(response)

    @build_api_method(METHOD_POST)
    def cr_logout(self, response):
        """
        @param str hash_id (optional)
        """
        self._state_params['auth'] = None
        self._user_data = None

    @build_api_method(METHOD_POST)
    def cr_signup(self, response):
        """
        Create a new CR account

        @param str email
        @param str password
        @param str hash_id (optional)
        """
        pass

    @build_api_method(METHOD_POST)
    def cr_start_session(self, response):
        """
        Should be called before anything else or likely to get an "unauthorized
        request" error

        @param str device_id
        @param str access_token
        """
        self._state_params['session_id'] = response['session_id']
        self._state_params['country_code'] = response['country_code']

    @build_api_method(METHOD_POST)
    def favorite(self, response):
        """
        NYI
        """
        pass

    def favorite_get(self): pass # get
    def favorite_set(self): pass # post
    def favorite_remove(self): pass # post

    @build_api_method(METHOD_GET)
    def list_chapter(self, response):
        """
        Get chapter and page info for a chapter

        @param int chapter_id
        """
        pass

    @build_api_method(METHOD_GET)
    def list_chapters(self, response):
        """
        Get the list of chapters in a series

        @param int series_id
        @param int user_id      (optional) effect unknown
        """
        pass

    @build_api_method(METHOD_GET)
    def list_filters(self, response):
        """
        Get the list of possible filters (possibly)
        """
        pass

    @build_api_method(METHOD_GET)
    def list_series(self, response):
        """
        Get the list of series

        @param str content_type     (optional) probably for differentiating manga from manwa, example value is "jp_manga"
        @param str filter           (optional) filter the returned results in some way, usage is unknown
        """
        pass

    @build_api_method(METHOD_POST)
    def log_chapterpage(self, response):
        """
        Presumably marks progress in a chapter

        @param int user_id
        @param int series_id
        @param int chapter_id
        @param int page_id
        """
        pass

    @build_api_method(METHOD_POST)
    def push_settings(self, response):
        """
        Save settings to CR's servers, probably account related stuff but unknown

        @param int user_id
        ** Additional keys should just be used as extra parameters for the function **
        """
        pass

    @build_api_method(METHOD_POST)
    def track_pageview(self, response):
        """
        Probably for CR's stats tracking or marking the last read page

        @param int user_id
        @param str page_ids
        @param str premium
        """
        pass
