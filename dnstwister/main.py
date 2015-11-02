""" DNS Twister web app.
"""
import dnstwistfork.dnstwist
import webapp2

class MainHandler(webapp2.RequestHandler):
    """ Simple web app.
    """
    def get(self):
        """ Main page.
        """
        domain = 'www.example.com'
        fuzzer = dnstwistfork.dnstwist.fuzz_domain(domain)
        fuzzer.fuzz()
        domains = fuzzer.domains
        self.response.write(str(domains))


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
