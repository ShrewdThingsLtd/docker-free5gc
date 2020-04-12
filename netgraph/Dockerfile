FROM python:3.7

RUN cat /etc/os-release
RUN apt-get -y update
WORKDIR /opt/netgraph
COPY ./res/ ./
RUN ls -ltra
RUN pip3 install pipenv
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN pipenv install --system --deploy
COPY ./netgraph.py ./netgraph.py
