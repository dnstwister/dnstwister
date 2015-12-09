""" DNS Twister web app.
"""
import base64
import dnstwist
import google.appengine.api.memcache
import google.appengine.api.urlfetch
import jinja2
import json
import logging
import os
import random
import resolvers
import tools
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join((
        os.path.dirname(__file__),
        'templates'
    ))),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


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
        except Exception as ex:
            logging.error(
                'Unable to decode valid domain from b64 GET param ({})'.format(
                    ex.message
                )
            )
            self.response.out.write(
                json.dumps({'ip': None, 'error': True})
            )
            return

        # Attempt to get from memcache
        ip = None
        mc_key = 'ip:{}'.format(domain)
        cached_ip = google.appengine.api.memcache.get(mc_key)

        # If in cache
        if cached_ip is not None:

            # We represent a cache hit for an unresolved IP as False but we
            # return None in the JSON.
            ip = None if cached_ip == False else cached_ip

        # If not in cache, get via microservice
        else:

            # Pick a resolver app at "random".
            appid = 'dnsresolve{}'.format(
                random.randint(0, resolvers.COUNT - 1)
            )

            resolver_url = 'https://{}.appspot.com/?d={}'.format(appid, domain)
            try:

                google.appengine.api.urlfetch.set_default_fetch_deadline(60)
                payload = json.loads(google.appengine.api.urlfetch.fetch(
                    resolver_url, follow_redirects=False,
                ).content)

                if payload['error'] == True:
                    raise Exception('error...')

                ip = payload['ip']

            except Exception as ex:

                logging.error(
                    'Unable to req IP for domain: {} via {} ({})'.format(
                        domain, resolver_url, ex.message,
                    )
                )

                # Any issue in resolving (503 for instance, for quota
                # exhaustion, or JSON malformed) needs the error flag set.
                self.response.out.write(
                    json.dumps({'ip': None, 'error': True})
                )
                return

            # We're here because the resolution request succeeded, even if the
            # IP wasn't resolved. Attempt to store the value in cache for next
            # time.
            try:

                if ip is not None:
                    google.appengine.api.memcache.set(mc_key, ip, time=86400)
                else:
                    # We set 'False' for a non-resolvable IP, though we return
                    # None in the JSON in this circumstance. This is because
                    # memcache hits return None when nothing is found. Expire
                    # cache entry after 24 hours.
                    google.appengine.api.memcache.set(mc_key, False, time=86400)

            except:
                # TODO: handle memcache error...
                logging.error(
                    'Unable to store {}:{} in memcache'.format(
                        mc_key, ip
                    )
                )

        # Response IP is now an IP address, or None.
        self.response.out.write(json.dumps(
            {'ip': ip, 'error': False})
        )


class MainHandler(webapp2.RequestHandler):
    """ Simple web app.
    """
    def post(self):
        """ Handle form submit.
        """
        qry_domains = tools.query_domains(self.request.POST)

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
    ('/test', TestResolver),
])


def main():
    # Set the logging level in the main function See the section on <a
    # href="/appengine/docs/python/#Python_App_caching">Requests and App
    # Caching</a> for information on how App Engine reuses your request
    # handlers when you specify a main function
    logging.getLogger().setLevel(logging.DEBUG)
    webapp2.util.run_wsgi_app(app)


if __name__ == '__main__':
    main()
