import json
import locale
import functools

import requests

from .constants import *

class ApiException(Exception):
    """Base class for exceptions thrown by the API classes
    """
    pass

class ApiNetworkException(ApiException):
    """We couldn't talk to the API because the internet tubes are clogged or
    something
    """
    pass

class ApiBadResponseException(ApiException):
    """We got a response from the API but it didn't make any sense or we don't
    know how to handle it
    """
    pass

class ApiError(ApiException):
    """API gave us an error response (that we know how to parse)
    """
    pass


class ApiInterface(object):
    """This will be the basis for the shared API interfaces once the Ajax and
    Web APIs have been implemented
    """
    pass

class AjaxApi(ApiInterface):
    """AJAX call API
    """
    pass

class ScraperApi(ApiInterface):
    """HTML scraping interface
    """
    pass

def make_api_method(req_method, secure=True, version=0):
    """Turn an API class's method into a function that builds the request,
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
    """

    METHOD_GET      = 'GET'
    METHOD_POST     = 'POST'

    def __init__(self, session_id=None, auth=None):
        """Init object, optionally with previously stored session and/or auth
        tokens
        """
        self._connector = requests.Session()
        self._request_headers = {
            'X-Android-Device-Manufacturer':
                ANDROID_DEVICE_MANUFACTURER,
            'X-Android-Device-Model':
                ANDROID_DEVICE_MODEL,
            'X-Android-Device-Product':
                ANDROID_DEVICE_PRODUCT,
            # TODO: maybe setting this to '1' will give us higher res
            # videos and/or soft-subs? there were some other headers that need
            # to be sent if this is '1' though, needs testing
            'X-Android-Device-Is-GoogleTV': '0',
            'X-Android-SDK': ANDROID_SDK_VERSION,
            'X-Android-Release': ANDROID_RELEASE_VERSION,
            'X-Android-Application-Version-Code': ANDROID_APP_CODE,
            'X-Android-Application-Version-Name': ANDROID_APP_PACKAGE,
            'User-Agent': ANDROID_USER_AGENT,
        }
        self._state_params = {
            'session_id': session_id,
            'auth': auth,
            'user': None,
        }
        # for debugging
        self._last_response = None
        # dunno what these are for yet, seems to be a way to tell the client
        # to do something
        self._session_ops = []

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
            'device_id':    ANDROID_DEVICE_ID,
            'device_type':  ANDROID_APP_PACKAGE,
            'access_token': CR_ACCESS_TOKEN,
            'version':      ANDROID_APP_CODE,
        }
        base_params.update(dict(k, v) \
            for k, v in self._state_params.iteritems() \
                if v is not None)
        return base_params

    def _do_post_request_tasks(self, response_data):
        """Handle actions that need to be done with every response

        I'm not sure what these session_ops are actually used for yet, seems to
        be a way to tell the client to do *something* if needed.
        """
        if 'ops' in response_data:
            try:
                self._session_ops.extend(response_data.get('ops', []))
            except AttributeError:
                # oops, wasn't a dict
                pass

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
            resp = request_func(url, full_params)
            try:
                is_error = resp.json['error']
            except TypeError:
                raise ApiBadResponseException(resp.content)
            if is_error:
                raise ApiError('%s: %s' % (resp.json['code'], resp.json['message']))
            else:
                self._last_response = resp
                data = resp.json['data']
                self._do_post_request_tasks(data)
                return data
        return do_request

    def _build_request_url(self, secure, api_method, version):
        """Build a URL for a API method request
        """
        if secure:
            proto = CR_API_SECURE_PROTO
        else:
            proto = CR_API_INSECURE_PROTO
        req_url = CR_API_URL.format(
            protocol=proto,
            api_method=api_method,
            version=version
        )
        return req_url

    @make_api_method(METHOD_POST, False)
    def start_session(self, response):
        """
        This is the only method that doesn't go over HTTPS (for some reason). Must
        be called before anything else or you get an "unauthorized request" error.

        I don't know what the duration param does in any of these methods

        @param int duration (optional)
        """
        self._state_params['session_id'] = response['session_id']
        self._state_params['country_code'] = response['country_code']

    @make_api_method(METHOD_POST)
    def end_session(self, response):
        """
        Should probably be called after ``logout``
        """
        self._state_params['session_id'] = None

    @make_api_method(METHOD_POST)
    def login(self, response):
        """
        Login using email/username and password, used to get the auth token

        @param str account
        @param str password
        @param int duration (optional)
        """
        self._state_params['auth'] = response['auth']

    @make_api_method(METHOD_POST)
    def logout(self, response):
        """
        Auth param is not actually required, will be included with requests
        automatically after logging in
        """
        self._state_params['auth'] = None

    @make_api_method(METHOD_POST)
    def authenticate(self, response):
        """
        This does not appear to be used, might refresh auth token though.

        @param str auth
        @param int duration (optional)
        """
        pass

    @make_api_method(METHOD_GET)
    def list_series(self, response):
        """
        Get the list of series, default limit seems to be 20.

        @param str media_type   one of CR_MEDIA_TYPE_*
        @param str filter       one of CR_FILTER_*, (optional)
        @param int offset=0     pick the index to start at, is not multiplied
                                    by limit or anything
        @param int limit=20     does not seem to have an upper bound
        @param str fields       comma separated list of CR_FIELD_* for extra
                                    info, this must be used to get things like
                                    video links which aren't in the default
                                    field set (optional)
        """
        pass

    @make_api_method(METHOD_GET)
    def list_media(self, response):
        """
        Get the list of videos for a series

        Only collection_id *or* series_id should be given, the API will
        probably give an error if either both or none are given

        @param int collection_id
        @param int series_id
        @param str sort=CR_FILTER_POPULAR
        @param int offset=0
        @param int limit=20
        @param str fields       comma separated list of CR_FIELD_* for extra
                                    info, this must be used to get things like
                                    video links which aren't in the default
                                    field set (optional)
        """
        pass

    @make_api_method(METHOD_GET)
    def info(self, response):
        """
        Get info about a specific video

        Same deal as `list_media`, only pass collection_id or series_id, not
        both or none

        @param int media_id
        @param int collection_id
        @param int series_id
        @param str fields       comma separated list of CR_FIELD_* for extra
                                    info, this must be used to get things like
                                    video links which aren't in the default
                                    field set (optional)
        """
        pass

    """ ** METHODS PAST THIS POINT ARE UNTESTED ** """

    @make_api_method(METHOD_POST)
    def add_to_queue(self, response):
        """
        @param int series_id
        """
        pass

    @make_api_method(METHOD_GET)
    def categories(self, response):
        """
        @param str media_type   probably should be one of CR_MEDIA_TYPE_*
        """
        pass

    @make_api_method(METHOD_GET)
    def queue(self, response):
        """
        @param str media_types
        """
        pass

    @make_api_method(METHOD_GET)
    def recently_watched(self, response):
        """
        @param str media_types
        @param int offset
        @param int limit
        """
        pass

    @make_api_method(METHOD_POST)
    def remove_from_queue(self, response):
        """
        @param int series_id
        """
        pass

    @make_api_method(METHOD_POST)
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

    @make_api_method(METHOD_POST)
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

    @make_api_method(METHOD_POST)
    def forgot_password(self, response):
        """
        @param str email
        """
        pass

    @make_api_method(METHOD_GET)
    def free_trial_info(self, response):
        """
        """
        pass

    @make_api_method(METHOD_GET)
    def list_ads(self, response):
        """
        @param int media_id
        """
        pass

    @make_api_method(METHOD_POST)
    def log_ad_requested(self, response):
        """
        @param str ad_network
        """
        pass

    @make_api_method(METHOD_POST)
    def log_ad_served(self, response):
        """
        @param str ad_network
        """
        pass

    @make_api_method(METHOD_POST)
    def log_first_launch(self, response):
        """
        """
        pass

    @make_api_method(METHOD_POST)
    def log_impression(self, response):
        """
        @param str view
        """
        pass

    @make_api_method(METHOD_POST)
    def log_install_referrer(self, response):
        """
        @param str referrer
        """
        pass

    @make_api_method(METHOD_POST)
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
