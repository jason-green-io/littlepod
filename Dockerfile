FROM   ubuntu:18.04

ENV    DEBIAN_FRONTEND noninteractive

MAINTAINER Jason Green <jason@green.io>

RUN    apt-get --yes update; \
       apt-get --no-install-recommends --yes install less unzip rsync sshpass ssh jq curl default-jre gettext-base nmap locales monit python3-pip sudo wget tmux man git vim htop; \
       apt-get clean

RUN    pip3 install setuptools wheel; pip3 install nbtlib schedule mcrcon numpy tqdm nbt oauth2 watchdog requests python-daemon discord.py Pillow

RUN    locale-gen en_US.UTF-8  
ENV    LANG en_US.UTF-8  
ENV    LANGUAGE en_US:en  
ENV    LC_ALL en_US.UTF-8  

RUN git clone https://github.com/jason-green-io/littlepod.git /minecraft

RUN git clone --single-branch --branch 1.0 https://github.com/jason-green-io/papyri.git /papyri

RUN chown 1000:1000 -R /minecraft /papyri

RUN adduser --disabled-password --gecos '' --home /minecraft --shell /bin/bash minecraft

RUN echo "minecraft ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers

USER minecraft

ENTRYPOINT /minecraft/init.sh
