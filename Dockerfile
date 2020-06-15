FROM python:3.6-alpine

ENV PYTHONUNBEFFERED 1

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache g++ gcc libxslt-dev
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user