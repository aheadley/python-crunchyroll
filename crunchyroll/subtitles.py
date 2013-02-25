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
from xml.dom.minidom import parseString as minidom_parseString

try:
    from crypto.cipher.aes_cbc import AES_CBC
    from crypto.cipher.base import noPadding
    _LEGACY_CRYPTO = True
except ImportError:
    from Crypto.Cipher.AES import MODE_CBC, AESCipher
    _LEGACY_CRYPTO = False

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

    def decrypt(self, subtitle_id, iv, encrypted_data):
        """Decrypt encrypted subtitle data

        @param int subtitle_id
        @param str iv
        @param str encrypted_data
        @return str
        """

        encryption_key = self._build_encryption_key(int(subtitle_id))
        decryption_func = self._get_decryption_func(encryption_key, iv.decode('base64'))
        return zlib.decompress(decryption_func(encrypted_data.decode('base64')))

    def _get_decryption_func(self, encryption_key, iv):
        """Get a function to do encryption based on the version of the pycrypto
        module being used
        """
        if _LEGACY_CRYPTO:
            def decrypt_func(data):
                cipher = AES_CBC(encryption_key, padding=noPadding(),
                    keySize=len(encryption_key))
                return cipher.decrypt(iv + data)
        else:
            def decrypt_func(data):
                cipher = AESCipher(encryption_key, MODE_CBC, iv)
                return cipher.decrypt(data)
        return decrypt_func

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

    def format(self, sub_xml_text):
        """Turn a string containing the subs xml document into the formatted
        subtitle string

        @param str sub_xml_text
        @return str
        """

        xml_doc = minidom_parseString(sub_xml_text)
        return self._format(xml_doc)

    def _format(self, sub_xml_doc):
        """Do the actual formatting on the parsed xml document, should be
        overridden by subclasses

        @param xml.dom.Document sub_xml_doc
        @return str
        """
        raise NotImplemented

class ASSFormatter(SubtitleFormatter):
    """Subtitle formatter for ASS format
    """

    def _format(self, sub_xml_doc):
        pass

    def _format_style(self, style_element):
        pass

    def _format_event(self, event_element):
        pass

class SRTFormatter(SubtitleFormatter):
    """Subtitle formatter for SRT (unstyled) format
    """

    def _format(self, sub_xml_doc):
        # TODO: finish this
        return '\n\n'.join(self._format_event(idx, event) \
            for idx, event in enumerate(sorted(events)))

    def _format_event(self, index, event):
        pass

    def _format_timestamp(self, timestamp):
        """Format timestamp to what SRT wants

        Turns a string like 0:00:04.17 -> 00:00:04,170

        @param str timestamp
        @return str
        """
        # TODO: milliseconds are wrong, should be left-justified
        return '{0:02d}:{1:02d}:{2:02d},{3:03d}'.format(
            *map(int, timestamp.replace('.', ':').split(':')))
