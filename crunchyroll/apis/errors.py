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

class ApiLoginFailure(ApiError):
    """Login info wasn't correct
    """
    pass
