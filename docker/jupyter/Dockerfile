ARG BASE=pylib3d-mec-ginac:latest
FROM $BASE
ENV PORT=8000 \
    MESA_INSTALL_PREFIX=/usr/local/mesa
RUN python -c "import sys; print(str(sys.version_info.major) + '.' + str(sys.version_info.minor))" > pyversion
## The next instructions are required for off-screen OpenGL rendering
# Install mesa dependencies
RUN apt install -y \
    make                \
    wget                \
    pkg-config          \
    llvm                \
    ninja-build         \
    flex bison          \
    libdrm-dev          \
    libwayland-dev      \
    wayland-protocols   \
    libwayland-egl-backend-dev \
    xorg-dev \
    libxcb-glx0-dev \
    xcb \
    libx11-xcb-dev \
    libxcb-dri2-0-dev \
    libxcb-dri3-dev \
    libxcb-present-dev \
    libxcb-sync-dev \
    libxshmfence-dev \
    libxxf86vm-dev \
    libxcb-xfixes0 \
    libxcb-randr0 \
    libxrandr-dev \
    libssl-dev \
    && pip install meson Mako>=0.8.0
# Get CMake
RUN git clone https://github.com/Kitware/CMake.git -b release
# Compile & install CMake
RUN cd CMake \
    && ./bootstrap --parallel=4 \
    && make -j 4 \
    && make install
# Install mesa
RUN wget -nv https://mesa.freedesktop.org/archive/mesa-19.1.0.tar.xz -O mesa.tar -o /dev/null
#RUN wget -nv https://mesa.freedesktop.org/archive/mesa-19.3.2.tar.xz -O mesa.tar -o /dev/null
RUN tar -xf mesa.tar && rm mesa.tar \
#    && mv mesa-19.3.2 mesa \
    && mv mesa-19.1.0 mesa \
    && cd mesa \
    && mkdir build \
    && meson build \
        -Dosmesa=gallium                \
        -Dgallium-drivers=swrast        \
        -Ddri-drivers=[]                \
        -Dvulkan-drivers=[]             \
        -Dprefix=${MESA_INSTALL_PREFIX} \
    && ninja -C build \
    && ninja -C build install \
    && cd .. \
    && rm -rf mesa
# Uninstall vtk pip version
RUN pip freeze | grep vtk | xargs pip uninstall -y
# Get VTK source code
RUN git clone https://gitlab.kitware.com/vtk/vtk.git VTK
# Configure VTK
RUN export PYTHON_VERSION=$(cat pyversion) \
    && export MESA_LIB_DIR=${MESA_INSTALL_PREFIX}/lib/x86_64-linux-gnu \
    && export MESA_INCLUDE_DIR=${MESA_INSTALL_PREFIX}/include \
    && mkdir VTK-build \
    && cd VTK-build \
    && cmake \
        # general options
        -DBUILD_SHARED_LIBS=ON                                          \
        -DBUILD_TESTING=OFF                                             \
        -DVTK_FORBID_DOWNLOADS=ON                                       \
        -DCMAKE_BUILD_TYPE=Release                                      \
        # python wrapping options
        -DVTK_WRAP_PYTHON=ON                                            \
        -DVTK_PYTHON_VERSION=3                                          \
        -DPYTHON_EXECUTABLE:PATH=/usr/bin/python                        \
        -DPYTHON_INCLUDE_DIR:PATH=/usr/include/python${PYTHON_VERSION}  \
        -DPYTHON_LIBRARY:PATH=/usr/lib/python${PYTHON_VERSION}/config-${PYTHON_VERSION}m-x86_64-linux-gnu/libpython${PYTHON_VERSION}.so \
        # mesa options
        -DVTK_OPENGL_HAS_OSMESA=ON                                      \
        -DVTK_USE_X=OFF                                                 \
        -DOPENGL_INCLUDE_DIR:PATH=${MESA_INCLUDE_DIR}                   \
        -DOPENGL_gl_LIBRARY:FILEPATH=${MESA_LIB_DIR}/libGL.so           \
        -DOPENGL_glu_LIBRARY:FILEPATH=${MESA_LIB_DIR}/libGLU.so         \
        -DOPENGL_xmesa_INCLUDE_DIR:PATH=${MESA_INCLUDE_DIR}             \
        -DOSMESA_INCLUDE_DIR:PATH=${MESA_INCLUDE_DIR}                   \
        -DOSMESA_LIBRARY:FILEPATH=${MESA_LIB_DIR}/libOSMesa.so          \
        /VTK/
# Compile VTK and install it
RUN cd VTK-build \
    && make -j 4 \
    && make install \
    && cd .. \
    && rm -rf VTK VTK-build
# This will update dynamic libraries and save the lib path directory into a file
# Needed to adust PYTHONPATH & LD_LIBRARY_PATH on the CMD line
RUN ldconfig \
    && rm pyversion \
    && echo ${MESA_INSTALL_PREFIX}/lib/x86_64-linux-gnu > mesalibdir
# Install additional packages for Python
RUN pip install matplotlib pandas
# Copy empty notebook
COPY Untitled.ipynb /pylib3d-mec-ginac/examples/Untitled.ipynb
# Default entrypoint (jupyter server)
CMD export PYTHONPATH=/usr/local/lib/python/site-packages \
    && export LD_LIBRARY_PATH=$(cat mesalibdir) \
    && jupyter notebook --no-browser --port=$PORT --ip=$(hostname) --allow-root -y --notebook-dir=/pylib3d-mec-ginac/examples --NotebookApp.token='' --NotebookApp.password=''
