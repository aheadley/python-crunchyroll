# -*- coding: utf-8 -*-

import requests

from ..apis import ApiInterface
from ..constants import AJAX
from .errors import *

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
            except Exception as err: # TODO: make this more specific
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

    def __init__(self):
        self._connector = requests.Session()
        self._last_response = None

    def _build_request_url(self, secure):
        proto = AJAX.PROTOCOL_SECURE if secure else AJAX.PROTOCOL_INSECURE
        return AJAX.API_URL.format(protocol=proto)

    def _build_request(self, req_method, req_url, secure, params):
        def req_func():
            try:
                func = getattr(self._connector, req_method.lower())
            except AttributeError:
                raise ApiException('Invalid request method')
            if secure and req_method == self.METHOD_POST:
                # wouldn't make sense to send data on a GET request
                return func(req_url, data=params)
            else:
                return func(req_url, params=params)
        return req_func

    @property
    def logged_in(self):
        return AJAX.COOKIE_USERID in self._connector.cookies

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
        return req_func()
