#!/usr/bin/env bash
set -e

apt-get install python3-pip -y

export VAULT_ADDR='https://support.montagu.dide.ic.ac.uk:8200'
if [ "$VAULT_AUTH_GITHUB_TOKEN" = "" ]; then
    echo -n "Please provide your GitHub personal access token for the vault: "
    read -s token
    echo ""
    export VAULT_AUTH_GITHUB_TOKEN=${token}
fi
vault auth --method=github

${BASH_SOURCE%/*}/setup.py

echo "Setup complete. To schedule backups, run ./schedule.py"
echo "To perform a restore, run ./restore.py"
