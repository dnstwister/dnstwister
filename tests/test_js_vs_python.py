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

    missing_from_js = []
    for d in py_domains:
        if d not in js_domains:
            missing_from_js.append(d)

    assert missing_from_js == []


def test_python_module_has_all_the_js_module_domains():
    """Run the JS in the browser, compare to the python output."""
    domain = 'abc.com'
    js_domains = load_js_domains(domain)
    py_domains = load_py_domains(domain)

    missing_from_py = []
    for d in js_domains:
        if d not in py_domains:
            missing_from_py.append(d)

    assert missing_from_py == []


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
        cursor += result['cursor'] + 1
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
