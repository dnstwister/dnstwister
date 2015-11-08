#!/usr/bin/env python
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
# dnstwist modified by Robert Wallhead (robert@thisismyrobot.com) for use in
# https://dnstwist.appspot.com - all functionality except fuzzing removed and
# various changes made to allow usage in Google App Engine.
#

__author__ = 'Marcin Ulikowski'
__version__ = '1.01'
__email__ = 'marcin@ulikowski.pl'

import re
import sys
import os.path


FILE_TLD = os.path.join('dnstwist', 'database', 'effective_tld_names.dat')
DB_TLD = os.path.exists(FILE_TLD)


class InvalidDomain(Exception):
    """ Exception for invalid domains.
    """
    pass


def validate_domain(domain):
    """ Validate a domain name.
    """
    if len(domain) > 255:
        return False
    if domain[-1] == '.':
        domain = domain[:-1]
    allowed = re.compile(
        r'\A([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}\Z', re.IGNORECASE
    )
    return allowed.match(domain)


class fuzz_domain(object):
    """ Domain fuzzer.
    """
    def __init__(self, domain):
        if not validate_domain(domain):
            raise InvalidDomain(domain)
        self.domain, self.tld = self.__domain_tld(domain)
        self.domains = []

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

    def __filter_domains(self):
        seen = set()
        filtered = []

        for d in self.domains:
            if validate_domain(d['domain']) and d['domain'] not in seen:
                seen.add(d['domain'])
                filtered.append(d)

        self.domains = filtered

    def __bitsquatting(self):
        result = []
        masks = [1, 2, 4, 8, 16, 32, 64, 128]
        for i in range(0, len(self.domain)):
            c = self.domain[i]
            for j in range(0, len(masks)):
                b = chr(ord(c) ^ masks[j])
                o = ord(b)
                if (o >= 48 and o <= 57) or (o >= 97 and o <= 122) or o == 45:
                    result.append(self.domain[:i] + b + self.domain[i+1:])

        return result

    def __homoglyph(self):
        glyphs = {
        'd': ['b', 'cl', 'dl', 'di'], 'm': ['n', 'nn', 'rn', 'rr'], 'l': ['1', 'i'],
        'o': ['0'], 'k': ['lk', 'ik', 'lc'], 'h': ['lh', 'ih'], 'w': ['vv'],
        'n': ['m', 'r'], 'b': ['d', 'lb', 'ib'], 'i': ['1', 'l'], 'g': ['q'], 'q': ['g']
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
            if self.domain[i] not in ['-', '.'] and self.domain[i-1] not in ['-', '.']:
                result.append(self.domain[:i] + '-' + self.domain[i:])

        return result

    def __insertion(self):
        keys = {
        '1': '2q', '2': '3wq1', '3': '4ew2', '4': '5re3', '5': '6tr4', '6': '7yt5', '7': '8uy6', '8': '9iu7', '9': '0oi8', '0': 'po9',
        'q': '12wa', 'w': '3esaq2', 'e': '4rdsw3', 'r': '5tfde4', 't': '6ygfr5', 'y': '7uhgt6', 'u': '8ijhy7', 'i': '9okju8', 'o': '0plki9', 'p': 'lo0',
        'a': 'qwsz', 's': 'edxzaw', 'd': 'rfcxse', 'f': 'tgvcdr', 'g': 'yhbvft', 'h': 'ujnbgy', 'j': 'ikmnhu', 'k': 'olmji', 'l': 'kop',
        'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm', 'm': 'njk'
        }
        result = []

        for i in range(1, len(self.domain)-1):
            if self.domain[i] in keys:
                for c in range(0, len(keys[self.domain[i]])):
                    result.append(self.domain[:i] + keys[self.domain[i]][c] + self.domain[i] + self.domain[i+1:])
                    result.append(self.domain[:i] + self.domain[i] + keys[self.domain[i]][c] + self.domain[i+1:])

        return result

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
        keys = {
        '1': '2q', '2': '3wq1', '3': '4ew2', '4': '5re3', '5': '6tr4', '6': '7yt5', '7': '8uy6', '8': '9iu7', '9': '0oi8', '0': 'po9',
        'q': '12wa', 'w': '3esaq2', 'e': '4rdsw3', 'r': '5tfde4', 't': '6ygfr5', 'y': '7uhgt6', 'u': '8ijhy7', 'i': '9okju8', 'o': '0plki9', 'p': 'lo0',
        'a': 'qwsz', 's': 'edxzaw', 'd': 'rfcxse', 'f': 'tgvcdr', 'g': 'yhbvft', 'h': 'ujnbgy', 'j': 'ikmnhu', 'k': 'olmji', 'l': 'kop',
        'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm', 'm': 'njk'
        }
        result = []

        for i in range(0, len(self.domain)):
            if self.domain[i] in keys:
                for c in range(0, len(keys[self.domain[i]])):
                    result.append(self.domain[:i] + keys[self.domain[i]][c] + self.domain[i+1:])

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

    def fuzz(self):
        """ Perform a domain fuzz.
        """
        self.domains.append({ 'fuzzer': 'Original*', 'domain': self.domain + '.' + self.tld })

        for domain in self.__bitsquatting():
            self.domains.append({ 'fuzzer': 'Bitsquatting', 'domain': domain + '.' + self.tld })
        for domain in self.__homoglyph():
            self.domains.append({ 'fuzzer': 'Homoglyph', 'domain': domain + '.' + self.tld })
        for domain in self.__hyphenation():
            self.domains.append({ 'fuzzer': 'Hyphenation', 'domain': domain + '.' + self.tld })
        for domain in self.__insertion():
            self.domains.append({ 'fuzzer': 'Insertion', 'domain': domain + '.' + self.tld })
        for domain in self.__omission():
            self.domains.append({ 'fuzzer': 'Omission', 'domain': domain + '.' + self.tld })
        for domain in self.__repetition():
            self.domains.append({ 'fuzzer': 'Repetition', 'domain': domain + '.' + self.tld })
        for domain in self.__replacement():
            self.domains.append({ 'fuzzer': 'Replacement', 'domain': domain + '.' + self.tld })
        for domain in self.__subdomain():
            self.domains.append({ 'fuzzer': 'Subdomain', 'domain': domain + '.' + self.tld })
        for domain in self.__transposition():
            self.domains.append({ 'fuzzer': 'Transposition', 'domain': domain + '.' + self.tld })

        if not self.domain.startswith('www.'):
            self.domains.append({ 'fuzzer': 'Various', 'domain': 'www' + self.domain + '.' + self.tld })
        if '.' in self.tld:
            self.domains.append({ 'fuzzer': 'Various', 'domain': self.domain + '.' + self.tld.split('.')[-1] })
        if self.tld != 'com' and '.' not in self.tld:
            self.domains.append({ 'fuzzer': 'Various', 'domain': self.domain + '-' + self.tld + '.com' })

        self.__filter_domains()
