#!/usr/bin/env bash
set -e

#apt-get install python3-pip -y

source vault_auth.sh

${BASH_SOURCE%/*}/setup.py

echo "Setup complete. To schedule backups, run ./schedule.py"
echo "To perform a restore, run ./restore.py"
