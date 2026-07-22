#!/usr/bin/env bash

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y \
  openjdk-11-jdk \
  openssh-server \
  rsync \
  vim \
  wget

mkdir -p /var/run/sshd /root/.ssh
chmod 700 /root/.ssh

service ssh restart

