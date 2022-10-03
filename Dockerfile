FROM python:3.8

WORKDIR /bb8
COPY bin/requirements.txt /bb8/
RUN pip3 install -r requirements.txt

COPY bin /bb8

COPY secrets /bb8/etc/secrets
COPY source-config.json /bb8/etc/source-config.json

ARG TARGETS
RUN python setup.py $TARGETS

ENTRYPOINT ["python", "main.py"]
