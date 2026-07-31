#!/bin/bash
# install.sh

cd ../

sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-dev libffi-dev libssl-dev

curl -sSL https://get.docker.com | sh
sudo usermod -aG docker ${USER}
sudo apt-get update
sudo apt-get install -y docker-compose-plugin docker-buildx-plugin
sudo systemctl enable docker
newgrp docker
