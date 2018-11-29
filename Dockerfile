FROM python:3.7-alpine

RUN apk add --update alpine-sdk libffi-dev libxml2-dev libxslt-dev python3-dev build-base linux-headers pcre-dev openssl-dev supervisor expect

RUN adduser -D ns2-web
WORKDIR /home/ns2-web
COPY requirements.txt requirements.txt

RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY . .

RUN chown -R ns2-web:ns2-web ./
USER ns2-web

EXPOSE 8000
ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf 

LABEL "com.centurylinklabs.watchtower.enable"="true"
ENTRYPOINT ["/usr/bin/supervisord"]