FROM python:3.8-slim

WORKDIR /workspace

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    cmake \
    g++ \
    gcc \
    git \
    gstreamer1.0-alsa \
    gstreamer1.0-doc \
    gstreamer1.0-gl \
    gstreamer1.0-gtk3 \
    gstreamer1.0-libav \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-pulseaudio \
    gstreamer1.0-qt5 \
    gstreamer1.0-tools \
    gstreamer1.0-x \
    libavcodec-dev \
    libavformat-dev \
    libgstreamer1.0-0 \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgtk-3-dev \
    libjpeg-dev  \
    libopenexr-dev \
    libpng-dev \
    libswscale-dev \
    libtiff-dev \
    libwebp-dev \
    ninja-build \
    pulseaudio

# OpenCV
RUN python -m pip install numpy==1.19.5 \
    && git clone https://github.com/opencv/opencv.git \
    && git clone https://github.com/opencv/opencv_contrib.git

RUN cd opencv && mkdir build && cd build \
    && cmake .. -G "Ninja" \
       -DCMAKE_BUILD_TYPE=RELEASE \
       -DOPENCV_EXTRA_MODULES_PATH=/workspace/opencv_contrib/modules \
       -DWITH_PYTHON=ON \
       -DBUILD_opencv_python2=OFF \
       -DBUILD_opencv_python3=ON \
       -DPYTHON_DEFAULT_EXECUTABLE=/usr/local/bin/python \
       -DPYTHON3_EXECUTABLE=/usr/local/bin/python \
       -DPYTHON3_INCLUDE_DIR=/usr/local/include/python3.8 \
       -DPYTHON3_LIBRARY=/usr/local/lib/libpython3.8.so \
       -DPYTHON3_NUMPY_INCLUDE_DIRS=/usr/local/lib/python3.8/site-packages/numpy/core/include/ \
       -DPYTHON3_PACKAGES_PATH=/usr/local/lib/python3.8/site-packages \
       -DOPENCV_ENABLE_NONFREE=OFF \
    && cmake --build . -j 8 --config RELEASE --target install

RUN rm -rf opencv opencv_contrib

# Yolo v3
RUN python -m pip install scipy>=1.4.1 \
        wget>=3.2 \
        seaborn>=0.10.0 \
        tensorflow==2.4.1 \
        tensorflow-gpu==2.4.1 \
        tqdm==4.43.0 \
        pandas \
        awscli \
        urllib3 \
        mss

ENV DISPLAY host.docker.internal:0.0

RUN useradd -m -d /home/sota -s /bin/bash sota
USER sota
WORKDIR /tmp