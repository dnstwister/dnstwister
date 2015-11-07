""" DNS Twister web app.
"""
import dnstwist
import jinja2
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
    ('/', MainHandler)
], debug=True)
