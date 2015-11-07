""" DNS Twister web app.
"""
import dnstwist
import google.appengine.api.memcache
import google.appengine.api.urlfetch
import jinja2
import json
import operator
import os
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def query_domains(data_dict):
    """ Return the queried domains from a request data dict, or None.

        Domains are newline separated in a textarea.
    """
    try:
        domains = data_dict['domains']
    except KeyError:
        return

    domains = filter(
        None, map(operator.methodcaller('strip'), domains.split('\n'))
    )

    return list(set(domains)) if len(domains) > 0 else None


def analyse(domain):
    """ Analyse a domain.
    """
    data = {'fuzzy_domains': []}
    try:
        fuzzer = dnstwist.DomainFuzzer(domain)
        fuzzer.fuzz()
        data['fuzzy_domains'] = fuzzer.domains
    except dnstwist.InvalidDomain:
        return

    return (domain, data)


class IpResolveHandler(webapp2.RequestHandler):
    """ Resolves Domains to IPs.

        We double-handle off another appspot app as gethostbyname() isn't
        implemented in GAE for Python?!?!?!
    """
    def get(self):
        """ Get the IP for a domain.
        """
        try:
            domain = self.request.GET['domain']
            if not dnstwist.validate_domain(domain):
                raise Exception('Invalid domain')
        except KeyError:
            self.response.out.write('Invalid/missing domain')
            return

        resp = json.loads(google.appengine.api.urlfetch.fetch(
            'https://dnsresolve.appspot.com/?domain={}'.format(domain),
            follow_redirects=False,
        ).content)
        self.response.out.write(json.dumps({'ip': resp['ip']}))


class MainHandler(webapp2.RequestHandler):
    """ Simple web app.
    """
    def post(self):
        """ Handle form submit.
        """
        qry_domains = query_domains(self.request.POST)

        # Handle malformed domains data by redirecting to GET page.
        if qry_domains is None:
            return self.get()

        reports = dict(filter(None, map(analyse, qry_domains)))

        # Handle no valid domains
        if len(reports) == 0:
            return self.get()

        template = JINJA_ENVIRONMENT.get_template('report.html')
        self.response.out.write(template.render(reports=reports))

    def get(self):
        """ Main page.
        """
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.out.write(template.render())
        return


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/ip', IpResolveHandler),
], debug=True)
