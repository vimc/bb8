FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY requirements.txt .
COPY app/metrics/requirements.txt ./app/metrics/
RUN pip3 install -r requirements.txt
RUN pip3 install -r app/metrics/requirements.txt

# Install docker
RUN apt-get update
RUN apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        software-properties-common
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
RUN add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"
RUN apt-get update
RUN apt-get install -y docker-ce


ENV STATIC_INDEX 1
COPY app /app
