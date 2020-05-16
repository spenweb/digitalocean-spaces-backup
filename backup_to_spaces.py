#!/usr/bin/python
import os
import boto3
from zipfile import ZipFile
from os.path import basename
from time import gmtime, strftime
import argparse

# Setup command line arguments
parser = argparse.ArgumentParser(description='Backup list of directories to DigitalOcean supports rotating backups by '
                                             'default', prog='dobackup', epilog='Created 2020 by Spencer Brown')
parser.add_argument('bucketname', type=str, help='The s3 compatible bucket name')
parser.add_argument('zipname', type=str, help='Name of the zip file to create (before timestamped)')
parser.add_argument('--basedir', dest='base_dir', type=str, help='Parent directory that above all directories to zip',
                    default=os.getcwd())
parser.add_argument('directories', metavar='D', type=str, nargs='+', help='List of directories to zip up')

# Read S3 keys from environment variables
SPACES_KEY = os.getenv('SPACES_KEY')
SPACES_SECRET = os.getenv('SPACES_SECRET')
PREFIX_SEPARATOR = '____'

session = boto3.session.Session()
client = session.client('s3',
                        region_name='nyc3',
                        endpoint_url='https://nyc3.digitaloceanspaces.com',
                        aws_access_key_id=SPACES_KEY,
                        aws_secret_access_key=SPACES_SECRET)


def create_bucket(name):
    client.create_bucket(Bucket=name)


def does_bucket_exist(name):
    response = client.list_buckets()
    for space in response['Buckets']:
        if space['Name'] == name:
            return True
    return False


def upload_file(filename, bucket):
    with open(filename, 'rb') as file:
        client.upload_fileobj(file, bucket, filename)


def zip_folders(zip_name: str, folders_to_zip: list, base_dir: str):
    with ZipFile(zip_name, 'w') as zip_object:
        for dir_name in folders_to_zip:
            for folder_name, subfolders, file_names in os.walk(os.path.join(base_dir, dir_name)):
                for file_name in file_names:
                    file_path = os.path.join(folder_name, file_name)
                    relative_name = file_path.split(os.path.join(base_dir, ''))[1]
                    zip_object.write(file_path, relative_name)


def date_prefix_name(name):
    date = strftime("%Y-%-m-%d", gmtime())
    return f'{date}{PREFIX_SEPARATOR}{name}';


def clean_up(zip_name: str):
    os.remove(zip_name)


def main():
    args = parser.parse_args()
    bucket_name = args.bucketname
    zip_name = date_prefix_name(args.zipname)
    dirs_to_zip = args.directories
    base_dir = args.base_dir

    if not does_bucket_exist(bucket_name):
        create_bucket(bucket_name)

    zip_folders(zip_name, dirs_to_zip, base_dir)

    upload_file(zip_name, bucket_name)

    clean_up(zip_name)


if __name__ == "__main__":
    main()
