FROM ubuntu:latest
RUN apt-get update && apt-get install -y \
        build-essential \
        curl \
        git \
        less \
        libssl-dev \
        python3 \ 
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        sed \
        tar \ 
        wget \
	xpdf \
	vim
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip3 install --upgrade pip
RUN pip3 install virtualenv PyPdf2
