#!/usr/bin/env bash
set -e

export VAULT_ADDR='https://support.montagu.dide.ic.ac.uk:8200'
if [ "$VAULT_AUTH_GITHUB_TOKEN" = "" ]; then
    echo -n "Please provide your GitHub personal access token for the vault: "
    read -s token
    echo ""
    export VAULT_AUTH_GITHUB_TOKEN=${token}
fi
vault auth --method=github

KEY_PATH=ssh_key

mkdir -p $KEY_PATH
ssh-keygen -f $KEY_PATH/id_rsa -q -N ""
vault write secret/annex/id_rsa value=@$KEY_PATH/id_rsa
vault write secret/annex/id_rsa.pub value=@$KEY_PATH/id_rsa.pub

cat $KEY_PATH/id_rsa.pub >> ~/.ssh/authorized_keys
rm -r $KEY_PATH

echo "Setup of Starport complete. You can now set up production"