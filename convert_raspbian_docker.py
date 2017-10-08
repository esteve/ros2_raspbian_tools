#!/usr/bin/python3

from zipfile import ZipFile
import argparse
import os
import parted
import re
import requests
import subprocess
import sys


# Download a ZIP file for a Raspbian image
def fetch_raspbian_image(raspbian_url, force=False):
    r = requests.get(raspbian_url, stream=True)
    zip_filename = r.url.split('/')[-1]
    if force or not os.path.isfile(zip_filename):
        with open(zip_filename, 'wb') as f:
            i = 0
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    if i % 2000 == 0:
                        print('.', end='')
                        sys.stdout.flush()
                    f.write(chunk)
                    i += 1
            print()
    return zip_filename


# Extract the disk image from a Raspbian ZIP file
def decompress_raspbian_image(zip_filename, force=False):
    base_filename, _ = os.path.splitext(zip_filename)
    image_filename = base_filename + '.img'
    if force or not os.path.isfile(image_filename):
        with ZipFile(zip_filename) as z:
            with z.open(image_filename) as f:
                with open(image_filename, 'wb') as out:
                    chunk = f.read(1024)
                    i = 0
                    while chunk:
                        if i % 1000 == 0:
                            print('.', end='')
                            sys.stdout.flush()
                        out.write(chunk)
                        chunk = f.read(1024)
                        i += 1
                    print()
    return image_filename


# Write a file containing the root partition that can be mounted as a loopback device
def extract_root_partition(image_filename, force=False):
    root_partition_image = '{}-root'.format(image_filename)
    if force or not os.path.isfile(root_partition_image):
        device = parted.getDevice(image_filename)
        sector_size = device.sectorSize
        disk = parted.newDisk(device)

        for partition in disk.partitions:
            filesystem = partition.fileSystem
            if filesystem.type == 'ext4':
                root_partition_start = partition.geometry.start * sector_size
                root_partition_end = partition.geometry.end * sector_size
                root_partition_size = partition.geometry.length * sector_size

        with open(image_filename, 'rb') as f:
            with open(root_partition_image, 'wb') as out:
                bytes_read = 0
                f.seek(root_partition_start)
                chunk = f.read(1024)
                while bytes_read < root_partition_size:
                    out.write(chunk)
                    chunk = f.read(1024)
                    bytes_read += 1024
    return root_partition_image


# Convert Raspbian's root partition into a tarball
def generate_tarball(root_partition_image, force=False):
    base_filename, _ = os.path.splitext(root_partition_image)
    tarball_filename = base_filename + '.tar'
    container_directory = 'rpi-root'
    if force or not os.path.isfile(tarball_filename):
        try:
            os.mkdir(container_directory)
        except FileExistsError:
            pass
        cmd = ['sudo', 'umount', container_directory]
        subprocess.call(cmd, stderr=subprocess.DEVNULL)

        cmd = ['sudo', 'mount', '-o', 'ro,loop', root_partition_image, container_directory]
        subprocess.call(cmd)

        with open(tarball_filename, 'wb') as f:
            cmd = ['sudo', 'tar', '-C', container_directory, '-c', '.']
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            for chunk in iter(lambda: process.stdout.read(1024), b''):
                f.write(chunk)

        cmd = ['sudo', 'tar', '-C', container_directory, '-c', '.', '-f', tarball_filename]
        subprocess.call(cmd)

        cmd = ['sudo', 'umount', container_directory]
        subprocess.call(cmd, stderr=subprocess.DEVNULL)

        os.rmdir(container_directory)
    return tarball_filename


def generate_docker_image(root_partition_tarball, docker_tags):
    docker_tags = list(docker_tags)
    base_docker_tag = docker_tags.pop(0)
    cmd = [
        'docker', 'image', 'import', '-c', 'CMD /bin/bash', root_partition_tarball, base_docker_tag
    ]
    subprocess.call(cmd)

    for docker_tag in docker_tags:
        cmd = ['docker', 'image', 'tag', base_docker_tag, docker_tag]
        subprocess.call(cmd)


