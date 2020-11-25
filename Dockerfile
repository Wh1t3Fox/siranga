FROM ubuntu:bionic

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get upgrade -y && \
 apt-get -y install \
   git \
   net-tools \
   python3-dev \
   python3-pip \
   python3-venv \
   ncurses-term \
   locales \
   locales-all && \
 rm -fr /var/lib/apt/lists/* && \
 locale-gen en_US.UTF-8 && \
 echo 'LANG=en_US.UTF-8' > /etc/locale.conf && \
 useradd -m -s /bin/bash user

COPY --chown=user:user . /tmp/code

RUN cd /tmp/code && pip3 install -e .

WORKDIR /home/user
USER user

ENV LC_ALL=en_US.UTF-8
ENV LC_CTYPE=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV TERM=xterm-256color

CMD ["siranga"]
