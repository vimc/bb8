FROM python:3

WORKDIR /bb8
COPY bin /bb8/bin
COPY tests /bb8/tests
COPY requirements-dev.txt /bb8

RUN pip3 install -r bin/requirements.txt
RUN pip3 install -r requirements-dev.txt

ENTRYPOINT ["pytest"]
