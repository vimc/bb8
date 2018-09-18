# bb8 metrics exporters

A small Flask app, designed to be run insied a docker container, that exposes a single `/metrics` endpoint returning
 the status of the local bb8 instance in a format that Prometheus can use for monitoring.

Installed as part of the bb8 install process, but to start as a standalone app for local development:

```
sudo pip3 install -r requirements.txt
./run
```