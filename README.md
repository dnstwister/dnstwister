# DNS Twister

[![Build Status](https://travis-ci.org/thisismyrobot/dnstwister.svg?branch=master)](https://travis-ci.org/thisismyrobot/dnstwister)

A Google App Engine-hosted version of the very excellent
[dnstwist](https://github.com/elceef/dnstwist).

Hosted [here](https://dnstwister.appspot.com).

## DNS Resolve

Because you cannot (yet) do [socket.gethostbyname()](https://docs.python.org/2/library/socket.html#socket.gethostbyname)
in Python on GAE, I have had to write a second application to do this, in
*PHP*.

This application simply returns the IP address of a domain passed to it by
URL.

Each resolve consumes a 'socket' in the quota (of a max 864,000 per day) so we
are deploying multiple copies of this app to distribute the quota usage. You
will need to run 'python build.py [n]' in the 'resolvers' directory, where [n]
is the number of resolver apps to build. You then need to upload these
resolvers one by one. The number built is also recorded in the dnstwister app.
If you run 'python build.py' without a number it will read that number and
just regenerate the same set of instances (useful if you update the dnsresolve
code). Each instance has a number postfixed in its name/id - eg 'dnsresolve0'.

You need pyyaml for this ('pip install pyyaml').

## DNSTWIST module

This project uses a modified (by me) snapshot of dnstwist, in
dnstwister/dnstwist. The snapshot of dnstwist was added to my project in
[this commit](https://github.com/thisismyrobot/dnstwister/commit/7ca44e96cb3b394d3e85fdb07b20e679e76e0742).

I have left the dnstwist original README and LICENCE in this snapshot, I hope
this is correct attribution and a correct use of the dnstwist project within
my project.

I am also using the identical Apache 2.0 license on my project, as I am unsure
how any other license would interact.

If you come across this repository and disagree with my usage, please contact
me via robert @ this is my robot . com and I will rectify it as quickly as
possible.

## Tests

WIP, but run using 'py.test'.
