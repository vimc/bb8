FROM python:3

WORKDIR /bb8
COPY bin /bb8
RUN pip3 install -r /bb8/requirements.txt

COPY secrets /bb8/etc/secrets
COPY source-config.json /bb8/etc/source-config.json

ARG TARGETS
RUN python setup.py $TARGETS
