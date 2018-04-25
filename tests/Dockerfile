FROM python:3

WORKDIR /bb8

COPY requirements-dev.txt /bb8
COPY bin/requirements.txt /bb8/bin/
RUN pip3 install -r bin/requirements.txt
RUN pip3 install -r requirements-dev.txt

COPY bin /bb8/bin
COPY tests /bb8/tests

ENTRYPOINT ["pytest", "--teamcity"]
