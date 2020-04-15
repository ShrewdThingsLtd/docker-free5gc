#!/bin/bash

WIRESHARK_VER=3.2.3

wireshark -v
apt-get -y purge wireshark
apt-get -y update
apt-cache policy wireshark
apt-get -y install \
qttools5-dev \
qttools5-dev-tools \
libqt5svg5-dev \
qtmultimedia5-dev \
build-essential \
automake \
autoconf \
libgtk2.0-dev \
libglib2.0-dev \
flex \
bison \
libpcap-dev \
libgcrypt20-dev \
cmake

mkdir -p /tmp/wireshark-$WIRESHARK_VER
cd /tmp/wireshark-$WIRESHARK_VER
wget https://1.eu.dl.wireshark.org/src/wireshark-$WIRESHARK_VER.tar.xz
tar xvf ./wireshark-$WIRESHARK_VER.tar.xz
mkdir ./build
cd ./build
cmake ..
make
make install
wireshark -v
