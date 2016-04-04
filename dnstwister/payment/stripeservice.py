"""Stripe payment gateway."""
import os
import stripe


def env_keys():
    """Return the api and public keys from environment variables."""
    return os.environ['STRIPE_API_KEY'], os.environ['STRIPE_PUBLIC_KEY']


class StripeService(object):
    """Stripe payments."""
    def __init__(self):
        self._keys_setup = False

    def _setup_keys(self):
        stripe.api_key, self._widget_public_key = env_keys()

    @property
    def widget_public_key(self):
        if not self._keys_setup:
            self._setup_keys()
            self._keys_setup = True
        return self._widget_public_key

    def charge(self, token, email, plan='dnstwister-alerts'):
        """Perform a charge."""
        if not self._keys_setup:
            self._setup_keys()
            self._keys_setup = True

        customer = stripe.Customer.create(
            source=token,
            plan=plan,
            email=email,
        )

        return customer.id

    def cancel(self, customer_id):
        """Cancel a subscription."""

        # TODO: need to fix subscriptions and to separate customer from sub.
        customer = stripe.Customer.retrieve(customer_id)
        customer.subscriptions.retrieve('sub_3R3PlB2YlJe84a').delete(
            at_period_end=True
        )
