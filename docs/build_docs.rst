Building the docs locally
=========================

You need the Python environment set up first first (see
[README.md](https://github.com/thisismyrobot/dnstwister/blob/master/README.md)):

..  code-block:: sh

    make html

This populates ./_build/html/

Autobuild
---------

To run the builds on change and to see a "live" preview:

..  code-block:: sh

    sphinx-autobuild . _build_html
