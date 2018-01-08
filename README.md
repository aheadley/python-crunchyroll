python-crunchyroll
==================

**ABANDONED** I don't have a Crunchyroll account or any real interest in
this package anymore

Python interface to Crunchyroll's undocumented APIs and utilities
for working with the returned data. Eventual plan is to create a better
XMBC plugin.

### Requirements

  * Python 2.6+
  * requests
  * tlslite

### Usage

Pretty much anything of interest is available now, including the RTMPE stream
data and decrypted and formatted subtitles.

Example usage:
~~~~
>>> from crunchyroll.apis.meta import MetaApi
>>> api = MetaApi()
>>> pprint([s.name for s in api.list_anime_series(limit=5)])
[u'07 Ghost',
 u'11eyes',
 u'A Bridge to the Starry Skies - Hoshizora e Kakaru Hashi',
 u'A Dark Rabbit has Seven Lives',
 u'Abunai Sisters']
>>> space_brothers = api.search_anime_series('Space Brothers')[0]
>>> pprint(space_brothers.description)
u'To follow his brother Hibito to the moon, Mutta will attempt to become an
astronaut at the age of 32.  Unaware of his own talent, Mutta chases his
dreams to get back in front of his younger brother.'
>>> sb_episodes = api.list_media(space_brothers)
>>> len(sb_episodes)
49
>>> ep = [e for e in sb_episodes if e.episode_number == '40'][0]
>>> print ep.episode_number, ep.name, ep.free_available
40 Heaven and Hell True
>>> api.login(username=username, password=password)
True
>>> stream = api.get_media_stream(ep)
>>> subs = stream.default_subtitles.decrypt().get_ass_formatted()
>>> print '\n'.join(subs.split('\n')[:9])
[Script Info]
Title: English (US)
ScriptType: v4.00+
WrapStyle: 0
PlayRexX: 704
PlayResY: 400
Subtitle ID: XXXXX
Language: English (US)
Created: 28 days ago
>>> [s.language for s in stream.subtitle_stubs]
['English (US)', u'Espa\xf1ol', u'Fran\xe7ais (France)', u'Portugu\xeas (Brasil)']
>>> fr_subs = api.unfold_subtitle_stub(stream.subtitle_stubs[2]).decrypt().get_srt_formatted()
>>> print '\n'.join(fr_subs.split('\n')[:11])
1
00:00:00,760 --> 00:00:02,940
Tiens ? Ça ne s'ouvre pas.

2
00:00:04,500 --> 00:00:06,770
Tourne le levier vers la gauche.

3
00:00:07,360 --> 00:00:10,150
Lequel ?
~~~~

### Testing

Run the unit tests with:

    $ python setup.py test

Note that some of the unit tests will use a CR account which should be made
available in the `CRUNCHYROLL_USERNAME` and `CRUNCHYROLL_PASSWORD` environment
variables.

### LICENSE

This project is licensed under GPLv2+, see LICENSE for more details.
