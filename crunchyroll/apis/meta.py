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

import functools
import json
import logging

from crunchyroll.apis import ApiInterface
from crunchyroll.apis.android import AndroidApi
from crunchyroll.apis.ajax import AjaxApi
from crunchyroll.apis.scraper import ScraperApi
from crunchyroll.constants import META, AJAX, ANDROID
from crunchyroll.apis.errors import *
from crunchyroll.models import *
from crunchyroll.util import return_collection

logger = logging.getLogger('crunchyroll.apis.meta')

def require_session_started(func):
    """Check if API sessions are started and start them if not
    """
    @functools.wraps(func)
    def inner_func(self, *pargs, **kwargs):
        if not self.session_started:
            logger.info('Starting session for required meta method')
            self.start_session()
        return func(self, *pargs, **kwargs)
    return inner_func

def require_android_logged_in(func):
    """Check if andoid API is logged in and login if not, implies
    `require_session_started`
    """
    @functools.wraps(func)
    @require_session_started
    def inner_func(self, *pargs, **kwargs):
        if not self._android_api.logged_in:
            logger.info('Logging into android API for required meta method')
            if not self.has_credentials:
                raise ApiLoginFailure(
                    'Login is required but no credentials were provided')
            self._android_api.login(account=self._state['username'],
                password=self._state['password'])
        return func(self, *pargs, **kwargs)
    return inner_func

def optional_android_logged_in(func):
    """Check if andoid API is logged in and login if credentials were provided,
    implies `require_session_started`
    """
    @functools.wraps(func)
    @require_session_started
    def inner_func(self, *pargs, **kwargs):
        if not self._android_api.logged_in and self.has_credentials:
            logger.info('Logging into android API for optional meta method')
            self._android_api.login(account=self._state['username'],
                password=self._state['password'])
        return func(self, *pargs, **kwargs)
    return inner_func

def require_ajax_logged_in(func):
    """Check if ajax API is logged in and login if not
    """
    @functools.wraps(func)
    def inner_func(self, *pargs, **kwargs):
        if not self._ajax_api.logged_in:
            logger.info('Logging into AJAX API for required meta method')
            if not self.has_credentials:
                raise ApiLoginFailure(
                    'Login is required but no credentials were provided')
            self._ajax_api.User_Login(name=self._state['username'],
                password=self._state['password'])
        return func(self, *pargs, **kwargs)
    return inner_func

def optional_ajax_logged_in(func):
    """Check if ajax API is logged in and login if credentials available
    """
    @functools.wraps(func)
    def inner_func(self, *pargs, **kwargs):
        if not self._ajax_api.logged_in and self.has_credentials:
            logger.info('Logging into AJAX API for optional meta method')
            self._ajax_api.User_Login(name=self._state['username'],
                password=self._state['password'])
        return func(self, *pargs, **kwargs)
    return inner_func

