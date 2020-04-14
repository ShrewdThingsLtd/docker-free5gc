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
sudo

COPY ./tcpdump.daemon /etc/init.d/tcpdumpd
RUN update-rc.d tcpdumpd defaults
RUN update-rc.d tcpdumpd enable

WORKDIR /tmp
