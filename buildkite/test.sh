#!/usr/bin/env bash
docker build -f tests/Dockerfile --tag bb8_tests .
docker run --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    bb8_tests
