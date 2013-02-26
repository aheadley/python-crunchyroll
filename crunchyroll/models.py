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

class DictModel(object):
    def __init__(self, data):
        if type(data) != dict:
            raise TypeError('DictModel can only be initialized with a dict')
        else:
            self._data = data

    def __getattr__(self, name):
        try:
            item = self._data.get(name)
        except KeyError as err:
            raise AttributeError(err)
        try:
            return DictModel(item)
        except TypeError:
            return item

class XmlModel(object):
    pass

class Series(DictModel):
    pass

class Media(DictModel):
    pass

class MediaStream(XmlModel):
    pass

