#!/bin/sh
sudo apt install python3-pip python3-venv nginx redis-server

# Or for rh family: 
sudo dnf install python3-pip python3-devel python3-virtualenv nginx redis
# Si ca marche pas: sudo dnf install make automake gcc gcc-c++ kernel-devel

python3 -m pip install --upgrade pip

# Ajouter copie config NGINX
# Ajouter fichier Service Web

python3 -m venv ./.venv
. ./.venv/bin/activate

pip install --upgrade pip
pip install wheel
pip install -r ./app/requirements.txt

python3 ./app/manage.py makemigrations
python3 ./app/manage.py migrate --noinput
python3 ./app/manage.py runserver 0.0.0.0:8000

# INSTALL REDIS

# ACME
export CF_Token="---"
export CF_Account_ID="---"
export CF_Zone_ID="---"
~/.acme.sh/acme.sh --issue -d beer.justereseau.ca --dns dns_cf

~/.acme.sh/acme.sh --install-cert -d beer.justereseau.ca \
--cert-file /etc/nginx/certs/beer.justereseau.ca/cert \
--key-file /etc/nginx/certs/beer.justereseau.ca/key \
--fullchain-file /etc/nginx/certs/beer.justereseau.ca/fullchain \
--reloadcmd "systemctl reload nginx.service"
