"""A test that compares the two implementations."""
# -*- coding: UTF-8 -*-
import io
import os

import js2py


def test_js_module_matches_python_module():
    """Run the JS in the browser, compare to the python output."""
    tld_js = load_js('tld.min.js')
    dnstwist_js = load_js('dnstwist.js').strip()[:-2]  # Parenthesis break it?

#    js2py.eval_js(tld_js)
    ev = js2py.eval_js(dnstwist_js)

    import pdb; pdb.set_trace()


#    from js2py.internals import seval
#    seval.eval_js_vm(tld_js + '\n' + dnstwist_js)


def load_js(filename):
    js_src_path = os.path.join(
        os.getcwd(),
        'dnstwister',
        'static',
        'sources',
        filename
    )

    return io.open(
        js_src_path,
        mode='r',
        encoding='utf-8'
    ).read()
