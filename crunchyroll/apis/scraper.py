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

import re
import json

from crunchyroll.apis import ApiInterface
from crunchyroll.constants import SCRAPER
from crunchyroll.apis.errors import *

class ScraperApi(ApiInterface):
    """Website scraper API
    """

    def __init__(self, connector):
        self._connector = connector

    def get_media_formats(self, media_id):
        """CR doesn't seem to provide the video_format and video_quality params
        through any of the APIs so we have to scrape the video page
        """
        url = (SCRAPER.API_URL + 'media-' + media_id).format(
            protocol=SCRAPER.PROTOCOL_INSECURE)
        format_pattern = re.compile(SCRAPER.VIDEO.FORMAT_PATTERN)
        formats = {}

        for format, param in SCRAPER.VIDEO.FORMAT_PARAMS.iteritems():
            resp = self._connector.get(url, params={param: '1'})
            if not resp.ok:
                continue
            match = format_pattern.search(resp.content)
            if match:
                formats[format] = (int(match.group(1)), int(match.group(2)))
        return formats
