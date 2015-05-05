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

from crunchyroll.apis import ApiInterface
from crunchyroll.constants import ANDROID
from crunchyroll.apis.errors import *

logger = logging.getLogger('crunchyroll.apis.android')

def make_android_api_method(req_method, secure=True, version=0):
    """Turn an AndroidApi's method into a function that builds the request,
    sends it, then passes the response to the actual method. Should be used
    as a decorator.
    """
    def outer_func(func):
        def inner_func(self, **kwargs):
            req_url = self._build_request_url(secure, func.__name__, version)
            req_func = self._build_request(req_method, req_url, params=kwargs)
            response = req_func()
            func(self, response)
            return response
        return inner_func
    return outer_func

# TODO: should rename this to MobileApi or AppApi, I doubt the iPhone API is
# different (is there even an iPhone app?)
class AndroidApi(ApiInterface):
    """Android (and probably iPhone) API interface

    Optional API method parameters are marked as such, or have a default
    value specified.

    Only hard-subbed and SD streams are supported, HD/soft-subs are simply
    not available through the API.
    @link http://www.crunchyroll.com/forumtopic-777139/are-streams-hd-on-the-new-kindle-fire-hd?fpid=41205823
    """

    METHOD_GET      = 'GET'
    METHOD_POST     = 'POST'

    def __init__(self, state=None):
        """Init object, optionally with previously stored session and/or auth
        tokens
        """
        self._connector = requests.Session()
        self._request_headers = {
            'X-Android-Device-Manufacturer':
                ANDROID.DEVICE_MANUFACTURER,
            'X-Android-Device-Model':
                ANDROID.DEVICE_MODEL,
            'X-Android-Device-Product':
                ANDROID.DEVICE_PRODUCT,
            # changing this to '1' doesn't seem to have an effect
            'X-Android-Device-Is-GoogleTV': '1',
            'X-Android-SDK': ANDROID.SDK_VERSION,
            'X-Android-Release': ANDROID.RELEASE_VERSION,
            'X-Android-Application-Version-Code': ANDROID.APP_CODE,
            'X-Android-Application-Version-Name': ANDROID.APP_PACKAGE,
            'User-Agent': ANDROID.USER_AGENT,
        }
        self._state_params = {
            'session_id': None,
            'auth': None,
            'user': None,
        }
        self._user_data = None
        # for debugging
        self._last_response = None
        # dunno what these are for yet, seems to be a way to tell the client
        # to do something
        self._session_ops = []
        if state is not None:
            self.set_state(state)
        logger.info('Initialized state: %r', self._state_params)

    def _get_locale(self):
        """Get the current locale with dashes (-) and underscores (_) removed

        Ex: en-US -> enUS
        """
        return locale.getdefaultlocale()[0].replace('_', '').replace('-', '')

    def _get_base_params(self):
        """Get the params that will be included with every request
        """
        base_params = {
            'locale':       self._get_locale(),
            'device_id':    ANDROID.DEVICE_ID,
            'device_type':  ANDROID.APP_PACKAGE,
            'access_token': ANDROID.ACCESS_TOKEN,
            'version':      ANDROID.APP_CODE,
        }
        base_params.update(dict((k, v) \
            for k, v in self._state_params.iteritems() \
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
            try:
                is_error = resp_json['error']
            except TypeError:
                raise ApiBadResponseException(resp.content)
            if is_error:
                raise ApiError('%s: %s' % (resp_json['code'], resp_json['message']))
            else:
                self._last_response = resp
                data = resp_json['data']
                self._do_post_request_tasks(data)
                return data
        return do_request

    def _build_request_url(self, secure, api_method, version):
        """Build a URL for a API method request
        """
        if secure:
            proto = ANDROID.PROTOCOL_SECURE
        else:
            proto = ANDROID.PROTOCOL_INSECURE
        req_url = ANDROID.API_URL.format(
            protocol=proto,
            api_method=api_method,
            version=version
        )
        return req_url

    @property
    def session_started(self):
        return self._state_params.get('session_id', None) is not None

    @property
    def logged_in(self):
        return self._state_params['auth'] is not None

    def is_premium(self, media_type):
        """Get if the session is premium for a given media type

        @param str media_type       Should be one of ANDROID.MEDIA_TYPE_*
        @return bool
        """
        if self.logged_in:
            if media_type in self._user_data['premium']:
                return True
        return False

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

    @make_android_api_method(METHOD_POST, False)
    def start_session(self, response):
        """
        This is the only method that doesn't go over HTTPS (for some reason). Must
        be called before anything else or you get an "unauthorized request" error.

        I don't know what the duration param does in any of these methods

        @param int duration (optional)
        """
        self._state_params['session_id'] = response['session_id']
        self._state_params['country_code'] = response['country_code']

    @make_android_api_method(METHOD_POST)
    def end_session(self, response):
        """
        Should probably be called after ``logout``
        """
        self._state_params['session_id'] = None

    @make_android_api_method(METHOD_POST)
    def login(self, response):
        """
        Login using email/username and password, used to get the auth token

        @param str account
        @param str password
        @param int duration (optional)
        """
        self._state_params['auth'] = response['auth']
        self._user_data = response['user']
        if not self.logged_in:
            raise ApiLoginFailure(response)

    @make_android_api_method(METHOD_POST)
    def logout(self, response):
        """
        Auth param is not actually required, will be included with requests
        automatically after logging in
        """
        self._state_params['auth'] = None
        self._user_data = None

    @make_android_api_method(METHOD_POST)
    def authenticate(self, response):
        """
        This does not appear to be used, might refresh auth token though.

        @param str auth
        @param int duration (optional)
        """
        pass

    @make_android_api_method(METHOD_GET)
    def list_series(self, response):
        """
        Get the list of series, default limit seems to be 20.

        @param str media_type   one of ANDROID.MEDIA_TYPE_*
        @param str filter       one of ANDROID.FILTER_*, (optional)
        @param int offset=0     pick the index to start at, is not multiplied
                                    by limit or anything
        @param int limit=20     does not seem to have an upper bound
        @param str fields       comma separated list of ANDROID.FIELD.* for extra
                                    info, this must be used to get things like
                                    video links which aren't in the default
                                    field set (optional)
        """
        pass

    @make_android_api_method(METHOD_GET)
    def list_media(self, response):
        """
        Get the list of videos for a series

        Only collection_id *or* series_id should be given, the API will
        probably give an error if either both or none are given

        @param int collection_id
        @param int series_id
        @param str sort=ANDROID.FILTER_POPULAR
        @param int offset=0
        @param int limit=20
        @param str fields       comma separated list of ANDROID.FIELD.* for extra
                                    info, this must be used to get things like
                                    video links which aren't in the default
                                    field set (optional)
        """
        pass

    @make_android_api_method(METHOD_GET)
    def info(self, response):
        """
        Get info about a specific video

        Same deal as `list_media`, only pass collection_id or series_id, not
        both or none

        @param int media_id
        @param int collection_id
        @param int series_id
        @param str fields       comma separated list of ANDROID.FIELD.* for extra
                                    info, this must be used to get things like
                                    video links which aren't in the default
                                    field set (optional)
        """
        pass

    """ ** METHODS PAST THIS POINT ARE UNTESTED ** """

    @make_android_api_method(METHOD_POST)
    def add_to_queue(self, response):
        """
        @param int series_id
        """
        pass

    @make_android_api_method(METHOD_GET)
    def categories(self, response):
        """
        @param str media_type   probably should be one of ANDROID.MEDIA_TYPE_*
        """
        pass

    @make_android_api_method(METHOD_GET)
    def queue(self, response):
        """
        @param str media_types  | (pipe) separated list of ANDROID.MEDIA_TYPE_*
        """
        pass

    @make_android_api_method(METHOD_GET)
    def recently_watched(self, response):
        """
        @param str media_types
        @param int offset
        @param int limit
        """
        pass

    @make_android_api_method(METHOD_POST)
    def remove_from_queue(self, response):
        """
        @param int series_id
        """
        pass

    @make_android_api_method(METHOD_POST)
    def signup(self, response):
        """
        @param str email
        @param str password
        @param str username
        @param str first_name
        @param str last_name
        @param int duration
        """
        pass

    @make_android_api_method(METHOD_POST)
    def free_trial_start(self, response):
        """
        @param str sku
        @param str currency_code
        @param str first_name
        @param str last_name
        @param str cc
        @param str exp_month
        @param str exp_year
        @param str zip
        @param str address_1
        @param str address_2
        @param str city
        @param str state
        @param str country_code
        """
        pass

    @make_android_api_method(METHOD_POST)
    def forgot_password(self, response):
        """
        @param str email
        """
        pass

    @make_android_api_method(METHOD_GET)
    def free_trial_info(self, response):
        """
        """
        pass

    @make_android_api_method(METHOD_GET)
    def list_ads(self, response):
        """
        @param int media_id
        """
        pass

    @make_android_api_method(METHOD_POST)
    def log_ad_requested(self, response):
        """
        @param str ad_network
        """
        pass

    @make_android_api_method(METHOD_POST)
    def log_ad_served(self, response):
        """
        @param str ad_network
        """
        pass

    @make_android_api_method(METHOD_POST)
    def log_first_launch(self, response):
        """
        """
        pass

    @make_android_api_method(METHOD_POST)
    def log_impression(self, response):
        """
        @param str view
        """
        pass

    @make_android_api_method(METHOD_POST)
    def log_install_referrer(self, response):
        """
        @param str referrer
        """
        pass

    @make_android_api_method(METHOD_POST)
    def log(self, response):
        """
        @param str event
        @param int media_id
        @param int playhead
        @param int elapsed
        @param int elapsed_delta
        @param int video_id
        @param int video_encode_id
        """
        pass
