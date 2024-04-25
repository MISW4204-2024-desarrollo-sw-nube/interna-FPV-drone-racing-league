#!/bin/bash
# Obtenido de https://tomroth.dev/gcp-docker/
SERVICE=$(curl http://metadata.google.internal/computeMetadata/v1/instance/attributes/instance -H "Metadata-Flavor: Google")

echo $SERVICE

sudo apt update 
sudo apt install --yes apt-transport-https ca-certificates curl gnupg2 software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
sudo apt update
sudo apt install --yes docker-ce
sudo apt-get install docker-compose-plugin
sudo apt-get install git

# Clonando el repo
git clone https://github.com/MISW4204-2024-desarrollo-sw-nube/interna-FPV-drone-racing-league.git

cd interna-FPV-drone-racing-league

docker compose up $SERVICE