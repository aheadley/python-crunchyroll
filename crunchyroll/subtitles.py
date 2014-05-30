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

import math
import hashlib
import zlib
import re
import logging

from tlslite.utils.cipherfactory import createAES

logger = logging.getLogger('crunchyroll.subtitles')

def aes_decrypt(key, iv, data):
    return str(createAES(key, iv).decrypt(data))

class SubtitleDecrypter(object):
    """Decrypt Crunchyroll's encrypted subtitle data

    This is pretty much copy and pasted from the Crunchyroll Takeout extension
    for XBMC, with minor readability enhancements

    @link https://code.google.com/p/urlxl-repo/source/browse/plugin.video.crunchyroll-takeout/resources/lib/crunchyDec.py
    """

    ENCRYPTION_KEY_SIZE     = 32
    # I have no idea where this comes from, gogo gadget copy and paste
    # results in 0x0540E9FA
    HASH_MAGIC_CONST        = int(math.floor(math.sqrt(6.9) * math.pow(2, 25)))

    HASH_SECRET_MOD_CONST   = 97
    HASH_SECRET_CHAR_OFFSET = 33
    HASH_SECRET_LENGTH      = 20

    def decrypt_subtitle(self, subtitle):
        """Decrypt encrypted subtitle data in high level model object

        @param crunchyroll.models.Subtitle subtitle
        @return str
        """
        return self.decrypt(self._build_encryption_key(int(subtitle.id)),
            subtitle['iv'][0].text.decode('base64'),
            subtitle['data'][0].text.decode('base64'))

    def decrypt(self, encryption_key, iv, encrypted_data):
        """Decrypt encrypted subtitle data

        @param int subtitle_id
        @param str iv
        @param str encrypted_data
        @return str
        """

        logger.info('Decrypting subtitles with length (%d bytes), key=%r',
            len(encrypted_data), encryption_key)
        return zlib.decompress(aes_decrypt(encryption_key, iv, encrypted_data))

    def _build_encryption_key(self, subtitle_id, key_size=ENCRYPTION_KEY_SIZE):
        """Generate the encryption key for a given media item

        Encryption key is basically just
        sha1(<magic value based on subtitle_id> + '"#$&).6CXzPHw=2N_+isZK') then
        padded with 0s to 32 chars

        @param int subtitle_id
        @param int key_size
        @return str
        """

        # generate a 160-bit SHA1 hash
        sha1_hash = hashlib.new('sha1', self._build_hash_secret((1, 2)) +
            self._build_hash_magic(subtitle_id)).digest()
        # pad to 256-bit hash for 32 byte key
        sha1_hash += '\x00' * max(key_size - len(sha1_hash), 0)
        return sha1_hash[:key_size]

    def _build_hash_magic(self, subtitle_id):
        """Build the other half of the encryption key hash

        I have no idea what is going on here

        @param int subtitle_id
        @return str
        """

        media_magic = self.HASH_MAGIC_CONST ^ subtitle_id
        hash_magic = media_magic ^ media_magic >> 3 ^ media_magic * 32
        return str(hash_magic)

    def _build_hash_secret(self, seq_seed, seq_len=HASH_SECRET_LENGTH,
            mod_value=HASH_SECRET_MOD_CONST):
        """Build a seed for the hash based on the Fibonacci sequence

        Take first `seq_len` + len(`seq_seed`) characters of Fibonacci
        sequence, starting with `seq_seed`, and applying e % `mod_value` +
        `HASH_SECRET_CHAR_OFFSET` to the resulting sequence, then return as
        a string

        @param tuple|list seq_seed
        @param int seq_len
        @param int mod_value
        @return str
        """

        # make sure we use a list, tuples are immutable
        fbn_seq = list(seq_seed)
        for i in range(seq_len):
            fbn_seq.append(fbn_seq[-1] + fbn_seq[-2])
        hash_secret = map(
            lambda c: chr(c % mod_value + self.HASH_SECRET_CHAR_OFFSET),
            fbn_seq[2:])
        return ''.join(hash_secret)

class SubtitleFormatter(object):
    """Base subtitle formatter class
    """

    def format(self, subtitles):
        """Turn a string containing the subs xml document into the formatted
        subtitle string

        @param str|crunchyroll.models.StyledSubtitle sub_xml_text
        @return str
        """
        logger.debug('Formatting subtitles (id=%s) with %s',
            subtitles.id, self.__class__.__name__)
        return self._format(subtitles).encode('utf-8')

    def _format(self, styled_subtitle):
        """Do the actual formatting on the parsed xml document, should be
        overridden by subclasses

        @param crunchyroll.models.StyledSubtitle styled_subtitle
        @return str
        """
        raise NotImplemented

