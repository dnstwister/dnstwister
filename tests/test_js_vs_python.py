"""A test that compares the two implementations."""
# -*- coding: UTF-8 -*-
import io
import os

import js2py

import dnstwister.dnstwist.dnstwist as dnstwist


def test_js_module_has_all_the_python_module_domains():
    """Run the JS in the browser, compare to the python output."""
    domain = 'abc.com'
    js_domains = load_js_domains(domain)
    py_domains = load_py_domains(domain)

    missing_from_js = [d
                       for d
                       in py_domains
                       if d not in js_domains]

    assert missing_from_js == [
        'wwabc.com',
        'wwwabc.com',
        'www-abc.com',
        'abccom.com'
    ]


def test_python_module_has_all_the_js_module_domains():
    """Run the JS in the browser, compare to the python output."""
    domain = 'abc.com'
    js_domains = load_js_domains(domain)
    py_domains = load_py_domains(domain)

    missing_from_py = [d
                       for d
                       in js_domains
                       if d not in py_domains]

    assert missing_from_py == [
        u'abxc.com',
        u'abxc.com',
        u'abxc.com',
        u'abdc.com',
        u'abdc.com',
        u'abdc.com',
        u'abfc.com',
        u'abfc.com',
        u'abfc.com'
    ]


def load_py_domains(domain):
    fuzzer = dnstwist.fuzz_domain('abc.com')
    fuzzer.fuzz()
    return [d['domain-name']
            for d
            in fuzzer.domains]


def load_js_domains(domain):
    tld_js = load_js('tld.min.js')
    dnstwist_js = load_js('dnstwist.js')
    js2py_obj = js2py.eval_js(tld_js + '\n' + dnstwist_js)

    cursor = 0
    domains = []
    while True:
        result = js2py_obj.tweak(domain, cursor)
        if result is None:
            break
        domains.append(result['domain'])
        cursor = result['cursor'] + 1
    return domains


def load_js(filename):
    js_src_path = os.path.join(
        os.getcwd(),
        'dnstwister',
        'static',
        'sources',
        filename
    )

    return io.open(js_src_path, mode='r', encoding='utf-8').read()
