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

import logging

logger = logging.getLogger('crunchyroll.apis')

# urllib3 gives annoying warnings when used with older python versions that don't
# matter to us, so we disable them
# @source https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
try:
    import requests
    requests.packages.urllib3.disable_warnings()
    logger.info('Disabled urllib3 warnings')
except Exception as err:
    logger.info('Couldnt disable urllib3 warnings: %s', err)

class ApiInterface(object):
    """This will be the basis for the shared API interfaces once the Ajax and
    Web APIs have been implemented
    """

    @property
    def session_started(self):
        """Check if the API session has started
        """
        raise NotImplemented

    @property
    def logged_in(self):
        """Check if a user has been logged in through the API
        """
        raise NotImplemented

    def get_state(self):
        """Get the internal state so that the session can be
        resumed without logging in again between runs
        """
        raise NotImplemented

    def set_state(self, state):
        """Set the internal state to resume without logging in
        again
        """
        raise NotImplemented
