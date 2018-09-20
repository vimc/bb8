FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY requirements.txt .
COPY app/metrics/requirements.txt ./app/metrics/
RUN pip3 install -r requirements.txt
RUN pip3 install -r app/metrics/requirements.txt

ENV STATIC_INDEX 1
COPY app /app
