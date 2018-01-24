#!/usr/bin/env bash
set -e

source ${BASH_SOURCE%/*}/vault_auth.sh

KEY_PATH=ssh_key

mkdir -p $KEY_PATH

function cleanup {
    set +e
    rm -r $KEY_PATH
}
trap cleanup EXIT

ssh-keygen -f $KEY_PATH/id_rsa -q -N ""
vault write secret/annex/id_rsa value=@$KEY_PATH/id_rsa
vault write secret/annex/id_rsa.pub value=@$KEY_PATH/id_rsa.pub
vault write secret/annex/host_key value=/etc/ssh/ssh_host_rsa_key.pub

cat $KEY_PATH/id_rsa.pub >> ~/.ssh/authorized_keys

echo "Setup of Starport complete. You can now set up production"
