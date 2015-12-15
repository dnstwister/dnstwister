""" DNS Twister web app.
"""
import base64
import google.appengine.api.memcache
import jinja2
import json
import logging
import os
import socket
import tools
import urllib
import webapp2


# Possible rendered errors, indexed by integer in 'error' GET param.
ERRORS = (
    'No valid domains submitted.',
    'Invalid report URL.',
    'No domains submitted.',
)


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join((
        os.path.dirname(__file__),
        'templates'
    ))),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)


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


class ReportHandler(webapp2.RequestHandler):
    """ Report rendering.
    """
    def _report(self, qry_domains):
        """ Render and return the report.
        """
        reports = dict(filter(None, map(tools.analyse, qry_domains)))

        # Handle no valid domains by redirecting to GET page.
        if len(reports) == 0:
            logging.error(
                'No valid domains found in {}'.format(qry_domains)
            )
            return self.redirect('/?error=0')

        template = JINJA_ENVIRONMENT.get_template('report.html')
        self.response.out.write(template.render(reports=reports))

    def get(self):
        """ Handle redirect from form submit.
        """
        # Try to parse out the list of domains
        try:
            qry_domains = map(
                base64.b64decode,
                self.request.GET['q'].split(',')
            )
        except Exception as ex:
            logging.error('Unable to decode valid domains from q GET param')
            return self.redirect('/?error=1')

        return self._report(qry_domains)


    def post(self):
        """ Handle form submit.
        """
        qry_domains = tools.query_domains(self.request.POST)

        # Handle malformed domains data by redirecting to GET page.
        if qry_domains is None:
            logging.error(
                'No valid domains in POST dict {}'.format(self.request.POST)
            )
            return self.redirect('/?error=2')

        # Attempt to create a <= 200 character GET parameter from the domains
        # so we can redirect to that (allows bookmarking). As in '/ip' we use
        # b64 to hide the domains from firewalls that already block some of
        # them.
        params = urllib.urlencode({
            'q': ','.join(map(base64.b64encode, qry_domains))
        })
        if len(params) <= 200:
            return self.redirect('?{}'.format(params))

        # If there's a ton of domains, just to the report.
        return self._report(qry_domains)


class MainHandler(webapp2.RequestHandler):
    """ Simple web app.
    """
    def get(self):
        """ Main page.
        """
        error = None
        try:
            error = ERRORS[int(self.request.GET['error'])]
        except:
            # This will fail on no error, an error that can't be converted to
            # an integer and an error that can be converted to an integer but
            # is not within the range of the tuple of errors. We don't need to
            # log these situations.
            pass

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.out.write(template.render(error=error))
        return


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/report', ReportHandler),
    ('/ip', IpResolveHandler),
])


def main():
    """ Main method to set up logging only.
    """
    logging.getLogger().setLevel(logging.DEBUG)
    webapp2.util.run_wsgi_app(app)


if __name__ == '__main__':
    main()
