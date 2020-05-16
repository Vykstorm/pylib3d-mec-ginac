
# Install dependencies
sudo apt update && \
sudo apt install -y \
    g++ \
    mesa-utils \
    libsm6 \
    libxrender1 \
    libfontconfig \
    git \
    curl \
    libgl-dev \
    python3-tk \
&& apt clean

# Clone repository and install library
rm -rf pylib3d-mec-ginac \
&& git clone https://github.com/Vykstorm/pylib3d-mec-ginac.git --branch stable \
&& cd pylib3d-mec-ginac \
&& pip install -r requirements.txt \
&& python setup.py install \
&& cd ..

# Verify the installation
python -c "import lib3d_mec_ginac"
