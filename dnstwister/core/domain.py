import binascii
import idna
import re


VALID_DOMAIN_RE = re.compile(
    r'(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}\.?$)',
    flags=re.IGNORECASE
)

class Domain:
    def __init__(self, domain):
        """Handle all the possible domain types coming in."""
        domain_unicode = self._try_parse_to_unicode_domain(domain)
        if domain_unicode is None:
            raise InvalidDomainException(f'Invalid domain: {repr(domain)}')

        self._domain_unicode = domain_unicode
        self._domain_ascii = idna.encode(domain_unicode).decode()

    def __str__(self):
        if self.to_unicode() == self.to_ascii():
            return self.to_unicode()
        return f'{self.to_unicode()} ({self.to_ascii()})'

    def __repr__(self):
        return self.to_ascii()

    def __eq__(self, other):
        other_domain = self._try_parse_to_unicode_domain(other)
        if other_domain is None:
            return False

        return Domain(other_domain).to_ascii() == self.to_ascii()

    def __hash__(self):
        return hash(self._domain_unicode)

    @staticmethod
    def _try_parse_to_unicode_domain(domain):
        try:

            # If we have a domain object, woo.
            if isinstance(domain, Domain):
                return domain.to_unicode()

            # If we have bytes, make it a string.
            try:
                domain = domain.decode()
            except AttributeError:
                pass

            # If domain is idna already, extract the unicode string.
            try:
                un_idna_domain = idna.decode(domain)
                if un_idna_domain != domain:
                    domain = un_idna_domain
            except:
                pass

            if len(domain) > 255:
                return

            if VALID_DOMAIN_RE.match(idna.encode(domain).decode()) is None:
                return

            return domain
        except:
            return

    @classmethod
    def try_parse(cls, domain):
        unicode_domain = cls._try_parse_to_unicode_domain(domain)
        if unicode_domain is not None:
            return Domain(unicode_domain)

    def to_unicode(self):
        return self._domain_unicode

    def to_ascii(self):
        return self._domain_ascii

    def to_hex(self):
        idna_bytes = self._domain_ascii.encode()
        return binascii.hexlify(idna_bytes).decode()


class InvalidDomainException(Exception):
    pass
