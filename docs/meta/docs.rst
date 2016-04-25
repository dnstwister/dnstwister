Building the docs locally
=========================

You need the requirements first:

..  code-block:: sh

    cd docs
    pip install -r requirements.txt
    make html

This populates ./_build/html/

Autobuild
---------

To run the builds on change and to see a "live" preview:

..  code-block:: sh

    sphinx-autobuild . _build_html
