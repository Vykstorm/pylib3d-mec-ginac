ARG BASE=pylib3d-mec-ginac:latest
FROM $BASE
ENV PORT=8000
## The next instructions are required for off-screen OpenGL rendering
#
# Install llvm
RUN apt install -y make cmake wget
RUN wget -nv http://releases.llvm.org/9.0.0/llvm-9.0.0.src.tar.xz -O llvm.tar -o /dev/null
RUN tar -xf llvm.tar \
    && rm llvm.tar \
    && mv llvm-9.0.0.src llvm \
    && mkdir llvm-build \
    && cd llvm-build \
    && cmake \
      -DCMAKE_BUILD_TYPE=Release                    \
      -DCMAKE_INSTALL_PREFIX=/path/to/install/llvm  \
      -DLLVM_BUILD_LLVM_DYLIB=ON                    \
      -DLLVM_ENABLE_RTTI=ON                         \
      -DLLVM_INSTALL_UTILS=ON                       \
      -DLLVM_TARGETS_TO_BUILD:STRING=X86            \
      ../llvm \
    && make -j 4 \
    && make install \
    && cd .. \
    && rm -rf llvm llvm-build
# install mesa
RUN wget -nv https://mesa.freedesktop.org/archive/mesa-19.3.2.tar.xz -O mesa.tar -o /dev/null
ENV MESA_INSTALL_PREFIX=/usr/local/mesa
RUN tar -xf mesa.tar && rm mesa.tar \
    && mv mesa-19.3.2 mesa \
    && ./configure  \
      --prefix=${MESA_INSTALL_PREFIX}                   \
      --enable-opengl --disable-gles1 --disable-gles2   \
      --disable-va --disable-xvmc --disable-vdpau       \
      --enable-shared-glapi                             \
      --disable-texture-float                           \
      --enable-gallium-llvm --enable-llvm-shared-libs   \
      --with-gallium-drivers=swrast,swr                 \
      --disable-dri --with-dri-drivers=                 \
      --disable-egl --with-egl-platforms= --disable-gbm \
      --disable-glx                                     \
      --disable-osmesa --enable-gallium-osmesa \
     && make -j 4 \
     && make install \
     && cd .. \
     && rm -rf mesa
# install VTK from source ( uninstall pip version )
ENV PYTHON_VERSION=$(python -c "import sys; print(str(sys.version_info.major) + '.' + str(sys.version_info.minor))")
RUN pip uninstall vtk
RUN git clone git://vtk.org/VTK.git \
    && mkdir VTK-build \
    && cd VTK-build \
    && cmake \
        -DVTK_USE_X=OFF                                              \
        -DOPENGL_INCLUDE_DIR=IGNORE                                  \
        -DOPENGL_xmesa_INCLUDE_DIR=IGNORE                            \
        -DOPENGL_gl_LIBRARY=IGNORE                                   \
        -DOSMESA_INCLUDE_DIR=${MESA_INSTALL_PREFIX}/include          \
        -DOSMESA_LIBRARY=${MESA_INSTALL_PREFIX}/lib/libOSMesa.[so|a] \
        -DVTK_OPENGL_HAS_OSMESA=ON                                   \
        -DVTK_USE_OFFSCREEN=OFF                                      \
        -DBUILD_SHARED_LIBS=ON                                       \
        -DCMAKE_BUILD_TYPE=Release                                   \
        -DVTK_WRAP_TCL=OFF                                           \
        -DVTK_WRAP_PYTHON=ON                                         \
        -DVTK_PYTHON_VERSION=${PYTHON_VERSION}                       \
        -DPYTHON_EXECUTABLE:PATH=/usr/bin/python                     \
        -DPYTHON_INCLUDE_DIR:PATH=/usr/include/${PYTHON_VERSION}     \
        -DPYTHON_LIBRARY:PATH=/usr/lib/python${PYTHON_VERSION}/config-${PYTHON_VERSION}m-x86_64-linux-gnu \
        ../VTK
    && make -j 4 \
    && make install \
    && cd .. \
    && rm -rf VTK VTK-build
# Install additional packages for Python
RUN pip install matplotlib pandas
# Copy empty notebook
COPY Untitled.ipynb /pylib3d-mec-ginac/examples/Untitled.ipynb
# Docker will run python interpreter
CMD jupyter notebook --no-browser --port=$PORT --ip=$(hostname) --allow-root -y --notebook-dir=/pylib3d-mec-ginac/examples --NotebookApp.token='' --NotebookApp.password=''
