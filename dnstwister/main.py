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
import socket
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
        # We assume we don't resolve the IP but that we had no error in the
        # attempt.
        ip = None
        error = False

        # Firstly, try and parse a valid domain (base64-encoded) from the
        # 'b64' GET parameter.
        domain = tools.parse_domain(self.request.GET)
        if domain is None:
            logging.error('Unable to decode valid domain from b64 GET param')
            self.abort(500)

        # Next, attempt to resolve via memcache. This returns None if not
        # found, as upposed to False when we found it but it didn't resolve
        # last time.
        mc_key = 'ip:{}'.format(domain)
        try:
            ip = google.appengine.api.memcache.get(mc_key)
        except Exception as ex:
            logging.error(
                'Unable to query memcache for {} ({})'.format(
                    mc_key, ex.message
                )
            )

        # If we got a memcache miss, attempt to resolve.
        if ip is None:

            try:

                ip = socket.gethostbyname(domain)

            except socket.gaierror:

                # Indicates failure to resolve to IP address, not an error in
                # the attempt.
                ip = False

            except Exception as ex:

                # Happens due to DNS issues, we can hand off to third party
                # here?
                logging.error(
                    'Failed local resolution of domain {} ({})'.format(
                        domain, ex.message
                    )
                )
                ip = False
                error = True

            # If we successfully attempted to resolve, store the result.
            if error is False:
                try:
                    google.appengine.api.memcache.set(mc_key, ip, time=86400)
                except Exception as ex:
                    logging.error(
                        'Unable to store in memcache for {}:{} ({})'.format(
                            mc_key, ip, ex.message
                        )
                    )

        # Response IP is now an IP address, or False.
        self.response.out.write(json.dumps(
            {'ip': ip, 'error': error})
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
