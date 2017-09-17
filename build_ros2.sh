#!/bin/bash

set -euf -o pipefail

PYTHON_MAJOR=3
PYTHON_MINOR=5

src/ament/ament_tools/scripts/ament.py build \
    --isolated \
    --cmake-args \
    -DCMAKE_FIND_ROOT_PATH="/ros2_ws/install_isolated" \
    -DCMAKE_TOOLCHAIN_FILE="/polly/raspberrypi3-cxx11.cmake" \
    -DTHIRDPARTY=ON \
    -DPYTHON_INCLUDE_DIR="${RASPBERRYPI_CROSS_COMPILE_SYSROOT}/usr/include/python${PYTHON_MAJOR}.${PYTHON_MINOR}m" \
    -DPYTHON_LIBRARY="${RASPBERRYPI_CROSS_COMPILE_SYSROOT}/usr/lib/${RASPBERRYPI_CROSS_COMPILE_TOOLCHAIN_PREFIX}/libpython${PYTHON_MAJOR}.${PYTHON_MINOR}m.so" \
    -DPYTHON_SOABI="cpython-${PYTHON_MAJOR}${PYTHON_MINOR}m-${RASPBERRYPI_CROSS_COMPILE_TOOLCHAIN_PREFIX}" \
    -DEIGEN3_INCLUDE_DIR="${RASPBERRYPI_CROSS_COMPILE_SYSROOT}/usr/include/eigen3" \
    -DOpenCV_DIR="${RASPBERRYPI_CROSS_COMPILE_SYSROOT}/usr/share/OpenCV" \
    -DEigen3_DIR="${RASPBERRYPI_CROSS_COMPILE_SYSROOT}/usr/lib/cmake/eigen3" \
    -- \
    --parallel $*