class ASS4Formatter(SubtitleFormatter):
    """Subtitle formatter for ASS v4 format
    """

    STYLE_HEADER    = u'[V4 Styles]'
    STYLE_KEYS      = u'Format: Name, Fontname, Fontsize, PrimaryColour, ' \
        'SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, ' \
        'StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, ' \
        'Shadow, Alignment, MarginL, MarginR, MarginV, Encoding'
    STYLE_FORMAT    = u'Style: {name}, {font_name}, {font_size}, {primary_colour}, ' \
        '{secondary_colour}, {outline_colour}, {back_colour}, {bold}, {italic}, ' \
        '{underline}, {strikeout}, {scale_x}, {scale_y}, {spacing}, {angle}, ' \
        '{border_style}, {outline}, {shadow}, {alignment}, {margin_l}, ' \
        '{margin_r}, {margin_v}, {encoding}'

    EVENT_HEADER    = u'[Events]'
    EVENT_KEYS      = u'Format: Layer, Start, End, Style, Name, MarginL, ' \
        'MarginR, MarginV, Effect, Text'
    EVENT_FORMAT    = u'Dialogue: 0,{start},{end},{style},{name},{margin_l},' \
        '{margin_r},{margin_v},{effect},{text}'

    def _format(self, styled_subtitle):
        return '\n'.join([
            self._format_header(styled_subtitle),
            self._format_styles(styled_subtitle.findall('.//styles/style')),
            self._format_events(styled_subtitle.findall('.//events/event')),
        ])

    def _format_header(self, subtitle_element):
        header = u"""[Script Info]
Title: {title}
ScriptType: v4.00
WrapStyle: {wrap_style}
PlayRexX: {play_res_x}
PlayResY: {play_res_y}
Subtitle ID: {id}
Language: {lang_string}
Created: {created}
"""
        return header.format(**subtitle_element._data.attrib)

    def _format_styles(self, style_elements):
        logger.debug('Formatting %d ASS style elements', len(style_elements))
        style = '\n'.join([
            self.STYLE_HEADER,
            self.STYLE_KEYS,
            '\n'.join(self._format_style(style) \
                for style in style_elements),
        ])
        return style + '\n'

    def _format_style(self, style_element):
        attrs = style_element._data.attrib.copy()
        for (k, v) in attrs.iteritems():
            # wikipedia suggests that v4 uses b10, while v4+ uses b16
            if v.startswith('&H'):
                attrs[k] = int(v[2:], 16)
        return self.STYLE_FORMAT.format(**attrs)

    def _format_events(self, event_elements):
        logger.debug('Formatting %d ASS event elements', len(event_elements))
        event_elements.sort(key=lambda e: int(e.id))
        events = '\n'.join([
            self.EVENT_HEADER,
            self.EVENT_KEYS,
            '\n'.join(self._format_event(event) \
                for event in event_elements),
        ])
        return events + '\n'

    def _format_event(self, event_element):
        return self.EVENT_FORMAT.format(**event_element._data.attrib)

class ASS4plusFormatter(ASS4Formatter):
    """Subtitle formatter for ASS v4+ format
    """

    STYLE_HEADER    = u'[V4+ Styles]'

    def _format_header(self, subtitle_element):
        header = u"""[Script Info]
Title: {title}
ScriptType: v4.00+
WrapStyle: {wrap_style}
PlayRexX: {play_res_x}
PlayResY: {play_res_y}
Subtitle ID: {id}
Language: {lang_string}
Created: {created}
"""
        return header.format(**subtitle_element._data.attrib)

    def _format_style(self, style_element):
        return self.STYLE_FORMAT.format(**style_element._data.attrib)

class SRTFormatter(SubtitleFormatter):
    """Subtitle formatter for SRT (unstyled) format
    """

    ASS_CMD_PATTERN     = re.compile(r'{[^}]+}')
    ASS_NEWLINE_PATTERN = re.compile(r'(?:\\n|\\N)')

    def _format(self, styled_subtitle):
        events = styled_subtitle.findall('.//events/event')
        logger.debug('Formatting %d SRT events', len(events))
        events.sort(key=lambda e: e.id)
        return '\n\n'.join(self._format_event(idx, event) \
            for idx, event in enumerate(events, 1)) + '\n'

    def _format_event(self, index, event):
        return '\n'.join([
            str(index),
            '{0} --> {1}'.format(
                self._format_timestamp(event.start),
                self._format_timestamp(event.end)),
            self._format_event_text(event),
        ])

    def _format_event_text(self, event):
        text = event._data.attrib.get('text')
        text = self.ASS_CMD_PATTERN.sub('', text)
        text = self.ASS_NEWLINE_PATTERN.sub('', text)
        return text

    def _format_timestamp(self, timestamp):
        """Format timestamp to what SRT wants

        Turns a string like 0:00:04.17 -> 00:00:04,170

        @param str timestamp
        @return str
        """
        return '{0:02d}:{1:02d}:{2:02d},{3:02d}0'.format(
            *map(int, timestamp.replace('.', ':').split(':')))
