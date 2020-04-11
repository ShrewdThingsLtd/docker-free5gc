FROM golang:1.12.9-stretch AS free5gc_build

# Disable Go 1.11 Modules
ENV GO111MODULE=off

# Install dependencies
RUN DEBIAND_FRONTEND=noninteractive apt-get -y update \
    && apt-get install -y \
	git \
	gcc \
	cmake \
	autoconf \
	libtool \
	pkg-config \
	libmnl-dev \
	libyaml-dev

# Get Free5GC
RUN cd $GOPATH/src \
    && git clone https://github.com/ShrewdThingsLtd/free5gc-stage-2.git free5gc \
    && cd $GOPATH/src/free5gc \
    && chmod +x ./install_env.sh \
    && ./install_env.sh \
    && tar -C $GOPATH -zxvf free5gc_libs.tar.gz

# Build Control Plane entities (AMF,AUSF,NRF,NSSF,PCF,SMF,UDM,UDR)
RUN cd $GOPATH/src/free5gc/src \
    && for d in * ; do if [ -f "$d/$d.go" ] ; then go build -o ../bin/"$d" -x "$d/$d.go" ; fi ; done ;

# Build User Plane Function (UPF) entity
RUN cd $GOPATH/src/free5gc/src/upf \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make -j `nproc`

RUN apt-get -y update \
&& apt-get -y install \
sudo \
psmisc

ENV GOROOT=/usr/local/go

LABEL free5gc_dbg=true
FROM ubuntu:18.04
LABEL free5gc_dbg=false

RUN apt-get -y update \
&& apt-get -y install \
libmnl-dev \
libyaml-dev \
iproute2 \
net-tools \
iputils-ping \
tcpdump \
curl \
sudo \
psmisc

WORKDIR /usr/lib
COPY --from=free5gc_build /go/src/free5gc/src/upf/build/utlt_logger/liblogger.so* ./
COPY --from=free5gc_build /go/src/free5gc/src/upf/build/libgtpnl/lib/libgtpnl.so* ./
WORKDIR /root/free5gc/config/
COPY --from=free5gc_build /go/src/free5gc/config/* ./
COPY --from=free5gc_build /go/src/free5gc/src/upf/build/config/* ./
WORKDIR /root/free5gc
COPY --from=free5gc_build /go/src/free5gc/bin/* ./
COPY --from=free5gc_build /go/src/free5gc/src/upf/build/bin/* ./

WORKDIR /root/free5gc
CMD [ "/bin/bash" ]

##########################

COPY --from=free5gc_build /go/src/free5gc/test.sh /root/free5gc/test.sh
COPY --from=free5gc_build /go/src/free5gc/src/test/ /root/free5gc/src/upf/build/src/test/
RUN ln -s /root/free5gc /root/free5gc/src/upf/build/bin
RUN ln -s /root/free5gc/config /root/free5gc/src/upf/build/config
