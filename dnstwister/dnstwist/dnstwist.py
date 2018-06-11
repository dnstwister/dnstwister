#!/usr/bin/env python
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
# dnstwist 1.04b modified by Robert Wallhead (robert@thisismyrobot.com) for
# use in https://dnstwister.report - all functionality except fuzzing removed
# and various changes made to support usage in Heroku.
#

__author__ = 'Marcin Ulikowski'
__version__ = '1.04b'
__email__ = 'marcin@ulikowski.pl'

import re
import os.path


FILE_TLD = os.path.join(
    'dnstwister',
    'dnstwist',
    'database',
    'effective_tld_names.dat'
)
DB_TLD = os.path.exists(FILE_TLD)
if not DB_TLD:
    raise Exception('TLD database is required!')


class InvalidDomain(Exception):
    """ Exception for invalid domains.
    """
    pass


def validate_domain(domain):
    """Validate a domain - including unicode domains."""
    try:
        if len(domain) == len(domain.encode('idna')) and domain != domain.encode('idna'):
            return False
    except (UnicodeError, TypeError):
        return False
    allowed = re.compile(r'(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}\.?$)', re.IGNORECASE)
    return allowed.match(domain.encode('idna'))


class fuzz_domain(object):
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
        'w': 'sxq', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhj'
        }
        self.keyboards = [ self.qwerty, self.qwertz, self.azerty ]

    def __domain_tld(self, domain):
        domain = domain.rsplit('.', 2)

        if len(domain) == 2:
            return domain[0], domain[1]

        if DB_TLD:
            cc_tld = {}
            re_tld = re.compile(r'^[a-z]{2,4}\.[a-z]{2}$', re.IGNORECASE)

            for line in open(FILE_TLD):
                line = line[:-1]
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

    def __validate_domain(self, domain):
        return validate_domain(domain)

    def __filter_domains(self):
        seen = set()
        filtered = []

        for d in self.domains:
            if self.__validate_domain(d['domain-name']) and d['domain-name'] not in seen:
                seen.add(d['domain-name'])
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
        glyphs = {
            'a': [u'à', u'á', u'â', u'ã', u'ä', u'å', u'ɑ', u'а', u'ạ', u'ǎ', u'ă', u'ȧ', u'ӓ'],
            'b': ['d', 'lb', 'ib', u'ʙ', u'Ь', u'b̔', u'ɓ', u'Б'],
            'c': [u'ϲ', u'с', u'ƈ', u'ċ', u'ć', u'ç'],
            'd': ['b', 'cl', 'dl', 'di', u'ԁ', u'ժ', u'ɗ', u'đ'],
            'e': [u'é', u'ê', u'ë', u'ē', u'ĕ', u'ě', u'ė', u'е', u'ẹ', u'ę', u'є', u'ϵ', u'ҽ'],
            'f': [u'Ϝ', u'ƒ', u'Ғ'],
            'g': ['q', u'ɢ', u'ɡ', u'Ԍ', u'Ԍ', u'ġ', u'ğ', u'ց', u'ǵ', u'ģ'],
            'h': ['lh', 'ih', u'һ', u'հ', u'Ꮒ', u'н'],
            'i': ['1', 'l', u'Ꭵ', u'í', u'ï', u'ı', u'ɩ', u'ι', u'ꙇ', u'ǐ', u'ĭ', u'ì', u'î', u'î́', u'ĩ', u'ĩ́', u'ĩ̀', u'ĩ̂', u'ĩ̌', u'ĩ̍', u'ĩ̎', u'ī', u'ī́', u'ī̀', u'ī̂', u'ī̌', u'ī̃', u'ī̄', u'ī̆', u'ī̆́', u'ĭ', u'ĭ̀', u'ĭ́', u'i̇́', u'ï̀', u'ḯ', u'ï̂', u'ï̃', u'ï̄', u'ï̌', u'ï̑', u'i̊', u'i̋', u'ỉ', u'i̍', u'i̎', u'ȉ', u'i̐', u'ȋ', u'į', u'į̀', u'į́', u'į̇́', u'į̂', u'į̃', u'į̇̃', u'į̄', u'į̄̀', u'į̄́', u'į̄̂', u'į̄̆', u'į̄̌', u'į̈', u'į̈̀', u'į̈́', u'į̈̂', u'į̈̌', u'į̈̄', u'į̋', u'į̌', u'į̱', u'į̱́', u'į̱̀', u'i̓', u'i̧', u'í̧', u'ì̧', u'î̧', u'i̭', u'ī̭', u'ḭ', u'ḭ̀', u'ḭ́', u'ḭ̄', u'ḭ̈', u'ḭ̈́', u'i̱', u'ì̱', u'í̱', u'î̱', u'ǐ̱', u'ĩ̱', u'ï̱', u'ḯ̱', u'ï̱̀', u'ï̱̂', u'ï̱̌', u'ī̱', u'ī̱́', u'ī̱̀', u'ī̱̂', u'i̮', u'ị', u'ị̀', u'ị́', u'ị̂', u'ị̃', u'ị̄', u'ị̈', u'ị̈̀', u'ị̈́', u'ị̈̂', u'ị̈̌', u'ị̌', u'ị̍', u'i̤', u'ì̤', u'í̤', u'î̤', u'ï̤', u'i̥', u'í̥', u'ï̥', u'i̯', u'í̯', u'ĩ̯', u'i̩', u'i͔', u'ī͔', u'ɨ', u'ɨ̀', u'ɨ́', u'ɨ̂', u'ɨ̌', u'ɨ̃', u'ɨ̄', u'ɨ̈', u'ɨ̧', u'ɨ̧̀', u'ɨ́', u'ɨ̂', u'ɨ̌', u'ɨ̃', u'ɨ̄', u'ɨ̈', u'ɨ̧', u'ɨ̧̀', u'ɨ̧̂', u'ɨ̧̌', u'ɨ̱', u'ɨ̱̀', u'ɨ̱̀', u'ɨ̱̂', u'ɨ̱̈', u'ɨ̱̌', u'ɨ̯', u'ᶖ', u'ı̣', u'ı̥', u'ɩ̀', u'ɩ́', u'ɩ̂', u'ɩ̃', u'ɩ̈', u'ɩ̌', u'ᵼ'],
            'j': [u'ј', u'ʝ', u'ϳ', u'ɉ'],
            'k': ['lk', 'ik', 'lc', u'κ', u'ⲕ', u'κ'],
            'l': ['1', 'i', u'ɫ', u'ł'],
            'm': ['n', 'nn', 'rn', 'rr', u'ṃ', u'ᴍ', u'м', u'ɱ'],
            'n': ['m', 'r', u'ń'],
            'o': ['0', u'Ο', u'ο', u'О', u'о', u'Օ', u'ȯ', u'ọ', u'ỏ', u'ơ', u'ó', u'ö', u'ӧ'],
            'p': [u'ρ', u'р', u'ƿ', u'Ϸ', u'Þ'],
            'q': ['g', u'զ', u'ԛ', u'գ', u'ʠ'],
            'r': [u'ʀ', u'Г', u'ᴦ', u'ɼ', u'ɽ'],
            's': [u'Ⴝ', u'Ꮪ', u'ʂ', u'ś', u'ѕ'],
            't': [u'τ', u'т', u'ţ'],
            'u': [u'μ', u'υ', u'Ս', u'ս', u'ц', u'ᴜ', u'ǔ', u'ŭ'],
            'v': [u'ѵ', u'ν', u'v̇'],
            'w': ['vv', u'ѡ', u'ա', u'ԝ'],
            'x': [u'х', u'ҳ', u'ẋ'],
            'y': [u'ʏ', u'γ', u'у', u'Ү', u'ý'],
            'z': [u'ʐ', u'ż', u'ź', u'ʐ', u'ᴢ']
        }

        result = []

        for ws in range(0, len(self.domain)):
            for i in range(0, (len(self.domain)-ws)+1):
                win = self.domain[i:i+ws]

                j = 0
                while j < ws:
                    c = win[j]
                    if c in glyphs:
                        win_copy = win
                        for g in glyphs[c]:
                            win = win.replace(c, g)
                            result.append(self.domain[:i] + win + self.domain[i+ws:])
                            win = win_copy
                    j += 1

        return list(set(result))

    def __hyphenation(self):
        result = []

        for i in range(1, len(self.domain)):
            result.append(self.domain[:i] + '-' + self.domain[i:])

        return result

    def __insertion(self):
        result = []

        for i in range(1, len(self.domain)-1):
            for keys in self.keyboards:
                if self.domain[i] in keys:
                    for c in keys[self.domain[i]]:
                        result.append(self.domain[:i] + c + self.domain[i] + self.domain[i+1:])
                        result.append(self.domain[:i] + self.domain[i] + c + self.domain[i+1:])

        return list(set(result))

    def __omission(self):
        result = []

        for i in range(0, len(self.domain)):
            result.append(self.domain[:i] + self.domain[i+1:])

        n = re.sub(r'(.)\1+', r'\1', self.domain)

        if n not in result and n != self.domain:
            result.append(n)

        return list(set(result))

    def __repetition(self):
        result = []

        for i in range(0, len(self.domain)):
            if self.domain[i].isalpha():
                result.append(self.domain[:i] + self.domain[i] + self.domain[i] + self.domain[i+1:])

        return list(set(result))

    def __replacement(self):
        result = []

        for i in range(0, len(self.domain)):
            for keys in self.keyboards:
                if self.domain[i] in keys:
                    for c in keys[self.domain[i]]:
                        result.append(self.domain[:i] + c + self.domain[i+1:])

        return list(set(result))

    def __vowel_swap(self):
        vowels = 'aeiou'
        result = []

        for i in range(0, len(self.domain)):
            for vowel in vowels:
                if self.domain[i] in vowels:
                    result.append(self.domain[:i] + vowel + self.domain[i+1:])

        return list(set(result))

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

    def __addition(self):
        result = []

        for i in range(97, 123):
            result.append(self.domain + chr(i))

        return result

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

        self.__filter_domains()
