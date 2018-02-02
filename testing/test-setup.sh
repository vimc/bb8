#!/usr/bin/env bash
set -ex
HERE=${BASH_SOURCE%/*}
BB8_ROOT=$(readlink -f ${HERE}/..)

if [ "$VAULT_AUTH_GITHUB_TOKEN" = "" ]; then
    echo "Variable VAULT_AUTH_GITHUB_TOKEN must be set"
    exit 1
fi

IMAGE_NAME=bb8_setup

docker build --rm -t $IMAGE_NAME $HERE
docker run --rm -v ${BB8_ROOT}:/src \
       -e VAULT_AUTH_GITHUB_TOKEN=$VAULT_AUTH_GITHUB_TOKEN \
       $IMAGE_NAME \
       /src/setup.sh
