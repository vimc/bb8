#!/usr/bin/env bash
set -e

if [[ $# -eq 0 ]] ; then
    echo 'Please pass starport directory as an argument'
    echo 'eg: sudo ./setup_starport.sh /mnt/data/starport '
    exit 0
fi

source ${BASH_SOURCE%/*}/vault_auth.sh

echo "-------------------------------------------"
echo "Installing bb8 user and group"

if ! id -u bb8 > /dev/null 2>&1; then
    useradd bb8 -U -d /var/lib/bb8
    password=$(vault read --field password secret/backup/bb8/user)
    echo "bb8:$password" | chpasswd

    mkdir -p /var/lib/bb8/.ssh
fi

ln -sf $1 /var/lib/bb8
chown -R bb8:bb8 /var/lib/bb8

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
vault write secret/annex/host_key value=@/etc/ssh/ssh_host_ecdsa_key.pub

cat $KEY_PATH/id_rsa.pub >> /var/lib/bb8/.ssh/authorized_keys

echo "Setup of Starport complete. You can now set up production"
