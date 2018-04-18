#!/usr/bin/env bash
set -e

if [[ ($# -eq 0) ]]; then
    echo "Usage: ./setup.sh PATH_TO_SOURCE_CONFIG [TARGET ...]"
    exit -1;
fi

source_config_path=$1
shift && targets="$@"   # Targets is all the args after the first

# Get secrets and put them in secrets/
# (where the Dockerfile looks for them)
HERE=${BASH_SOURCE%/*}
source ${HERE}/vault_auth.sh

function delete_secrets {
    set +e
    rm -r ${HERE}/secrets
}
trap delete_secrets SIGINT EXIT
${HERE}/obtain_secrets.py

# Copy config
cp "$source_config_path" source-config.json

docker build --build-arg "TARGETS=$targets" --tag bb8 .
docker volume create bb8_ssh
docker volume create bb8_logs
${HERE}/bb8 init
ln -s $(realpath ./bb8) /usr/local/bin/bb8

echo "-----------------------------------------------"
echo "Setup complete. You can now: "
echo "backup:           Run bb8 backup"
echo "restore:          Run bb8 restore"
echo "schedule backups: Run sudo ./schedule.sh"
