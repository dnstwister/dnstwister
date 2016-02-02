# DNS Twister

[![Development Build Status](https://travis-ci.org/thisismyrobot/dnstwister.svg?branch=master)](https://travis-ci.org/thisismyrobot/dnstwister)
[![Live Build Status](https://travis-ci.org/thisismyrobot/dnstwister.svg?branch=heroku-deploy)](https://travis-ci.org/thisismyrobot/dnstwister)

A Heroku-hosted version of the very excellent
[dnstwist](https://github.com/elceef/dnstwist).

Hosted [here](https://dnstwister.herokuapp.com).

## DNSTWIST module

This project uses a modified (by me) snapshot of dnstwist, in
dnstwister/dnstwist. The snapshot of dnstwist was added to my project in
[this commit](https://github.com/thisismyrobot/dnstwister/commit/7ca44e96cb3b394d3e85fdb07b20e679e76e0742).

I have left the dnstwist original README and LICENCE in this snapshot, I hope
this is correct attribution and a correct use of the dnstwist project within
my project.

I have applied an "Unlicense" to DNS Twister and I believe
[this is acceptable](http://opensource.stackexchange.com/a/963/3236). If you
come across this repository and disagree with my usage, attribution or
licensing of dnstwist, please raise a Git issue and I will address your
concern as quickly as possible.

## Tests

WIP, run using 'py.test'.

## Google App Engine

This project used to be on GAE
([link may still work?](https://dnstwister.appspot.com)) but has since been
migrated to Heroku. To view the GAE codebase you'll need to look at the
[1.1 tag](https://github.com/thisismyrobot/dnstwister/releases/tag/1.1).
