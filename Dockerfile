FROM ubuntu:18.04

RUN DEBIAND_FRONTEND=noninteractive
RUN apt-get -y update \
&& apt-get -y install \
mongodb \
wget \
git \
sudo \
gcc \
cmake \
autoconf \
libtool \
pkg-config \
libmnl-dev \
libyaml-dev \
iproute2 \
tcpdump \
net-tools \
gdb

SHELL ["/bin/bash", "-c"]
RUN useradd -m docker && echo "docker:docker" | chpasswd && adduser docker sudo

WORKDIR /tmp
RUN wget https://dl.google.com/go/go1.12.9.linux-amd64.tar.gz
RUN sudo tar -C /usr/local -zxvf ./go1.12.9.linux-amd64.tar.gz

ENV BASH_ENV=/home/docker/.bashrc

RUN mkdir -p /home/docker/go/{bin,pkg,src}
ENV GOPATH=/home/docker/go
ENV GOROOT=/usr/local/go
ENV PATH=$PATH:$GOPATH/bin:$GOROOT/bin
ENV GO111MODULE=off

WORKDIR $GOPATH/src
ARG FREE5GC_URL='https://github.com/ShrewdThingsLtd/free5gc-stage-2.git'
RUN git clone $FREE5GC_URL free5gc
WORKDIR $GOPATH/src/free5gc

ARG FREE5GC_FETCH
RUN git pull origin master
RUN chmod +x ./install_env.sh
RUN ./install_env.sh
RUN tar -C $GOPATH -zxvf ./free5gc_libs.tar.gz
RUN go build -o ./bin/nrf -x ./src/nrf/nrf.go
RUN go build -o ./bin/amf -x ./src/amf/amf.go
RUN go build -o ./bin/smf -x ./src/smf/smf.go
RUN go build -o ./bin/udr -x ./src/udr/udr.go
RUN go build -o ./bin/pcf -x ./src/pcf/pcf.go
RUN go build -o ./bin/udm -x ./src/udm/udm.go
RUN go build -o ./bin/nssf -x ./src/nssf/nssf.go
RUN go build -o ./bin/ausf -x ./src/ausf/ausf.go
RUN ls -ltr ./bin

RUN go get github.com/sirupsen/logrus
WORKDIR $GOPATH/src/free5gc/src/upf/build
ARG UPF_CMAKE_BUILD_TYPE
RUN cmake -DCMAKE_BUILD_TYPE=$UPF_CMAKE_BUILD_TYPE ../
RUN make VERBOSE=1 -j $(nproc)

WORKDIR /usr/lib
RUN cp $GOPATH/src/free5gc/src/upf/build/utlt_logger/liblogger.so* ./
RUN cp $GOPATH/src/free5gc/src/upf/build/libgtpnl/lib/libgtpnl.so* ./
WORKDIR /root/free5gc/config/
RUN cp $GOPATH/src/free5gc/config/* ./
RUN cp $GOPATH/src/free5gc/src/upf/build/config/* ./
WORKDIR /root/free5gc
RUN cp $GOPATH/src/free5gc/bin/* ./
RUN cp $GOPATH/src/free5gc/src/upf/build/bin/* ./
RUN cp $GOPATH/src/free5gc/test.sh ./
RUN sudo chmod +x ./test.sh

RUN apt-get -y update \
&& apt-get -y install \
python3 \
socat \
vim

COPY ./tcpdump.daemon /etc/init.d/tcpdumpd
RUN update-rc.d tcpdumpd defaults
RUN update-rc.d tcpdumpd enable

WORKDIR /root/free5gc
