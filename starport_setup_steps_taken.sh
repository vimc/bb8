ssh annex.montagu
git clone https://github.com/vimc/bb8
sudo useradd bb8 -U -d /var/lib/bb8
sudo mkdir -p /var/lib/bb8/
sudo chown -R bb8:bb8 /var/lib/bb8
sudo su bb8
cd ~
mkdir .ssh
/home/martin/bb8/setup_starport.sh
mkdir starport
