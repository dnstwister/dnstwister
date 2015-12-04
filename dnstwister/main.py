""" DNS Twister web app.
"""
import base64
import dnstwist
import google.appengine.api.memcache
import google.appengine.api.urlfetch
import jinja2
import json
import operator
import os
import random
import resolvers
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join((
        os.path.dirname(__file__),
        'templates'
    ))),
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
        results = list(fuzzer.domains)

        # Add a base64 encoded version of the domain for the later IP
        # resolution. We do this because the same people who may use this app
        # already have blocking on things like www.exampl0e.com in URLs...
        for r in results:
            r['b64'] = base64.b64encode(r['domain'])
        data['fuzzy_domains'] = results
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
            domain = base64.b64decode(self.request.GET['b64'])
            if not dnstwist.validate_domain(domain):
                raise Exception('Invalid domain')
            # TODO: log...
        except:
            self.response.out.write(json.dumps({'ip': None}))
            return

        # Attempt to get from memcache
        ip = None
        mc_key = 'ip:{}'.format(domain)
        cached_ip = google.appengine.api.memcache.get(mc_key)

        # If not in cache, get via microservice
        if cached_ip is None:

            # Pick a resolver app at "random".
            appid = 'dnsresolve{}'.format(
                random.randint(0, resolvers.COUNT - 1)
            )

            try:
                resolved_ip = json.loads(google.appengine.api.urlfetch.fetch(
                    'https://{}.appspot.com/?d={}'.format(appid, domain),
                    follow_redirects=False,
                ).content)['ip']

                if resolved_ip is None:
                    # We set 'False' for a non-resolvable IP, though we return
                    # None in the JSON in this circumstance. This is because
                    # memcache hits return None when nothing is found. Expire
                    # cache entry after 24 hours.
                    google.appengine.api.memcache.set(mc_key, False, time=86400)
                else:
                    ip = resolved_ip
                    google.appengine.api.memcache.set(mc_key, ip, time=86400)

            except Exception as _:
                # Any failure to resolve an IP doesn't update memcache. TODO:
                # return error/distinguish between memcache set() error and
                # failure to resolve ip...
                pass

        # False indicates was not resolved last time, we return None in that
        # instance (so no-op needed there). If the ip is not None or False, we
        # return it.
        elif cached_ip != False:
            ip = cached_ip

        self.response.out.write(json.dumps({'ip': ip}))


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
            # TODO: Log / help text...
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
