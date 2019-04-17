FROM python:2.7.16-alpine

MAINTAINER Prashant Shahi <coolboi567@gmail.com>

RUN apk update && \
    apk add --virtual .build-deps gcc musl-dev && \
    apk add git postgresql-dev && \
    git clone https://github.com/thisismyrobot/dnstwister

WORKDIR /dnstwister

RUN pip install pipenv && \
    pipenv install && \
    pipenv install --dev && \
    apk del .build-deps git

ENTRYPOINT ["pipenv", "run"]

CMD ["python", "test_server.py"]