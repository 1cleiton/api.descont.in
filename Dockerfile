FROM python:3.6-alpine

ENV PYTHONUNBEFFERED 1

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache g++ gcc libxslt-dev
RUN apk add --update --no-cache postgresql-client
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && pip install --no-cache-dir psycopg2 \
    && apk del --no-cache .build-deps
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user