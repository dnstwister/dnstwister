# -*- coding: utf-8 -*-
#
# dnstwist
#
# Generate and resolve domain variations to detect typo squatting,
# phishing and corporate espionage.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# dnstwist modified by Robert Wallhead for use in https://dnstwister.report
# and this repository.
#

__author__ = 'Marcin Ulikowski'
__version__ = '20180623'
__email__ = 'marcin@ulikowski.pl'

import re
import os.path

import idna

from dnstwister.core.domain import Domain


FILE_TLD = os.path.join(
    'dnstwister',
    'dnstwist',
    'database',
    'effective_tld_names.dat'
)
DB_TLD = os.path.exists(FILE_TLD)
if not DB_TLD:
    raise Exception('TLD database is required!')


class DomainFuzzer(object):
    """ Domain fuzzer.
    """
    def __init__(self, domain):
        self.domain, self.tld = self.__domain_tld(domain)
        self.domains = []
        self.qwerty = {
        '1': '2q', '2': '3wq1', '3': '4ew2', '4': '5re3', '5': '6tr4', '6': '7yt5', '7': '8uy6', '8': '9iu7', '9': '0oi8', '0': 'po9',
        'q': '12wa', 'w': '3esaq2', 'e': '4rdsw3', 'r': '5tfde4', 't': '6ygfr5', 'y': '7uhgt6', 'u': '8ijhy7', 'i': '9okju8', 'o': '0plki9', 'p': 'lo0',
        'a': 'qwsz', 's': 'edxzaw', 'd': 'rfcxse', 'f': 'tgvcdr', 'g': 'yhbvft', 'h': 'ujnbgy', 'j': 'ikmnhu', 'k': 'olmji', 'l': 'kop',
        'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm', 'm': 'njk'
        }
        self.qwertz = {
        '1': '2q', '2': '3wq1', '3': '4ew2', '4': '5re3', '5': '6tr4', '6': '7zt5', '7': '8uz6', '8': '9iu7', '9': '0oi8', '0': 'po9',
        'q': '12wa', 'w': '3esaq2', 'e': '4rdsw3', 'r': '5tfde4', 't': '6zgfr5', 'z': '7uhgt6', 'u': '8ijhz7', 'i': '9okju8', 'o': '0plki9', 'p': 'lo0',
        'a': 'qwsy', 's': 'edxyaw', 'd': 'rfcxse', 'f': 'tgvcdr', 'g': 'zhbvft', 'h': 'ujnbgz', 'j': 'ikmnhu', 'k': 'olmji', 'l': 'kop',
        'y': 'asx', 'x': 'ysdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm', 'm': 'njk'
        }
        self.azerty = {
        '1': '2a', '2': '3za1', '3': '4ez2', '4': '5re3', '5': '6tr4', '6': '7yt5', '7': '8uy6', '8': '9iu7', '9': '0oi8', '0': 'po9',
        'a': '2zq1', 'z': '3esqa2', 'e': '4rdsz3', 'r': '5tfde4', 't': '6ygfr5', 'y': '7uhgt6', 'u': '8ijhy7', 'i': '9okju8', 'o': '0plki9', 'p': 'lo0m',
        'q': 'zswa', 's': 'edxwqz', 'd': 'rfcxse', 'f': 'tgvcdr', 'g': 'yhbvft', 'h': 'ujnbgy', 'j': 'iknhu', 'k': 'olji', 'l': 'kopm', 'm': 'lp',
        'w': 'sxq', 'x': 'wsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhj'
        }
        self.keyboards = [ self.qwerty, self.qwertz, self.azerty ]
        self.glyphs = {
            'a': ['à', 'á', 'â', 'ã', 'ä', 'å', 'ɑ', 'ạ', 'ǎ', 'ă', 'ȧ', 'ą'],
            'b': ['d', 'lb', 'ʙ', 'ɓ', 'ḃ', 'ḅ', 'ḇ'],
            'c': ['e', 'ƈ', 'ċ', 'ć', 'ç', 'č', 'ĉ'],
            'd': ['b', 'cl', 'dl', 'ɗ', 'đ', 'ď', 'ɖ', 'ḑ', 'ḋ', 'ḍ', 'ḏ', 'ḓ'],
            'e': ['c', 'é', 'è', 'ê', 'ë', 'ē', 'ĕ', 'ě', 'ė', 'ẹ', 'ę', 'ȩ', 'ɇ', 'ḛ'],
            'f': ['ƒ', 'ḟ'],
            'g': ['q', 'ɢ', 'ɡ', 'ġ', 'ğ', 'ǵ', 'ģ', 'ĝ', 'ǧ', 'ǥ'],
            'h': ['lh', 'ĥ', 'ȟ', 'ħ', 'ɦ', 'ḧ', 'ḩ', 'ⱨ', 'ḣ', 'ḥ', 'ḫ', 'ẖ'],
            'i': ['1', 'l', 'í', 'ì', 'ï', 'ı', 'ɩ', 'ǐ', 'ĭ', 'ỉ', 'ị', 'ɨ', 'ȋ', 'ī'],
            'j': ['ʝ', 'ɉ'],
            'k': ['lk', 'ik', 'lc', 'ḳ', 'ḵ', 'ⱪ', 'ķ'],
            'l': ['1', 'i', 'ɫ', 'ł'],
            'm': ['n', 'nn', 'rn', 'rr', 'ṁ', 'ṃ', 'ᴍ', 'ɱ', 'ḿ'],
            'n': ['m', 'r', 'ń', 'ṅ', 'ṇ', 'ṉ', 'ñ', 'ņ', 'ǹ', 'ň', 'ꞑ'],
            'o': ['0', 'ȯ', 'ọ', 'ỏ', 'ơ', 'ó', 'ö'],
            'p': ['ƿ', 'ƥ', 'ṕ', 'ṗ'],
            'q': ['g', 'ʠ'],
            'r': ['ʀ', 'ɼ', 'ɽ', 'ŕ', 'ŗ', 'ř', 'ɍ', 'ɾ', 'ȓ', 'ȑ', 'ṙ', 'ṛ', 'ṟ'],
            's': ['ʂ', 'ś', 'ṣ', 'ṡ', 'ș', 'ŝ', 'š'],
            't': ['ţ', 'ŧ', 'ț', 'ƫ'],
            'u': ['ᴜ', 'ǔ', 'ŭ', 'ü', 'ʉ', 'ù', 'ú', 'û', 'ũ', 'ū', 'ų', 'ư', 'ů', 'ű', 'ȕ', 'ȗ', 'ụ'],
            'v': ['ṿ', 'ⱱ', 'ᶌ', 'ṽ', 'ⱴ'],
            'w': ['vv', 'ŵ', 'ẁ', 'ẃ', 'ẅ', 'ⱳ', 'ẇ', 'ẉ', 'ẘ'],
            'x': [],
            'y': ['ʏ', 'ý', 'ÿ', 'ŷ', 'ƴ', 'ȳ', 'ɏ', 'ỿ', 'ẏ', 'ỵ'],
            'z': ['ʐ', 'ż', 'ź', 'ᴢ', 'ƶ', 'ẓ', 'ẕ', 'ⱬ']
        }

    def __domain_tld(self, domain):
        domain = domain.rsplit('.', 2)

        if len(domain) == 2:
            return domain[0], domain[1]

        if DB_TLD:
            cc_tld = {}
            re_tld = re.compile(r'^[a-z]{2,4}\.[a-z]{2}$', re.IGNORECASE)

            for line in open(FILE_TLD, 'rb'):
                line = str(line[:-1], 'utf-8')
                if re_tld.match(line):
                    sld, tld = line.split('.')
                    if not tld in cc_tld:
                        cc_tld[tld] = []
                    cc_tld[tld].append(sld)

            sld_tld = cc_tld.get(domain[2])
            if sld_tld:
                if domain[1] in sld_tld:
                    return domain[0], domain[1] + '.' + domain[2]

        return domain[0] + '.' + domain[1], domain[2]

    def __filter_domains(self):
        seen = set()
        filtered = []

        for d in self.domains:

            d_obj = Domain.try_parse(d['domain-name'])
            if d_obj is None:
                continue

            if d_obj.to_unicode() in seen:
                continue
            seen.add(d_obj.to_unicode())

            filtered.append(d)

        self.domains = filtered

    def __bitsquatting(self):
        result = []
        masks = [1, 2, 4, 8, 16, 32, 64, 128]
        for i in range(0, len(self.domain)):
            c = self.domain[i]
            for j in range(0, len(masks)):

                # Deal with Unicode later...
                if ord(c) > 255:
                    continue

                b = chr(ord(c) ^ masks[j])
                o = ord(b)
                if (o >= 48 and o <= 57) or (o >= 97 and o <= 122) or o == 45:
                    result.append(self.domain[:i] + b + self.domain[i+1:])

        return result

    def __homoglyph(self):

        result = set()

        for ws in range(0, len(self.domain)):
            for i in range(0, (len(self.domain)-ws)+1):
                win = self.domain[i:i+ws]

                j = 0
                while j < ws:
                    c = win[j]
                    if c in self.glyphs:
                        win_copy = win
                        for g in self.glyphs[c]:
                            win = win.replace(c, g)
                            result.add(self.domain[:i] + win + self.domain[i+ws:])
                            win = win_copy

                            # Very long domains have terrible complexity when
                            # ran through this algorithm.
                            if len(result) >= 1000:
                                return result
                    j += 1

        return result

    def __hyphenation(self):
        result = []

        for i in range(1, len(self.domain)):
            result.append(self.domain[:i] + '-' + self.domain[i:])

        return result

    def __insertion(self):
        result = set()

        for i in range(1, len(self.domain)):
            for keys in self.keyboards:
                if self.domain[i] in keys:
                    for c in keys[self.domain[i]]:
                        result.add(self.domain[:i] + c + self.domain[i] + self.domain[i+1:])
                        result.add(self.domain[:i] + self.domain[i] + c + self.domain[i+1:])

        return result

    def __omission(self):
        result = set()

        for i in range(0, len(self.domain)):
            result.add(self.domain[:i] + self.domain[i+1:])

        n = re.sub(r'(.)\1+', r'\1', self.domain)

        if n not in result and n != self.domain:
            result.add(n)

        return result

    def __repetition(self):
        result = set()

        for i in range(0, len(self.domain)):
            if self.domain[i].isalpha():
                result.add(self.domain[:i] + self.domain[i] + self.domain[i] + self.domain[i+1:])

        return result

    def __replacement(self):
        result = set()

        for i in range(0, len(self.domain)):
            for keys in self.keyboards:
                if self.domain[i] in keys:
                    for c in keys[self.domain[i]]:
                        result.add(self.domain[:i] + c + self.domain[i+1:])

        return result

    def __subdomain(self):
        result = []

        for i in range(1, len(self.domain)):
            if self.domain[i] not in ['-', '.'] and self.domain[i-1] not in ['-', '.']:
                result.append(self.domain[:i] + '.' + self.domain[i:])

        return result

    def __transposition(self):
        result = []

        for i in range(0, len(self.domain)-1):
            if self.domain[i+1] != self.domain[i]:
                result.append(self.domain[:i] + self.domain[i+1] + self.domain[i] + self.domain[i+2:])

        return result

    def __vowel_swap(self):
        vowels = 'aeiou'
        result = set()

        for i in range(0, len(self.domain)):
            for vowel in vowels:
                if self.domain[i] in vowels:
                    result.add(self.domain[:i] + vowel + self.domain[i+1:])

        return result

    def __addition(self):
        result = []

        for i in range(97, 123):
            result.append(self.domain + chr(i))

        return result

    def __other_tlds(self):
        tlds = [
            # Common TLDs
            'com', 'cn', 'de', 'net', 'uk', 'org', 'co',

            # Most abused (spamhaus/phishstats)
            'live', 'buzz', 'gq', 'tk', 'fit', 'cf', 'ga',
            'ml', 'wang', 'ru', 'top', 'info', 'in', 'br'
        ]

        return [f'{self.domain}.{tld}' for tld in tlds]

    def fuzz(self):
        """ Perform a domain fuzz.
        """
        self.domains.append({ 'fuzzer': 'Original*', 'domain-name': self.domain + '.' + self.tld })

        for domain in self.__addition():
            self.domains.append({ 'fuzzer': 'Addition', 'domain-name': domain + '.' + self.tld })
        for domain in self.__bitsquatting():
            self.domains.append({ 'fuzzer': 'Bitsquatting', 'domain-name': domain + '.' + self.tld })
        for domain in self.__homoglyph():
            self.domains.append({ 'fuzzer': 'Homoglyph', 'domain-name': domain + '.' + self.tld })
        for domain in self.__hyphenation():
            self.domains.append({ 'fuzzer': 'Hyphenation', 'domain-name': domain + '.' + self.tld })
        for domain in self.__insertion():
            self.domains.append({ 'fuzzer': 'Insertion', 'domain-name': domain + '.' + self.tld })
        for domain in self.__omission():
            self.domains.append({ 'fuzzer': 'Omission', 'domain-name': domain + '.' + self.tld })
        for domain in self.__repetition():
            self.domains.append({ 'fuzzer': 'Repetition', 'domain-name': domain + '.' + self.tld })
        for domain in self.__replacement():
            self.domains.append({ 'fuzzer': 'Replacement', 'domain-name': domain + '.' + self.tld })
        for domain in self.__subdomain():
            self.domains.append({ 'fuzzer': 'Subdomain', 'domain-name': domain + '.' + self.tld })
        for domain in self.__transposition():
            self.domains.append({ 'fuzzer': 'Transposition', 'domain-name': domain + '.' + self.tld })
        for domain in self.__vowel_swap():
            self.domains.append({ 'fuzzer': 'Vowel swap', 'domain-name': domain + '.' + self.tld })

        if not self.domain.startswith('www.'):
            self.domains.append({ 'fuzzer': 'Various', 'domain-name': 'ww' + self.domain + '.' + self.tld })
            self.domains.append({ 'fuzzer': 'Various', 'domain-name': 'www' + self.domain + '.' + self.tld })
            self.domains.append({ 'fuzzer': 'Various', 'domain-name': 'www-' + self.domain + '.' + self.tld })
        if '.' in self.tld:
            self.domains.append({ 'fuzzer': 'Various', 'domain-name': self.domain + '.' + self.tld.split('.')[-1] })
            self.domains.append({ 'fuzzer': 'Various', 'domain-name': self.domain + self.tld })
        if '.' not in self.tld:
            self.domains.append({ 'fuzzer': 'Various', 'domain-name': self.domain + self.tld + '.' + self.tld })
        if self.tld != 'com' and '.' not in self.tld:
            self.domains.append({ 'fuzzer': 'Various', 'domain-name': self.domain + '-' + self.tld + '.com' })

        for domain_with_tld in self.__other_tlds():
            self.domains.append({ 'fuzzer': 'Other TLD', 'domain-name': domain_with_tld })

        self.__filter_domains()
