python-crunchyroll
==================

Python interface to Crunchyroll's undocumented mobile app API.

### Requirements

  * requests

### Usage

Currently works for logging in and listing series/episodes. Video file URLs can
also be found but they are hard-subbed and no subtitle files are available yet
via the API.

Example usage:
~~~~
>>> import crunchyroll.api
>>> api = crunchyroll.api.AndroidApi()
>>> session_data = api.start_session()
>>> from crunchyroll.constants import *
>>> series_list = api.list_series(media_type=CR_MEDIA_TYPE_ANIME)
>>> pprint([s['name'] for s in series_list])
[u'Naruto Shippuden',
 u'NARUTO Spin-Off: Rock Lee & His Ninja Pals',
 u'Kotoura-San',
 u'Magi',
 u'Gintama',
 u'Space Brothers',
 u'Hunter x Hunter',
 u'Shin Sekai Yori (From the New World)',
 u'Maoyu',
 u'Ixion Saga DT',
 u'Cardfight!! Vanguard Link Joker (Season 3)',
 u'Chihayafuru',
 u'Hakkenden: Eight Dogs of the East',
 u'Fairy Tail',
 u'Folktales from Japan',
 u'Saint Seiya Omega',
 u'Polar Bear Cafe',
 u"Wooser's Hand-to-Mouth Life",
 u'Blast of Tempest',
 u'The Pet Girl of Sakurasou']
~~~~

### LICENSE

This project is licensed under GPLv2+, I will get around to adding the license
to the repo... eventually.
