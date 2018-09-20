# bb8 metrics exporters

A small Flask app, designed to be run inside a docker container, that exposes a single `/metrics` endpoint returning
 the status of the local bb8 instance in a format that Prometheus can use for monitoring.

To start:

```
sudo pip3 install -r requirements.txt
./run
```