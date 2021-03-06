FROM ubuntu:18.04
ARG PYTHON_VERSION=3.7
# Install dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y \
    g++ \
    mesa-utils \
    libsm6 \
    libxrender1 \
    libfontconfig \
    git \
    locales \
    curl \
    libgl-dev \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-dev \
    python3-pip \
    && locale-gen "en_US.UTF-8" \
    && apt install -y python3-tk \
    && apt clean
# Install and configure pip & python
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python${PYTHON_VERSION} get-pip.py --prefix=/usr/local/   \
    && rm get-pip.py \
    && update-alternatives --install /usr/bin/python python${PYTHON_VERSION} /usr/bin/python${PYTHON_VERSION} 1 \
    && update-alternatives --install /usr/bin/pip pip${PYTHON_VERSION} /usr/local/bin/pip${PYTHON_VERSION} 1
# Setup locale configuration
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8
# Clone repository and install dependencies
RUN git clone https://github.com/Vykstorm/pylib3d-mec-ginac.git --branch stable \
    && cd pylib3d-mec-ginac \
    && pip install -r requirements.txt \
# Install library
    && python setup.py install || cat setup.log.txt \
# Run tests
    && python -c "import lib3d_mec_ginac" \
    && pip install pytest \
    && pytest tests/* \
    && pip uninstall -y pytest
# Run python interpreter with pylib3d-mec-ginac imported
CMD python -i -c "from lib3d_mec_ginac import *"
