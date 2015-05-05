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

from setuptools import setup, find_packages

import crunchyroll


with open('README.md') as readme:
    long_description = readme.read()

with open('requirements.txt') as reqs:
    requirements = [line.strip() for line in reqs if line.strip()]

SETUP_ARGS = {
    # package metadata
    'name':             crunchyroll.__title__,
    'description':      crunchyroll.__description__,
    'long_description': long_description,
    'version':          crunchyroll.__version__,
    'author':           crunchyroll.__author__,
    'author_email':     crunchyroll.__author_email__,
    'url':              crunchyroll.__url__,

    # pypi metadata
    'license':          'GPLv2.0',
    'platforms':        'any',
    'install_requires': requirements,
    'classifiers':      [
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    # setuptools info
    'packages':         find_packages(),
    'test_suite':       'tests',
}

if __name__ == '__main__':
    setup(**SETUP_ARGS)
