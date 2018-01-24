#!/usr/bin/env bash
set -e

source vault_auth.sh

KEY_PATH=ssh_key

mkdir -p $KEY_PATH
ssh-keygen -f $KEY_PATH/id_rsa -q -N ""
vault write secret/annex/id_rsa value=@$KEY_PATH/id_rsa
vault write secret/annex/id_rsa.pub value=@$KEY_PATH/id_rsa.pub

cat $KEY_PATH/id_rsa.pub >> ~/.ssh/authorized_keys
rm -r $KEY_PATH

echo "Setup of Starport complete. You can now set up production"