# Current state of dnstwister/please read before suggesting changes

As of October 2019 __dnstwister__ is going through a number of breaking
changes to support the cut-over to Python 3 before 2020. If you're looking for
a stable Python 2 version of __dnstwister__ then
[2.14](https://github.com/thisismyrobot/dnstwister/releases/tag/2.14) is the
one you want.

### NOTE: This means that this README and/or the code in this master branch might not work at this point in time. This notice will be removed once the codebase has stabilised again. As mentioned above, the current stable version of __dnstwister__ is [2.14](https://github.com/thisismyrobot/dnstwister/releases/tag/2.14). Thank you for your patience as I complete this cut-over.

# dnstwister

A Heroku-hosted version of the very excellent
[dnstwist](https://github.com/elceef/dnstwist).

|production|development|
|:--------:|:---------:|
|[![Production Branch Build Status](https://travis-ci.org/thisismyrobot/dnstwister.svg?branch=heroku-deploy)](https://travis-ci.org/thisismyrobot/dnstwister)|[![Development Branch Build Status](https://travis-ci.org/thisismyrobot/dnstwister.svg?branch=master)](https://travis-ci.org/thisismyrobot/dnstwister)|

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/thisismyrobot/dnstwister/tree/heroku-deploy)

## dnstwist vs. dnstwister

In [the author's](https://github.com/elceef) words, dnstwist helps you
["...find similar-looking domains that adversaries can use to attack
you..."](https://github.com/elceef/dnstwist/blob/master/docs/README.md)

This project, __dnstwister__, gives you access to the power of dnstwist via a
convenient Heroku-deployable Python flask-based web interface and offers
csv/json reports and a fully featured RESTful API.

## dnstwist module

This project currently uses a modified version of dnstwist, in
[dnstwister/dnstwist](dnstwister/dnstwist).

I have kept the original dnstwist README and LICENCE but I have applied an
"Unlicense" to __dnstwister__.

Though the licences are different (dnstwist 
[uses](https://github.com/elceef/dnstwist/blob/master/docs/LICENSE) an
Apache licence),
[this is an acceptable](http://opensource.stackexchange.com/a/963/3236) use of
dnstwist in my project.

## What about [dnstwister.report](https://dnstwister.report)?

As of October 2019 the core code that runs
[dnstwister.report](https://dnstwister.report) was forked from this
__dnstwister__ open-source repository into a private repository. This was done
to:

 * Clearly separate the code required to run a web-scale SaaS offering from
that required to host your own __dnstwister__ instance - for instance email
gateways and FaaS endpoints.

* Allow for the introduction of my own IP beyond that of the core
[dnstwist](https://github.com/elceef/dnstwist) module authored by
[elceef](https://github.com/elceef).

To ensure I am respecting the [dnstwist
licence](https://github.com/elceef/dnstwist/blob/master/docs/LICENSE) the
dnstwist module embedded in this repository will __always__ match that used in
[dnstwister.report](https://dnstwister.report).

__The current version of dnstwist used in this repository and in
[dnstwister.report](https://dnstwister.report) is [available
here](/tree/master/dnstwister/dnstwist), including the original Apache
LICENCE.__

## Contributors

 * [@elceef](https://github.com/elceef) (dnstwist itself)
 * [@peterwallhead](http://github.com/peterwallhead) (mobile UI assistance)
 * [@prashant-shahi](https://github.com/prashant-shahi) (docker configuration)
 * [@wesinator](https://github.com/wesinator) (file export improvements)
 * [@ninoseki](https://github.com/ninoseki) (api improvements)

## Developing dnstwister

You need Python 3.7.4.

Once-off setup:

```sh
pip install pipenv
pipenv install --dev
```

Running:

```sh
pipenv run python local_server.py
```

And browse via http://localhost:5000

## Running dnstwister using Docker

If you don't have [Docker](https://hub.docker.com/) installed, you can click
[here](https://www.docker.com/community-edition/ "Docker : Community Edition")
for **Docker CE**, and follow the installation steps.

### Building and Running locally

```sh
# Cloning latest source code
git clone https://github.com/thisismyrobot/dnstwister

# Changing directory
cd dnstwister

# Checkout to the stable branch i.e. heroku-deploy
git checkout heroku-deploy

# Building dnstwister image using Dockerfile
docker build -t dnstwister .

# Running the application inside a container
docker run -td -p 5000:5000 --name myapp dnstwister
```

Now, go to `http://localhost:5000` using any browser to use dnstwister.

### Fetching pre-built image

Alternatively, you can pull the pre-built image from DockerHub, and run
locally. This way, you wouldn't have to wait for the build time. The image
present in docker hub is from the stable branch **heroku-deploy**.

```sh
docker pull dnstwister/dnstwister:2.9.3
docker run -td -p 5000:5000 --name myapp dnstwister/dnstwister:2.9.3
```

Now, go to `http://localhost:5000` using any browser to use dnstwister.

## Tests

Running:

```sh
pipenv run py.test
```

## Say hello

I'd love to hear your feedback so [email me](mailto:hello@dnstwister.report),
fire off a [tweet](https://twitter.com/dnstwister) in my general direction! :)
