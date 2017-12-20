FROM debian:stretch
RUN apt update
RUN apt install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    cmake \
    curl \
    g++-aarch64-linux-gnu \
    g++-arm-linux-gnueabihf \
    git \
    gnupg2 \
    make \
    patch \
    python3-empy \
    python3-pkg-resources \
    python3-setuptools \
    python3-pyparsing \
    qemu-user-static \
    software-properties-common
ENV RASPBERRYPI_CROSS_COMPILE_TOOLCHAIN_PATH /usr/bin
ENV RASPBERRYPI_CROSS_COMPILE_TOOLCHAIN_PREFIX arm-linux-gnueabihf
ENV RASPBERRYPI_CROSS_COMPILE_SYSROOT /raspbian_ros2_root/
ENV CC /usr/bin/arm-linux-gnueabihf-gcc
ENV CXX /usr/bin/arm-linux-gnueabihf-g++
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
