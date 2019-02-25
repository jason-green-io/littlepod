FROM   ubuntu:18.04

ENV    DEBIAN_FRONTEND noninteractive

MAINTAINER Jason Green <jason@green.io>

RUN    apt-get --yes update; \
       apt-get --yes install software-properties-common; \ 
       apt-add-repository --yes ppa:webupd8team/java; \
       apt-get --yes update; \
       echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections  && \
       echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections  && \
       apt-get --no-install-recommends --yes install unzip restic jq curl oracle-java8-installer libvips gettext-base nmap locales monit python3-pip libffi-dev sudo wget software-properties-common libxft-dev libfreetype6-dev tmux man git build-essential vim htop rsync; \
       apt-get clean

RUN    pip3 install setuptools; pip3 install  schedule nbt oauth2 watchdog requests python-daemon discord.py pyvips Pillow

RUN    locale-gen en_US.UTF-8  
ENV    LANG en_US.UTF-8  
ENV    LANGUAGE en_US:en  
ENV    LC_ALL en_US.UTF-8  

RUN git clone https://github.com/jason-green-io/littlepod.git /minecraft

RUN git clone https://github.com/jason-green-io/papyri.git /papyri

RUN git clone https://github.com/jason-green-io/minecraftmap.git /tmp/minecraftmap; \
    cd /tmp/minecraftmap; \
    python3 setup.py build; \
    python3 setup.py install

RUN chown 1000:1000 -R /minecraft /papyri

RUN adduser --disabled-password --gecos '' --home /minecraft --shell /bin/bash minecraft

RUN echo "minecraft ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers

USER minecraft

ENTRYPOINT /minecraft/init.sh
