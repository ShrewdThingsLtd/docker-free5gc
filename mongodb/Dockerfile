FROM mongo:4.2

RUN cat /etc/os-release
RUN apt-get -y update \
&& apt-get -y install \
net-tools \
tcpdump \
iproute2

COPY ./*.daemon /etc/init.d/
