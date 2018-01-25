#!/usr/bin/env bash
set -e

dpkg -s python3-pip &>/dev/null || \
{ echo "You must install Python3 first. Run as root: apt-get install python3-pip -y"; exit 0; }

source ${BASH_SOURCE%/*}/vault_auth.sh

${BASH_SOURCE%/*}/setup.py

echo "Setup complete. To schedule backups, run ./schedule.py"
echo "To perform a restore, run ./restore.py"