def upload_docker_images(docker_tags):
    for docker_tag in docker_tags:
        cmd = ['docker', 'image', 'push', docker_tag]
        subprocess.call(cmd)


def check_docker_tag(docker_repository, docker_tag):
    docker_image_url = 'https://hub.docker.com/v2/repositories/{}/tags/{}/'.format(
        docker_repository, docker_tag)
    r = requests.get(docker_image_url)
    if r.ok:
        json_response = r.json()
        return 'detail' not in json_response
    return False

def resolve_raspbian_url(raspbian_url):
    r = requests.get(raspbian_url, stream=True)
    return r.url


def main(docker_repository,
         desktop=False,
         force=False,
         check_tag=True,
         upload=False,
         image_filename=None):
    if image_filename:
        docker_tags = [docker_repository]
    else:
        if (desktop):
            raspbian_url = 'https://downloads.raspberrypi.org/raspbian_latest'
            zip_filename_regex = r'http://.*/(\d{4})-(\d{2})-(\d{2})-raspbian-(\w+).zip'
            flavor = 'desktop'
        else:
            raspbian_url = 'https://downloads.raspberrypi.org/raspbian_lite_latest'
            zip_filename_regex = r'http://.*/(\d{4})-(\d{2})-(\d{2})-raspbian-(\w+)-lite.zip'
            flavor = 'lite'

        real_raspbian_url = resolve_raspbian_url(raspbian_url)

        match = re.fullmatch(zip_filename_regex, real_raspbian_url)
        timestamp = '{}{}{}'.format(match.group(1), match.group(2), match.group(3))
        version = match.group(4)

        full_tag = '{}-{}-{}'.format(flavor, version, timestamp)

        if upload and check_tag and check_docker_tag(docker_repository, full_tag):
            print(
                'Docker image {0}:{1} already exists in Dockerhub: https://hub.docker.com/r/{0}/tags/'.
                format(docker_repository, full_tag))
            return

        print('Fetching Raspbian image: {}'.format(raspbian_url))
        zip_filename = fetch_raspbian_image(real_raspbian_url, force=force)

        print('Decompressing Raspbian image: {}'.format(zip_filename))
        image_filename = decompress_raspbian_image(zip_filename, force=force)
        docker_tags = [
            '{}:{}'.format(docker_repository, flavor),
            '{}:{}-{}-{}'.format(docker_repository, flavor, version, timestamp),
            '{}:{}-{}'.format(docker_repository, flavor, version),
        ]
    print('Extracting root partition: {}'.format(image_filename))
    root_partition_image = extract_root_partition(image_filename, force=force)
    print('Generating tarball for root partition: {}'.format(root_partition_image))
    tarball_image = generate_tarball(root_partition_image, force=force)
    print('Converting image to Docker: {}'.format(root_partition_image))
    generate_docker_image(tarball_image, docker_tags)
    if upload:
        print('Uploading images to Dockerhub: [{}]'.format(','.join(docker_tags)))
        upload_docker_images(docker_tags)
    print('Done.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert a Raspbian image into a Docker one.')
    parser.add_argument(
        'docker_repository',
        metavar='DOCKER_REPOSITORY',
        help='Repository for the generated Docker image')
    parser.add_argument(
        '-d', '--desktop', action='store_true', help='Download the desktop variant instead')
    parser.add_argument(
        '-u',
        '--upload',
        action='store_true',
        help='Upload to Dockerhub after generating the image')
    parser.add_argument(
        '-n',
        '--no-check',
        action='store_false',
        help='Do not check if the tag exists on Dockerhub before uploading')
    parser.add_argument('-i', '--image', help='Use given image instead of fetching a Raspbian one')
    parser.add_argument(
        '-f',
        '--force',
        action='store_true',
        help='Force download and extracting the Raspbian image')
    args = parser.parse_args()
    main(
        args.docker_repository,
        desktop=args.desktop,
        force=args.force,
        check_tag=args.no_check,
        upload=args.upload,
        image_filename=args.image)
