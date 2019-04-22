FROM python:2.7.16-alpine

ARG BRANCH=heroku-deploy

MAINTAINER coolboi567 <PrashantShahi567@gmail.com>

WORKDIR /opt/dnstwister

RUN apk update && apk add --virtual .build-deps gcc musl-dev && \
    apk add git postgresql-dev && \
    git clone https://github.com/thisismyrobot/dnstwister . --branch $BRANCH && \
    pip install pipenv && pipenv install && pipenv install --dev && \
    apk del .build-deps git

ENTRYPOINT ["pipenv", "run"]

CMD ["python", "test_server.py"]
