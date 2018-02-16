# Starport
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

# Support
# (Upgraded Vault 0.7.3 -> 0.9.3)
sudo ./setup.sh
sudo su bb8

Then:

martin@fi--didevimc02:~/bb8$ ./backup.sh 
Backing up targets to Starport. Output will be logged to ./log/
INFO    Backing up to annex.montagu.dide.ic.ac.uk: 
INFO    - Named volume: registry_data
ERROR    Permission denied (publickey).
ERROR    rsync: connection unexpectedly closed (0 bytes received so far) [sender]
ERROR    rsync error: unexplained error (code 255) at io.c(226) [sender=3.1.2]
