""" DNS Twister web app.
"""
import dnstwist
import webapp2

class MainHandler(webapp2.RequestHandler):
    """ Simple web app.
    """
    def get(self):
        """ Main page.
        """
        domain = 'www.example.com'
        fuzzer = dnstwist.DomainFuzzer(domain)
        fuzzer.fuzz()
        domains = fuzzer.domains
        self.response.write(str(domains))


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
