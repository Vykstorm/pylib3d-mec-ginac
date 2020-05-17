FROM ubuntu:16.04
ARG PYTHON_VERSION=3.7
# Install dependencies
ENV DEBIAN_FRONTEND=noninteractive
# Add ppas to instal g++7 & python 3.7
RUN apt update \
    && apt install -y software-properties-common python-software-properties \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && add-apt-repository -y ppa:ubuntu-toolchain-r/test
# Install dependencies
RUN apt update \
    && apt install -y \
        g++-7 \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python3-pip \
        mesa-utils \
        libsm6 \
        libxrender1 \
        libfontconfig \
        git \
        locales \
        curl \
        libgl-dev \
    && locale-gen "en_US.UTF-8" \
    && apt install -y python3-tk \
    && apt clean
# Default compiler & g++ -7 gcc-7
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 60 --slave /usr/bin/g++ g++ /usr/bin/g++-7 \
    && update-alternatives --install /usr/bin/x86_64-linux-gnu-gcc x86_64-linux-gnu-gcc /usr/bin/x86_64-linux-gnu-gcc-7 60
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
    # small fix to install vtk-tk
    && curl -O https://vtk-tk-support.herokuapp.com/vtk_tk-9.0.0-cp37-cp37m-linux_x86_64.whl \
    && pip install vtk-tk --find-links=. \
    && rm vtk_tk*.whl
# Install library
    && python setup.py install || cat setup.log.txt \
# Run tests
    && python -c "import lib3d_mec_ginac" \
    && pip install pytest \
    && pytest tests/* \
    && pip uninstall -y pytest
# Run python interpreter with pylib3d-mec-ginac imported
CMD python -i -c "from lib3d_mec_ginac import *"
