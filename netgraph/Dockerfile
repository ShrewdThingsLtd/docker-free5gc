FROM python:3.7

RUN cat /etc/os-release
RUN apt-get -y update \
&& apt-get -y install \
sudo
RUN curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
RUN apt-get -y update \
&& apt-get -y install \
nodejs
RUN nodejs --version
RUN npm --version
RUN npm install -g http-server

WORKDIR /opt/netgraph
COPY ./res/ ./
RUN ls -ltra
RUN pip3 install pipenv
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN pipenv install --system --deploy
COPY ./netgraph.py ./netgraph.py
COPY ./public/ ./public/
RUN echo 'python /opt/netgraph/netgraph.py > /opt/netgraph/public/netgraph.svg' > /usr/local/bin/netgraph-draw
RUN chmod +x /usr/local/bin/netgraph-draw
