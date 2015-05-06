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
import functools
import pipes
import xml.etree.ElementTree as ET
try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser

logger = logging.getLogger('crunchyroll.util')

# use a singleton parser
_html_parser = HTMLParser()

def html_unescape(html_string):
    return _html_parser.unescape(html_string)

def return_collection(collection_type):
    """Change method return value from raw API output to collection of models
    """
    def outer_func(func):
        @functools.wraps(func)
        def inner_func(self, *pargs, **kwargs):
            result = func(self, *pargs, **kwargs)
            return map(collection_type, result)
        return inner_func
    return outer_func

def parse_xml_string(xml_string):
    return ET.fromstring(xml_string)

def xml_node_to_string(xml_node):
    return ET.tostring(xml_node)

def format_rtmpdump_args(rtmp_data):
    arg_string = '-r {url} -W {swf_url} -T {token} -y {file} ' \
        '-p {page_url} -t {url}'
    return arg_string.format(**dict([(k, pipes.quote(v)) for (k,v) in rtmp_data.items()]))

# NullHandler was added in py2.7
if hasattr(logging, 'NullHandler'):
    NullHandler = logging.NullHandler
else:
    class NullHandler(logging.Handler):
        def handle(self, record):
            pass

        def emit(self, record):
            pass

        def createLock(self):
            self.lock = None

LOG_FORMAT = logging.Formatter('[%(asctime)s] %(levelname)8s - %(name)s: %(message)s')
