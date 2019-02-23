"""A test that compares the two implementations."""
import os

import js2py


def test_js_module_matches_python_module():
    """Run the JS in the browser, compare to the python output."""
    tld_js = load_js('tld.min.js')
    dnstwist_js = load_js('dnstwist.js')

    js2py.eval_js(tld_js + dnstwist_js)


def load_js(filename):
    js_src_path = os.path.join(
        os.getcwd(),
        'dnstwister',
        'static',
        'sources',
        filename
    )

    with open(js_src_path, 'r') as js_f:
        return js_f.read()
