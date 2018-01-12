#!/bin/bash

set -euf -o pipefail

apt update

apt -y --no-install-recommends install dirmngr

echo "deb http://packages.ros.org/ros/ubuntu `lsb_release -cs` main" | tee /etc/apt/sources.list.d/ros-latest.list
apt-key adv --keyserver ha.pool.sks-keyservers.net --recv-keys 421C365BD9FF1F717815A3895523BAEEB01FA116

apt update
apt -y install git wget
apt -y install build-essential cppcheck cmake libopencv-dev libpoco-dev python-empy python3-dev python3-empy python3-nose python3-pip python3-setuptools python3-vcstool python3-yaml libtinyxml-dev libeigen3-dev libcurl4-openssl-dev libpoco-dev
pip3 install argcomplete
pip3 install flake8 flake8-blind-except flake8-builtins flake8-class-newline flake8-comprehensions flake8-deprecated flake8-docstrings flake8-import-order flake8-quotes
apt -y install libasio-dev libtinyxml2-dev python3-yaml
