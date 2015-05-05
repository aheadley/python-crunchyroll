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
import logging
import functools

from crunchyroll.util import parse_xml_string, return_collection, xml_node_to_string
from crunchyroll.subtitles import SubtitleDecrypter, SRTFormatter, ASS4plusFormatter
from crunchyroll.constants import META

logger = logging.getLogger('crunchyroll.models')

class DictModel(object):
    def __init__(self, data):
        if not isinstance(data, dict):
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

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, repr(self._data))

class XmlModel(object):
    def __init__(self, node):
        if isinstance(node, basestring):
            try:
                node = parse_xml_string(node)
            except Exception as err:
                raise ValueError(err)
        elif isinstance(node, XmlModel):
            logger.debug('Creating new %s with node=%r', self.__class__.__name__,
                node)
            node = node._data
        elif node is None:
            raise ValueError('XmlModel node cannot be NoneType')
        self._data = node

    def __getattr__(self, name):
        try:
            return self._data.attrib.get(name)
        except KeyError as err:
            raise AttributeError(err)

    def __repr__(self):
        name = self.__class__.__name__
        try:
            return '<%s(id=%s)>' % (name, self.id)
        except (AttributeError, TypeError):
            return '<%s(%s)>' % (name, self.tag_name)

    def __str__(self):
        return self.text if self.text is not None else repr(self)

    __unicode__ = __str__

    def __getitem__(self, name):
        return map(XmlModel, self.findall('./' + name))

    @property
    def text(self):
        return self._data.text

    @property
    def tag_name(self):
        return self._data.tag

    def findall(self, query):
        return map(XmlModel, self._data.findall(query))

    def findfirst(self, query):
        try:
            return self.findall(query)[0]
        except IndexError:
            return None

class Series(DictModel):
    pass

class Media(DictModel):
    pass

class SubtitleStub(XmlModel):
    LANG_UNKNOWN    = 'UNKNOWN'

    @property
    def language(self):
        lang = re.search(r'^\[.*\]\s*(.*)', self.title)
        if lang:
            lang_string = lang.group(1)
        else:
            lang_string = self.LANG_UNKNOWN
        logger.debug('%r language: %r -> %r', self, self.title, lang_string)
        return lang_string

    @property
    def is_default(self):
        return self.default == '1'

class Subtitle(XmlModel):
    def __init__(self, node):
        super(Subtitle, self).__init__(node)
        self._decrypter = SubtitleDecrypter()

    def decrypt(self):
        return StyledSubtitle(self._decrypter.decrypt(
            self._decrypter._build_encryption_key(int(self.id)),
            self['iv'][0].text.decode('base64'),
            self['data'][0].text.decode('base64')))

class StyledSubtitle(XmlModel):
    def get_ass_formatted(self):
        formatter = ASS4plusFormatter()
        return formatter.format(self)

    def get_srt_formatted(self):
        formatter = SRTFormatter()
        return formatter.format(self)

def require_not_upsell(func):
    @functools.wraps(func)
    def inner_func(self, *pargs, **kwargs):
        if not self.is_upsell:
            return func(self, *pargs, **kwargs)
        else:
            return None

class StreamInfo(XmlModel):
    @property
    def is_upsell(self):
        return bool(self['upsell'])

    @property
    def rtmp_data(self):
        data = {
            'url':         self.findfirst(
                './/host').text,
            'file':         self.findfirst(
                './/file').text,
            'token':        self.findfirst(
                './/token').text,
            'swf_url':      META.SWF_URL,
            'page_url':     META.PAGE_URL,
        }
        return data

    @property
    def duration(self):
        return float(self.findfirst(
            './/metadata/duration').text)

    @property
    def resolution(self):
        width = self.findfirst(
            '//metadata/width').text
        height = self.findfirst(
            '//metadata/height').text
        return (int(width), int(height))

class MediaStream(XmlModel):
    @property
    def stream_info(self):
        return StreamInfo(self._data.findall('.//{default}preload/stream_info')[0])

    @property
    def default_subtitles(self):
        return Subtitle(self.findfirst('.//{default}preload/subtitle'))

    @property
    @return_collection(SubtitleStub)
    def subtitle_stubs(self):
        return self.findall('.//{default}preload/subtitles/subtitle')
