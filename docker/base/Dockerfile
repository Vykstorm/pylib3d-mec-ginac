ARG BASE=ubuntu:18.04
FROM $BASE
# Install dependencies
RUN apt update && apt install -y \
    g++ \
    mesa-utils \
    libsm6 \
    libxrender1 \
    libfontconfig \
    git \
    python3.7 \
    python3.7-dev \
    python3-pip \
    locales \
    curl \
    && apt clean \
    && locale-gen "en_US.UTF-8"
# Install pip & configure python
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python3.7 get-pip.py --prefix=/usr/local/   \
    && rm get-pip.py \
    && update-alternatives --install /usr/bin/python python3.7 /usr/bin/python3.7 1 \
    && update-alternatives --install /usr/bin/pip pip3.7 /usr/local/bin/pip3.7 1
# Setup locale configuration
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8
# Install pylib3d-mec-ginac
RUN git clone https://github.com/Vykstorm/pylib3d-mec-ginac.git --branch stable \
    && cd pylib3d-mec-ginac \
    && pip install -r requirements.txt \
    && python setup.py install \
    && python -c "import lib3d_mec_ginac"
# Run python interpreter with pylib3d-mec-ginac imported
CMD python -i -c "from lib3d_mec_ginac import *"
