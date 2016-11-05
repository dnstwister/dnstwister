# dnstwister

A Heroku-hosted version of the very excellent
[dnstwist](https://github.com/elceef/dnstwist).

[![Production Branch Build Status](https://travis-ci.org/thisismyrobot/dnstwister.svg?branch=heroku-deploy)](https://travis-ci.org/thisismyrobot/dnstwister)
[![Production Branch Coverage Status](https://coveralls.io/repos/github/thisismyrobot/dnstwister/badge.svg?branch=heroku-deploy)](https://coveralls.io/github/thisismyrobot/dnstwister?branch=heroku-deploy)
[![Production Branch Code Health](https://landscape.io/github/thisismyrobot/dnstwister/heroku-deploy/landscape.svg?style=flat)](https://landscape.io/github/thisismyrobot/dnstwister/heroku-deploy)

[![Development Branch Build Status](https://travis-ci.org/thisismyrobot/dnstwister.svg?branch=master)](https://travis-ci.org/thisismyrobot/dnstwister)
[![Development Branch Coverage Status](https://coveralls.io/repos/github/thisismyrobot/dnstwister/badge.svg?branch=master)](https://coveralls.io/github/thisismyrobot/dnstwister?branch=master)
[![Development Branch Code Health](https://landscape.io/github/thisismyrobot/dnstwister/master/landscape.svg?style=flat)](https://landscape.io/github/thisismyrobot/dnstwister/master)

## What is dnstwister?

In the author's words, dnstwist helps you
["...find similar-looking domains that adversaries can use to attack you..."](https://github.com/elceef/dnstwist/blob/master/docs/README.md)

This project, __dnstwister__, gives you access to the power of dnstwist via a
convenient web interface and offers email alerts, Atom feeds, csv/json reports
and a fully featured RESTful API.

Oh, and it's 100% free.

__dnstwister__ is hosted at [https://dnstwister.report](https://dnstwister.report).

## dnstwist module

This project currently uses a modified snapshot of version 1.02 of dnstwist, in
[dnstwister/dnstwist](dnstwister/dnstwist).

I have kept the original dnstwist README and LICENCE in that snapshot but I
have applied an "Unlicense" to __dnstwister__.

I understand - though the licences are different (dnstwist 
[uses](https://github.com/elceef/dnstwist/blob/master/docs/LICENSE) an
Apache licence) - that [this is acceptable](http://opensource.stackexchange.com/a/963/3236)
use of dnstwist in my project.

If you come across this repository and disagree with my usage, attribution or
licensing of dnstwist, please raise a
[Git issue](https://github.com/thisismyrobot/dnstwister/issues) and I will
address your concern as quickly as possible.

## Tests

Run 'py.test'.

## Google App Engine version

This project used to be hosted on Google App Engine (GAE) but has since been migrated to Heroku. To view
the GAE codebase you'll need to look at the [1.1
tag](https://github.com/thisismyrobot/dnstwister/releases/tag/1.1).
