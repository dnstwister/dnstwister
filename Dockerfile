FROM python:2.7.16-alpine

ARG BRANCH=heroku-deploy

MAINTAINER coolboi567 <coolboi567@gmail.com>

WORKDIR /opt/dnstwister

COPY . /opt/dnstwister

RUN apk update && apk add --virtual .build-deps gcc musl-dev && \
    apk add postgresql-dev && \
    pip install pipenv && pipenv install && pipenv install --dev && \
    apk del .build-deps

ENTRYPOINT ["pipenv", "run"]

CMD ["python", "test_server.py"]
