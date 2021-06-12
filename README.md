# dnstwister

A Python 3 Heroku-hostable web-application wrapping the excellent
[dnstwist](https://github.com/elceef/dnstwist).

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/thisismyrobot/dnstwister/tree/heroku-deploy)

## dnstwist

In [the author's](https://github.com/elceef) words, dnstwist helps you
["...find similar-looking domains that adversaries can use to attack
you..."](https://github.com/elceef/dnstwist/blob/master/docs/README.md)

This project, __dnstwister__, gives you access to the power of dnstwist via a
convenient Heroku-deployable Python flask-based web interface and offers
csv/json reports and a fully featured RESTful API.

This project uses a modified version of dnstwist, in
[dnstwister/dnstwist](dnstwister/dnstwist).

I have kept the original dnstwist README and LICENCE but I have applied an
"Unlicense" to __dnstwister__.

Though the licences are different (dnstwist 
[uses](https://github.com/elceef/dnstwist/blob/master/docs/LICENSE) an
Apache licence),
[this is an acceptable](http://opensource.stackexchange.com/a/963/3236) use of
dnstwist in my project.

## [dnstwister.report](https://dnstwister.report)

The SaaS offering [dnstwister.report](https://dnstwister.report) grew out of
this repository, but as of October 2019 the core code that runs
[dnstwister.report](https://dnstwister.report) was forked from this
__dnstwister__ repository into a private repository. This was done to:

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
here](https://github.com/thisismyrobot/dnstwister/tree/master/dnstwister/dnstwist),
including the original Apache LICENCE.__

Pull requests against this repository may or may not be merged into this
repository and/or the private repository, as appropriate.

## Contributors

 * [@elceef](https://github.com/elceef) (dnstwist itself)
 * [@peterwallhead](http://github.com/peterwallhead) (mobile UI assistance)
 * [@prashant-shahi](https://github.com/prashant-shahi) (docker configuration)
 * [@wesinator](https://github.com/wesinator) (file export improvements)
 * [@ninoseki](https://github.com/ninoseki) (api improvements)

## Developing and running dnstwister

You need Python 3.9.

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

# Building dnstwister image using Dockerfile
docker build -t dnstwister .

# Running the application inside a container
docker run -td -p 5000:5000 --name myapp dnstwister
```

Now, go to `http://localhost:5000` using any browser to use dnstwister.

### Fetching pre-built image

Alternatively, you can pull the pre-built image from DockerHub, and run
locally. This way, you wouldn't have to wait for the build time.

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
