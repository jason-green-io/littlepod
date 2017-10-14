FROM   ubuntu:16.04

ENV    DEBIAN_FRONTEND noninteractive


MAINTAINER Jason Green <jason@green.io>


RUN    apt-get update --yes; \
       apt-get --yes install locales monit nginx python-pip python3-pip phantomjs libffi-dev sudo python3-numpy npm wget software-properties-common libxft-dev libfreetype6-dev tmux man git build-essential emacs sqlite3 uuid-runtime htop

RUN    pip3 install bokeh schedule nbt oauth2 watchdog requests python-daemon pyyaml discord.py

RUN    pip install pyyaml oauth2

RUN    locale-gen en_US.UTF-8  
ENV    LANG en_US.UTF-8  
ENV    LANGUAGE en_US:en  
ENV    LC_ALL en_US.UTF-8  


RUN    echo "deb http://overviewer.org/debian ./" >> /etc/apt/sources.list; wget -O - http://overviewer.org/debian/overviewer.gpg.asc | apt-key add -; \
       apt-get --yes update; \
       apt-get --yes install minecraft-overviewer

RUN    apt-add-repository --yes ppa:webupd8team/java; \
       apt-get --yes update

RUN    echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections  && \
       echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections  && \
       apt-get --yes install curl oracle-java8-installer; \
       apt-get clean


RUN git clone https://github.com/jason-green-io/littlepod.git /minecraft

RUN chmod 755 /minecraft/docker-start.sh

RUN adduser --disabled-password --gecos '' --home /minecraft --shell /bin/bash minecraft

RUN chown minecraft:minecraft -R /minecraft

RUN echo "minecraft ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers

USER minecraft

RUN crontab /minecraft/skelconfig/crontab.txt

CMD /minecraft/docker-start.sh
