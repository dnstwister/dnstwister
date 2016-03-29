"""Stripe payment gateway."""
import stripe


class StripeService(object):
    """Stripe payments."""
    def __init__(self, api_key, widget_public_key):
        stripe.api_key = api_key
        self._widget_public_key = widget_public_key

    @property
    def widget_public_key(self):
        return self._widget_public_key

    def charge(self, token, email, plan='dnstwister-alerts'):
        """Perform a charge."""
        customer = stripe.Customer.create(
            source=token,
            plan=plan,
            email=email,
        )

        return customer.id
