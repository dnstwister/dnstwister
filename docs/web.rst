Help
====

What is dnstwister?
-------------------

**dnstwister** generates a list of domain names that are similar to one that
you provide, checking to see if any of them are registered.

Why use dnstwister?
-------------------

**dnstwister** can tell you if someone may be using a domain like yours for
malicious purposes like `phishing <https://en.wikipedia.org/wiki/Phishing>`_
or trademark infringement.

For instance as the owner of the domain **dnstwister.report** I would be very
interested to know if someone registered the 'dnstw1ster.report' domain and
started sending malicious password-reset emails to users.

**dnstwister** makes it trivial to `answer that exact question 
<https://dnstwister.report/search?ed=646e73747769737465722e7265706f7274>`_.

Email alerts |email_icon|
-------------------------

..  |email_icon| image:: https://dnstwister.report/static/email.png
    :height: 20
    :width: 20
    :target: #email-and-atom-alerts-email-icon-feed-icon

So you don't have to keep coming back and running searches, **dnstwister** can
also alert you via Email within 24 hours if a **new** domain is registered
like yours, if an existing domain has changed IP address or has even been
unregistered. To subscribe you simply click on the appropriate icon after
performing a search.

"Noisy" domains
~~~~~~~~~~~~~~~

Some domains change IP address all the time, or are constantly registered then
unregistered. This is almost always due to the domain being parked. You can
hide these domains from your email alerts by ticking the "Ignore domains that
change all the time." box when signing up.

Ticking this box will improve the quality of the alerts you get, ensuring the
important alerts aren't lost in the noise.

In the future existing subscribers will be able to change this setting too.

How it works
------------

Let's say you `do a dnstwister search on www.example.com
<https://dnstwister.report/search/7777772e6578616d706c652e636f6d>`_.

Firstly, **dnstwister** will generate a list of similar domains - something
like:

..  code-block:: none

    www.examplea.com
    www.examplec.com
    ...
    www.axample.com
    ...

(you can `thank dnstwist <https://github.com/elceef/dnstwist>`_ for that
awesome algorithm)

For each of these domains, **dnstwister** will attempt to resolve a `DNS A
record <https://en.wikipedia.org/wiki/List_of_DNS_record_types#A>`_ - the
mapping between a domain name and an IP address. This will look something
like: 

..  image:: _static/search.png

Successfully resolving a domain to an IP address indicates someone has
registered it.

FAQ
---

1. Why do you use `hexadecimal <https://en.wikipedia.org/wiki/Hexadecimal>`_
for all the domain references?

Corporate firewalls and proxies will often block malicious domains even if
they are only part of a query string in the URL- eg
`https://dnstwister.report/search/[malicious domain]
<#faq>`_.

By encoding the domain as hexidecimal you can still perform your searches and
analysis.

API
---

We have a JSON `API available <https://dnstwister.report/api/>`_ for you to
play with, if you're keen.
