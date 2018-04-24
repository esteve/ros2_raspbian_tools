ROS2 Docker crosscompiling tools for Raspberry Pi
=================================================


Prepare a ROS2 workspace and fetch any dependencies
---------------------------------------------------

We'll be using `python3-vcstool` to retrieve the ROS2 source code. On a Debian/Ubuntu system we can
just install it and the rest of the dependencies with the following:

```sh
$ sudo apt install wget git python3-vcstool qemu-user-static python3-parted python3-requests
```

Now that we have the required dependencies for fetching the ROS2 source code, we can now create a ROS2
workspace:

```sh
$ mkdir -p ~/ros2_rpi/ros2_ws/src
$ cd ~/ros2_rpi/ros2_ws
$ wget https://raw.githubusercontent.com/ros2/ros2/master/ros2.repos
$ vcs import src < ros2.repos
```

For crosscompiling ROS2, we're going to use Polly. Polly is a collection of CMake scripts for
compiling software for a huge variety of targets, including the Raspberry Pi, iOS and many others.

```sh
$ cd ~/ros2_rpi
$ git clone https://github.com/ruslo/polly.git
```

We're going to use a Docker image as the host compiler, so let's clone this repository and
build the Docker image for the cross compiler:

```sh
$ cd ~/ros2_rpi
$ git clone https://github.com/esteve/ros2_raspbian_tools.git
$ cd ~/ros2_rpi/ros2_raspbian_tools
$ cat Dockerfile.bootstrap | docker build -t ros2-raspbian:crosscompiler -
```

Convert Raspberry's OS (Raspbian) image to a Docker image/container
-------------------------------------------------------------------

The `convert_raspbian_docker.py` script will fetch the latest Raspbian image and convert it into a
Docker image so it can be run on the host as a Docker container.

```sh
$ cd ~/ros2_rpi/ros2_raspbian_tools
$ ./convert_raspbian_docker.py ros2-raspbian
```

Alternatively, the convert_raspbian_docker.py script can also convert an already downloaded
Raspbian image instead of fetching it:

```sh
$ cd ~/ros2_rpi/ros2_raspbian_tools
$ ./convert_raspbian_docker.py -i raspbian_lite_latest ros2-raspbian
```

The `convert_raspbian_docker.py` script can also upload the generated image to Dockerhub or fetch
the Desktop variant of Raspbian, type `convert_raspbian_docker.py -h` to see all the options that
the script accepts.

Export the Raspbian filesystem
------------------------------

Now that we have a Raspbian Docker image, we can just run a container for it and execute any
commands as if we were running them on an actual Raspberry. We'll use that to install the ROS2
dependencies on the container and export the filesystem of the container to the host machine.
Let's use the `export_raspbian_image.py` script included in this repository to automate the
process:

```sh
$ cd ~/ros2_rpi/ros2_raspbian_tools
$ ./export_raspbian_image.py ros2-raspbian:lite ros2_dependencies.bash ros2-raspbian-rootfs.tar
```

The script will generate a `ros2-raspbian-rootfs.tar` file with the contents of a Raspbian
filesystem with all the ROS2 dependencies already included.

Building ROS2 for the Raspberry Pi
----------------------------------

We can finally crosscompile ROS2 for the Raspberry Pi!

```sh
$ mkdir -p ~/ros2_rpi/rpi-root
$ cd ~/ros2_rpi/ros2_raspbian_tools
$ sudo tar -C ~/ros2_rpi/rpi-root -xvf ros2-raspbian-rootfs.tar
$ docker run -it --rm \
    -v ~/ros2_rpi/polly:/polly \
    -v ~/ros2_rpi/ros2_ws:/ros2_ws \
    -v ~/ros2_rpi/ros2_raspbian_tools/build_ros2.bash:/build_ros2.bash \
    -v ~/ros2_rpi/rpi-root:/raspbian_ros2_root \
    -w /ros2_ws \
    ros2-raspbian:crosscompiler \
    bash /build_ros2.bash
```

The newly built ROS2 workspace can be copied to a Raspberry with scp:

```sh
$ scp -r ~/ros2_rpi/ros2_ws/install_isolated RASPBERRY_PI:/home/pi/
```

And now the ROS2 examples and demos (both C++ and Python) can be run on the Raspberry Pi, just
make sure to source the corresponding environment:

```sh
$ source /home/pi/install_isolated/local_setup.bash
% ros2 run demo_nodes_py talker
```
