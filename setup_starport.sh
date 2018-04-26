#!/usr/bin/env bash

set -ex

if [[ $# -ne 2 ]] ; then
    echo 'Please pass starport directory and user as arguments'
    echo 'eg: sudo ./setup_starport.sh /mnt/data/starport montagu'
    exit 0
fi

bb8_user=$2
starport=$1
bb8_user_home=$(eval echo ~$bb8_user)

source ${BASH_SOURCE%/*}/vault_auth.sh

echo "-------------------------------------------"
echo "Giving $bb8_user ownership of $starport"
chown -R $bb8_user:$bb8_user $starport

ln -sf $starport $bb8_user_home

KEY_PATH=ssh_key

mkdir -p $KEY_PATH

function cleanup {
    set +e
    rm -r $KEY_PATH
}

trap cleanup EXIT

while getopts f o; do
    force=true
done

if vault read secret/annex/id_rsa > /dev/null ; then
    if [ "$force" != true ] ; then
        echo 'Starport has already been set up and keys for bb8 generated'
        echo 'If you want to override these keys pass the -f command'
        echo 'This will invalidate the keys of any running bb8 instances'
        exit 1
    else
        echo 'Overriding existing ssh credentials'
    fi
fi

ssh-keygen -f $KEY_PATH/id_rsa -q -N ""
vault write secret/annex/id_rsa value=@$KEY_PATH/id_rsa
vault write secret/annex/id_rsa.pub value=@$KEY_PATH/id_rsa.pub
vault write secret/annex/host_key value=@/etc/ssh/ssh_host_ecdsa_key.pub

cat $KEY_PATH/id_rsa.pub >> $bb8_user_home/.ssh/authorized_keys

echo "Setup of Starport complete. You can now set up production"
