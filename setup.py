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

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import crunchyroll

packages = [
    'crunchyroll',
    'crunchyroll.apis',
]

classifiers = (
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
)

def format_requirement(req):
    COMP_CHARS = '<>!='
    try:
        idx = min(req.find(c) for c in COMP_CHARS if req.find(c) > 0)
    except ValueError:
        return req
    else:
        return '%s (%s)' % (req[:idx], req[idx:])

raw_requirements = open('requirements.txt').read().strip()
requirements = [format_requirement(req) for req in raw_requirements.split('\n')]

setup(
    name='crunchyroll',
    version=crunchyroll.__version__,
    description='Library to interface with Crunchyroll\'s APIs',
    long_description=open('README.md').read(),
    author=crunchyroll.__author__,
    author_email=crunchyroll.__author_email__,
    url=crunchyroll.__url__,
    packages=packages,
    package_data={'': ['LICENSE']},
    license=open('LICENSE').read(),
    classifiers=classifiers,
    provides=['crunchyroll'],
    requires=requirements
)
