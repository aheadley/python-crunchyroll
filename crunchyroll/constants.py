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

class API:
    BASE_DOMAIN = 'crunchyroll.com'
    PROTOCOL_INSECURE   = 'http'
    PROTOCOL_SECURE     = 'https'

    LOG_FORMAT          = '%(asctime)s - %(levelname)s - [%(name)s] %(message)s'

class ANDROID(API):
    ACCESS_TOKEN                = 'Scwg9PRRZ19iVwD'
    API_DOMAIN                  = 'api.' + API.BASE_DOMAIN
    API_URL                     = '{protocol}://' + API_DOMAIN + '/' \
                                    '{api_method}.{version}.json'

    # eventually these should be used to identify this library so CR can get
    # usage statistics about people using third-party apps or something, maybe
    DEVICE_MANUFACTURER = 'unknown'
    DEVICE_MODEL        = 'google_sdk'
    DEVICE_PRODUCT      = 'google_sdk'
    USER_AGENT          = 'Dalvik/1.6.0 (Linux; U; Android 4.2; google_sdk Build/JB_MR1)'
    # this should probably be replaced with a UUIDv4 in api init
    DEVICE_ID           = '00000000-18c4-ade8-ffff-ffff99d603a9'
    SDK_VERSION         = '17'
    RELEASE_VERSION     = '4.2'
    APP_CODE            = '66'
    APP_VERSION_NAME    = '0.7.9'
    APP_PACKAGE         = 'com.crunchyroll.crunchyroid'

    # dunno what these are for yet
    PREMIUM_FLAG_ANIME      = 'anime'
    PREMIUM_FLAG_DRAMA      = 'drama'
    PREMIUM_FLAG_TAISENG    = 'taiseng'

    # media type flags
    MEDIA_TYPE_ANIME    = 'anime'
    MEDIA_TYPE_DRAMA    = 'drama'

    # filter flags
    FILTER_POPULAR      = 'popular'
    FILTER_SIMULCAST    = 'simulcast'
    FILTER_UPDATED      = 'updated'
    FILTER_ALPHA        = 'alpha'
    FILTER_NEWEST       = 'newest'
    FILTER_PREFIX       = 'prefix:' # search maybe?
    FILTER_TAG          = 'tag:' # need to find a list of tags
    # media listing must use one of these
    FILTER_ASC          = 'asc'
    FILTER_DESC         = 'desc'

    class FIELD:
        # these are apparently like database fields or something that you can add
        # to the list_series, list_media, and info methods to get additional or only
        # specific info. of particular note is the MEDIA_STREAM_DATA field
        # to get the streams
        GENERAL_MOST_LIKELY_MEDIA   = 'most_likely_media'
        GENERAL_ORDERING            = 'ordering'
        MEDIA_ID                    = 'media.media_id'
        MEDIA_NAME                  = 'media.name'
        MEDIA_EPISODE_NUMBER        = 'media.episode_number'
        MEDIA_SCREENSHOT_IMAGE      = 'media.screenshot_image'
        MEDIA_STREAM_DATA           = 'media.stream_data'
        MEDIA_FREE_AVAILABLE        = 'media.free_available'
        MEDIA_PREMIUM_AVAILABLE     = 'media.premium_available'
        MEDIA_AVAILABILITY_NOTES    = 'media.availablity_notes'
        MEDIA_PLAYHEAD              = 'media.playhead'
        MEDIA_TYPE                  = 'media.media_type'
        MEDIA_DESCRIPTION           = 'media.description'
        SERIES                      = 'series'
        SERIES_ID                   = 'series.series_id'
        SERIES_NAME                 = 'series.name'
        SERIES_PUBLISHER_NAME       = 'series.publisher_name'
        SERIES_YEAR                 = 'series.year'
        SERIES_SCREENSHOT_IMAGE     = 'series.screenshot_image'
        SERIES_LANDSCAPE_IMAGE      = 'series.landscape_image'
        SERIES_PORTRAIT_IMAGE       = 'series.portrait_image'
        SERIES_MEDIA_COUNT          = 'series.media_count'
        SERIES_MEDIA_TYPE           = 'series.media_type'
        SERIES_IN_QUEUE             = 'series.in_queue'
        SERIES_DESCRIPTION          = 'series.description'
        IMAGE_FWIDE_URL             = 'image.fwide_url'
        IMAGE_WIDESTAR_URL          = 'image.widestar_url'
        IMAGE_LARGE_URL             = 'image.large_url'
        IMAGE_FULL_URL              = 'image.full_url'

class AJAX(API):
    API_DOMAIN                  = 'www.' + API.BASE_DOMAIN
    API_URL                     = '{protocol}://' + API_DOMAIN + '/xml/'
    API_CURRENT_PAGE            = API.PROTOCOL_INSECURE + '://' + API_DOMAIN + '/'

    HEADER_REFERRER     = 'http://static.ak.crunchyroll.com/flash/' \
        '20130201144858.bd8118f7c58d1da788d88782497e30a4/StandardVideoPlayer.swf'
    HEADER_ORIGIN       = 'http://static.ak.crunchyroll.com'
    HEADER_USER_AGENT   = ANDROID.USER_AGENT

    COOKIE_USERID       = 'c_userid'
    COOKIE_USERKEY      = 'c_userkey'
    COOKIE_VISITOR      = 'c_visitor'
    COOKIE_SESSID       = 'sess_id'

    class VIDEO:
        FORMATS             = [
            '1080p',
            '720p',
            '480p',
            '360p',
        ]

class SCRAPER(API):
    API_DOMAIN                  = 'www.' + API.BASE_DOMAIN
    API_URL                     = '{protocol}://' + API_DOMAIN + '/'

    class VIDEO(AJAX.VIDEO):
        FORMAT_PARAMS       = dict((f, f[-1]+f[:-1]) for f in AJAX.VIDEO.FORMATS)
        FORMAT_PATTERN      = r'swfobject\.embedSWF.*express_install\.swf\',' \
            '.*video_format%3D(\d+).*video_quality%3D(\d+)%26.*,loadBrandedPlayerAd.*'



class META(API):
    MAX_SERIES          = 500
    MAX_MEDIA           = 1000

    TYPE_ANIME          = ANDROID.MEDIA_TYPE_ANIME
    TYPE_DRAMA          = ANDROID.MEDIA_TYPE_DRAMA

    # sorting for series lists
    SORT_POPULAR        = ANDROID.FILTER_POPULAR
    SORT_SIMULCAST      = ANDROID.FILTER_SIMULCAST
    SORT_UPDATED        = ANDROID.FILTER_UPDATED
    SORT_ALPHA          = ANDROID.FILTER_ALPHA
    SORT_NEWEST         = ANDROID.FILTER_NEWEST
    # sorting for media lists
    SORT_ASC            = ANDROID.FILTER_ASC
    SORT_DESC           = ANDROID.FILTER_DESC

    VIDEO = AJAX.VIDEO

    # normally you would need the player revision to generate this URL, but
    # fortunately CR provides us with the latest version to the CPA.swf without
    # the revision in the path
    SWF_URL             = 'http://static.ak.crunchyroll.com/swf/ChromelessPlayerApp.swf'
    PAGE_URL            = AJAX.API_CURRENT_PAGE