class MetaApi(ApiInterface):
    """High level interface to crunchyroll
    """

    def __init__(self, username=None, password=None, state=None):
        self._state = {
            'username': username,
            'password': password,
        }
        self._ajax_api = AjaxApi()
        self._android_api = AndroidApi()
        if state is not None:
            self.set_state(state)

    @property
    def session_started(self):
        return self._ajax_api.session_started and \
            self._android_api.session_started

    @property
    def logged_in(self):
        return self._ajax_api.logged_in and self._android_api.logged_in

    @property
    def has_credentials(self):
        return self._state['username'] is not None and \
            self._state['password'] is not None

    def get_state(self):
        return json.dumps({
            'meta':     self._state,
            'ajax':     self._ajax_api.get_state(),
            'android':  self._android_api.get_state(),
        })

    def set_state(self, state):
        # TODO: error handling here
        decoded_state = json.loads(state)
        self._state = decoded_state['meta']
        self._ajax_api.set_state(decoded_state['ajax'])
        self._android_api.set_state(decoded_state['android'])

    @optional_android_logged_in
    def is_premium(self, media_type):
        """Get if the user is premium for a given media type

        @param str media_type       should be one of ANDROID.MEDIA_TYPE_*
        @return bool
        """
        return self._android_api.is_premium(media_type)

    def start_session(self):
        """Start the underlying APIs sessions

        Calling this is not required, it will be called automatically if
        a method that needs a session is called

        @return bool
        """
        self._android_api.start_session()
        return self.session_started

    @require_session_started
    def login(self, username, password):
        """Login with the given username/email and password

        Calling this method is not required if credentials were provided in
        the constructor, but it could be used to switch users or something maybe

        @return bool
        """
        # we could get stuck in an inconsistent state if got an exception while
        # trying to login with different credentials than what is stored so
        # we rollback the state to prevent that
        state_snapshot = self._state.copy()
        try:
            self._ajax_api.User_Login(name=username, password=password)
            self._android_api.login(account=username, password=password)
        except Exception as err:
            # something went wrong, rollback
            self._state = state_snapshot
            raise err
        self._state['username'] = username
        self._state['password'] = password
        return self.logged_in

    @optional_android_logged_in
    @return_collection(Series)
    def list_anime_series(self, sort=META.SORT_ALPHA, limit=META.MAX_SERIES, offset=0):
        """Get a list of anime series

        @param str sort     pick how results should be sorted, should be one
                                of META.SORT_*
        @param int limit    limit number of series to return, there doesn't
                                seem to be an upper bound
        @param int offset   list series starting from this offset, for pagination
        @return list<crunchyroll.models.Series>
        """
        result = self._android_api.list_series(
            media_type=ANDROID.MEDIA_TYPE_ANIME,
            filter=sort,
            limit=limit,
            offset=offset)
        return result

    @optional_android_logged_in
    @return_collection(Series)
    def list_drama_series(self, sort=META.SORT_ALPHA, limit=META.MAX_SERIES, offset=0):
        """Get a list of drama series

        @param str sort     pick how results should be sorted, should be one
                                of META.SORT_*
        @param int limit    limit number of series to return, there doesn't
                                seem to be an upper bound
        @param int offset   list series starting from this offset, for pagination
        @return list<crunchyroll.models.Series>
        """
        result = self._android_api.list_series(
            media_type=ANDROID.MEDIA_TYPE_DRAMA,
            filter=sort,
            limit=limit,
            offset=offset)
        return result

    @optional_android_logged_in
    @return_collection(Series)
    def search_anime_series(self, query_string):
        """Search anime series list by series name, case-sensitive

        @param str query_string     string to search for, note that the search
                                        is very simplistic and only matches against
                                        the start of the series name, ex) search
                                        for "space" matches "Space Brothers" but
                                        wouldn't match "Brothers Space"
        @return list<crunchyroll.models.Series>
        """
        result = self._android_api.list_series(
            media_type=ANDROID.MEDIA_TYPE_ANIME,
            filter=ANDROID.FILTER_PREFIX + query_string)
        return result

    @optional_android_logged_in
    @return_collection(Series)
    def search_drama_series(self, query_string):
        """Search drama series list by series name, case-sensitive

        @param str query_string     string to search for, note that the search
                                        is very simplistic and only matches against
                                        the start of the series name, ex) search
                                        for "space" matches "Space Brothers" but
                                        wouldn't match "Brothers Space"
        @return list<crunchyroll.models.Series>
        """
        result = self._android_api.list_series(
            media_type=ANDROID.MEDIA_TYPE_DRAMA,
            filter=ANDROID.FILTER_PREFIX + query_string)
        return result

    @optional_android_logged_in
    @return_collection(Media)
    def list_media(self, series, sort=META.SORT_DESC, limit=META.MAX_MEDIA, offset=0):
        """List media for a given series or collection

        @param crunchyroll.models.Series series the series to search for
        @param str sort                         choose the ordering of the
                                                    results, only META.SORT_DESC
                                                    is known to work
        @param int limit                        limit size of results
        @param int offset                       start results from this index,
                                                    for pagination
        @return list<crunchyroll.models.Media>
        """
        params = {
            'sort': sort,
            'offset': offset,
            'limit': limit,
        }
        params.update(self._get_series_query_dict(series))
        result = self._android_api.list_media(**params)
        return result

    @optional_android_logged_in
    @return_collection(Media)
    def search_media(self, series, query_string):
        """Search for media from a series starting with query_string, case-sensitive

        @param crunchyroll.models.Series series     the series to search in
        @param str query_string                     the search query, same restrictions
                                                        as `search_anime_series`
        @return list<crunchyroll.models.Media>
        """
        params = {
            'sort': ANDROID.FILTER_PREFIX + query_string,
        }
        params.update(self._get_series_query_dict(series))
        result = self._android_api.list_media(**params)
        return result

    @optional_ajax_logged_in
    def get_media_stream(self, media_item, format, quality):
        """Get the stream data for a given media item

        @param crunchyroll.models.Media media_item
        @param int format
        @param int quality
        @return crunchyroll.models.MediaStream
        """
        result = self._ajax_api.VideoPlayer_GetStandardConfig(
            media_id=media_item.media_id,
            video_format=format,
            video_quality=quality)
        return MediaStream(result)

    @optional_ajax_logged_in
    def get_stream_info(self, media_item, format, quality):
        result = self._ajax_api.VideoEncode_GetStreamInfo(
            media_id=media_item.media_id,
            video_format=format,
            video_encode_quality=quality)
        return StreamInfo(result)

    @return_collection(SubtitleStub)
    def get_subtitle_stubs(self, media_item):
        result = self._ajax_api.Subtitle_GetListing(media_id=media_item.media_id)
        return XmlModel(result)['subtitle']

    def unfold_subtitle_stub(self, subtitle_stub):
        """Turn a SubtitleStub into a full Subtitle object

        @param crunchyroll.models.SubtitleStub subtitle_stub
        @return crunchyroll.models.Subtitle
        """
        return Subtitle(self._ajax_api.Subtitle_GetXml(
            subtitle_script_id=int(subtitle_stub.id)))

    @optional_ajax_logged_in
    def get_stream_formats(self, media_item):
        """Get the available media formats for a given media item

        @param crunchyroll.models.Media
        @return dict
        """
        scraper = ScraperApi(self._ajax_api._connector)
        formats = scraper.get_media_formats(media_item.media_id)
        return formats

    @require_android_logged_in
    @return_collection(Series)
    def list_queue(self, media_types=[META.TYPE_ANIME, META.TYPE_DRAMA]):
        """List the series in the queue, optionally filtering by type of media

        @param list<str> media_types    a list of media types to filter the queue
                                            with, should be of META.TYPE_*
        @return list<crunchyroll.models.Series>
        """
        result = self._android_api.queue(media_types='|'.join(media_types))
        return [queue_item['series'] for queue_item in result]

    @require_android_logged_in
    def add_to_queue(self, series):
        """Add a series to the queue

        @param crunchyroll.models.Series series
        @return bool
        """
        result = self._android_api.add_to_queue(series_id=series.series_id)
        return result

    @require_android_logged_in
    def remove_from_queue(self, series):
        """Remove a series from the queue

        @param crunchyroll.models.Series series
        @return bool
        """
        result = self._android_api.remove_from_queue(series_id=series.series_id)
        return result

    def _get_series_query_dict(self, series):
        """Pick between collection_id and series_id params in series models for the
        Android API

        @param crunchyroll.models.Series series
        @return dict
        """
        if hasattr(series, 'series_id'):
            return {'series_id': series.series_id}
        else:
            return {'collection_id': series.collection_id}
