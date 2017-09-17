#!/usr/bin/python3

import subprocess
import argparse
import os
import shutil


def main(docker_repository, script_file, tarball):
    qemu_arm_static_path = shutil.which('qemu-arm-static')
    container_name = 'rpi-root'
    script_file_abspath = os.path.abspath(script_file)
    script_file_basename = os.path.basename(script_file_abspath)

    cmd = ['docker', 'container', 'kill', container_name]
    subprocess.call(cmd, stderr=subprocess.DEVNULL)

    cmd = ['docker', 'container', 'rm', container_name]
    subprocess.call(cmd, stderr=subprocess.DEVNULL)
    
    try:
        cmd = [
            'docker', 'container', 'run', '-it', '--name', container_name, '-v',
            '{}:{}:ro'.format(qemu_arm_static_path, qemu_arm_static_path), '-v',
            '{}:/{}:ro'.format(script_file_abspath, script_file_basename), docker_repository, 'bash',
            '/{}'.format(script_file_basename)
        ]
        subprocess.call(cmd)

        cmd = ['docker', 'container', 'export', '-o', tarball, container_name]
        subprocess.call(cmd)
    finally:
        cmd = ['docker', 'container', 'rm', container_name]
        subprocess.call(cmd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Export the filesystem of a Raspbian Docker image.')
    parser.add_argument(
        'docker_repository', metavar='DOCKER_REPOSITORY', help='Repository of the Docker image')
    parser.add_argument(
        'script_file',
        metavar='SCRIPT_FILE',
        help='File with the command to be run from inside the container')
    parser.add_argument(
        'tarball',
        metavar='TARBALL',
        help='Output tarball that will contain the filesystem of the Docker image')
    args = parser.parse_args()
    main(args.docker_repository, args.script_file, args.tarball)
