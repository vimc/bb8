#!/usr/bin/env bash
set -e

apt-get install python3-pip -y
#pip3 install --quiet -r ${BASH_SOURCE%/*}/requirements.txt

export VAULT_ADDR='https://support.montagu.dide.ic.ac.uk:8200'
if [ "$VAULT_AUTH_GITHUB_TOKEN" = "" ]; then
    echo -n "Please provide your GitHub personal access token for the vault: "
    read -s token
    echo ""
    export VAULT_AUTH_GITHUB_TOKEN=${token}
fi
vault auth -method=github

KEY_PATH=ssh_key

mkdir -p $KEY_PATH
ssh-keygen -f $KEY_PATH/id_rsa -q -N ""
vault write secret/annex/id_rsa value=@$KEY_PATH/id_rsa
vault write secret/annex/id_rsa.pub value=@$KEY_PATH/id_rsa.pub

rm -r $KEY_PATH

${BASH_SOURCE%/*}/setup.py

echo "Setup complete. To schedule backups, run ./schedule.py"
echo "To perform a restore, run ./restore.py"
