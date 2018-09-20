# bb8 metrics exporters

A small Flask app, designed to be run inside a docker container, that exposes a single `/metrics` endpoint returning
 metadata from the local starport in a format that Prometheus can use for monitoring.

Automatically installed as part of the starport setup process, but can also be started by running:

```
sudo pip3 install -r requirements.txt
./run ABS_PATH_TO_STARPORT
```
