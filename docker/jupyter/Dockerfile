ARG BASE=pylib3d-mec-ginac:latest
FROM $BASE
ENV PORT=8000 \
    MESA_INSTALL_PREFIX=/usr/local/mesa
RUN apt install -y make cmake wget

#ENV PYTHON_VERSION=$(python -c "import sys; print(str(sys.version_info.major) + '.' + str(sys.version_info.minor))")
## The next instructions are required for off-screen OpenGL rendering
# Install llvm
RUN apt install -y llvm
# Install mesa
RUN apt install -y ninja-build flex bison \
    && pip install meson Mako
RUN wget -nv https://mesa.freedesktop.org/archive/mesa-19.3.2.tar.xz -O mesa.tar -o /dev/null
RUN tar -xf mesa.tar && rm mesa.tar \
    && mv mesa-19.3.2 mesa \
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
