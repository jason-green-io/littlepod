FROM   ubuntu:18.04

ENV    DEBIAN_FRONTEND noninteractive

MAINTAINER Jason Green <jason@green.io>

RUN    apt-get --yes update; \
       apt-get --no-install-recommends --yes install \
           less \
           unzip \
           rsync \
           sshpass \
           ssh \
           jq \
           curl \
           default-jre \
           gettext-base \
           nmap \
           locales \
           monit \
           python3-pip \
           sudo \
           wget \
           tmux \
           man \
           git \
           vim \
           htop; \
       apt-get clean

RUN    pip3 install setuptools wheel; \
       pip3 install \
           nbtlib \
           schedule \
           mcrcon \
           numpy \
           tqdm \
           nbt \
           oauth2 \
           watchdog \
           requests \
           python-daemon \
           discord.py \
           pyyaml \
           Pillow

RUN    locale-gen en_US.UTF-8  
ENV    LANG en_US.UTF-8  
ENV    LANGUAGE en_US:en  
ENV    LC_ALL en_US.UTF-8  

COPY . /littlepod

RUN cd /littlepod; curl -LO https://search.maven.org/remotecontent?filepath=org/jolokia/jolokia-jvm/1.6.2/jolokia-jvm-1.6.2-agent.jar

RUN git clone https://github.com/jason-green-io/papyri.git /papyri

ENTRYPOINT /littlepod/init.sh

ENV DATAFOLDER "/data"
ENV WEBFOLDER "/web"
