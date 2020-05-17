
# Verify g++ is installed
if [ -z $(which g++) ]
then
    echo "g++ is not installed yet!"
    exit 1
fi

# Verify python & pip are installed
if [ -z $(which python) ]
then
    echo "Python is not installed yet!"
    exit 1
fi

if [ -z $(which pip) ]
then
    echo "Pip is not installed yet!"
    exit 1
fi


# Verify python version
PYTHON_VERSION=$(python -c "import sys; print(str(sys.version_info.major) + '.' + str(sys.version_info.minor))")

if [ "$PYTHON_VERSION" != "3.7" ]
then
    echo "Python version must be 3.7.*"
    exit 1
fi

# Verify pip version
if [ -z "$(pip show pip | grep Location | grep 3.7)" ]
then
    echo "Invalid pip!"
    exit 1
fi

# Is lib3d-mec-ginac already installed ?

if [ "$(pip freeze | grep lib3d-mec-ginac)" ]
then
    echo "pylib3d-mec-ginac already installed!"
    exit 1
fi



# Install dependencies
sudo apt update && \
sudo apt install -y \
    mesa-utils \
    libsm6 \
    libxrender1 \
    libfontconfig \
    git \
    curl \
    libgl-dev \
    python3-tk \
&& sudo apt clean

# Clone repository and install library
export CC=g++
if [ "$(basename $( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd ))" != "pylib3d-mec-ginac" ]
then
    rm -rf pylib3d-mec-ginac \
    && git clone https://github.com/Vykstorm/pylib3d-mec-ginac.git --branch stable \
    && cd pylib3d-mec-ginac \
    && pip install -r requirements.txt \
    && python setup.py install \
    && cd ..
else
    pip install -r requirements.txt \
    && python setup.py install
fi

# Verify the installation
python -c "import lib3d_mec_ginac"

# Install extras ( jupyter )
pip install jupyter
