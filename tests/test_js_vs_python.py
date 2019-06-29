# -*- coding: UTF-8 -*-
"""A test that compares the two implementations.

The comparison runs the JavaScript implementation in js2py and compares it
to the original Python version (from elceef) that I've slightly modified.
"""
import io
import os

import js2py

import dnstwister.dnstwist.dnstwist as dnstwist


JS = None


def test_js_module_has_all_the_python_module_domains():
    """Run the JS, compare to the python output."""
    domain = 'abcdefghijk-lmnopqrstuvwxyz.com'
    js_domains = load_js_domains(domain)
    py_domains = load_py_domains(domain)

    missing_from_js = [d
                       for d
                       in py_domains
                       if d not in js_domains]

    assert missing_from_js == []


def test_js_module_handles_short_domains():
    """'à.com' needs to not return '.com' as a result."""
    domain = 'à.com'.decode('utf-8')
    js_domains = load_js_domains(domain)

    assert '.com' not in js_domains


def test_python_module_has_all_the_js_module_domains():
    """Run the JS, compare to the python output."""
    domain = 'abcdefghijk-lmnopqrstuvwxyz.com'
    js_domains = load_js_domains(domain)
    py_domains = load_py_domains(domain)

    missing_from_py = [d
                       for d
                       in js_domains
                       if d not in py_domains]

    assert missing_from_py == []


def load_py_domains(domain):
    fuzzer = dnstwist.fuzz_domain(domain)
    fuzzer.fuzz()
    return [d['domain-name'].encode('utf-8')
            for d
            in fuzzer.domains]


def load_js_domains(domain):
    # Save a little time in the tests.
    global JS
    if JS is None:
        JS = build_js()

    cursor = 0
    domains = []
    while True:
        result = JS.tweak(domain, cursor)
        if result is None:
            break
        domains.append(result['domain'].encode('utf-8'))
        cursor = result['cursor'] + 1
    return domains


def build_js():
    tld_js = load_js('tld.min.js')
    dnstwist_js = load_js('dnstwist.js')
    js2py_obj = js2py.eval_js(tld_js + '\n' + dnstwist_js)
    return js2py_obj


def load_js(filename):
    js_src_path = os.path.join(
        os.getcwd(),
        'dnstwister',
        'static',
        'sources',
        filename
    )

    return io.open(js_src_path, mode='r', encoding='utf-8').read()
