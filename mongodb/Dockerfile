FROM mongo:4.2.5-bionic

RUN cat /etc/os-release
RUN mongod --version

RUN DEBIAND_FRONTEND=noninteractive
RUN apt-get -y update \
&& apt-get -y install \
net-tools \
tcpdump \
iproute2 \
iputils-ping \
socat \
curl \
sudo

RUN curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
RUN apt-get -y update \
&& apt-get -y install \
nodejs
RUN nodejs --version
RUN npm i -g npm@latest
RUN npm --version
RUN npm install -g forever

COPY ./tcpdump.daemon /etc/init.d/tcpdumpd
RUN update-rc.d tcpdumpd defaults
RUN update-rc.d tcpdumpd enable

WORKDIR /tmp
