FROM python:3.8

WORKDIR /bb8

COPY requirements-dev.txt /bb8/
COPY bin/requirements.txt /bb8/
RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements-dev.txt

COPY bin /bb8/bin
COPY tests /bb8/tests

ENTRYPOINT ["pytest", "--teamcity"]
