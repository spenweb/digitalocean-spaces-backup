#!/usr/bin/python
import os
import boto3
from zipfile import ZipFile
from datetime import datetime
import argparse

# Read S3 keys from environment variables
SPACES_KEY = os.getenv('SPACES_KEY')
SPACES_SECRET = os.getenv('SPACES_SECRET')

# Constants
PREFIX_SEPARATOR = '____'
TIME_FORMAT = "%Y%m%d"
DEFAULT_ROTATION_COUNT_MAX = 10

# Setup command line arguments
parser = argparse.ArgumentParser(description='Backup list of directories to DigitalOcean supports rotating backups by '
                                             'default', prog='dobackup', epilog='Created 2020 by Spencer Brown')
parser.add_argument('bucketname', type=str, help='The s3 compatible bucket name')
parser.add_argument('zipname', type=str, help='Name of the zip file to create (before timestamped)')
parser.add_argument('--basedir', dest='base_dir', type=str, help='Parent directory that above all directories to zip',
                    default=os.getcwd())
parser.add_argument('directories', metavar='D', type=str, nargs='+', help='List of directories to zip up')
parser.add_argument('-o', '--rotationcountmax', dest='rotation_count_max', type=int, help='Max number of back ups for '
                                                                                          'the given zipname',
                    default=DEFAULT_ROTATION_COUNT_MAX)

# Initialize the S3 session
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


def delete_remote_file(filename, bucket):
    client.delete_object(Bucket=bucket,
                         Key=filename)


def zip_folders(zip_name: str, folders_to_zip: list, base_dir: str):
    with ZipFile(zip_name, 'w') as zip_object:
        for dir_name in folders_to_zip:
            for folder_name, subfolders, file_names in os.walk(os.path.join(base_dir, dir_name)):
                for file_name in file_names:
                    file_path = os.path.join(folder_name, file_name)
                    relative_name = file_path.split(os.path.join(base_dir, ''))[1]
                    zip_object.write(file_path, relative_name)


def date_prefix_name(name):
    date = datetime.strftime(datetime.now(), TIME_FORMAT)
    return f'{date}{PREFIX_SEPARATOR}{name}';


def local_clean_up(zip_name: str):
    os.remove(zip_name)


def find_related_remote_files(filename: str, bucket: str) -> list:
    related_files = list()

    response = client.list_objects(Bucket=bucket)
    for obj in response['Contents']:
        parts = obj['Key'].split(PREFIX_SEPARATOR)
        if len(parts) == 2 and parts[1] == filename:
            related_files.append(parts)
    return related_files


def determine_files_to_delete(file_data: list, rotation_count_max: int) -> list:
    count = len(file_data)
    files_to_delete = []

    if count > rotation_count_max:
        files_with_dates = []
        for file_parts in file_data:
            d = datetime.strptime(file_parts[0], TIME_FORMAT)
            file_parts.append(d)
            files_with_dates.append(file_parts)

        # Sort the files
        files_with_dates.sort(key=lambda tup: tup[2])

        overage = count - rotation_count_max
        file_delete_data = files_with_dates[0:overage]

        for data in file_delete_data:
            files_to_delete.append(f'{data[0]}{PREFIX_SEPARATOR}{data[1]}')

    return files_to_delete


def remote_clean_up(filename: str, bucket: str, rotation_count_max: int):
    file_parts = find_related_remote_files(filename, bucket)
    files_to_delete = determine_files_to_delete(file_parts, rotation_count_max)
    pass


def main():
    args = parser.parse_args()
    bucket_name = args.bucketname
    zip_name = args.zipname
    dated_zip_name = date_prefix_name(zip_name)
    dirs_to_zip = args.directories
    base_dir = args.base_dir
    rotation_count_max = args.rotation_count_max

    if not does_bucket_exist(bucket_name):
        create_bucket(bucket_name)

    zip_folders(dated_zip_name, dirs_to_zip, base_dir)

    upload_file(dated_zip_name, bucket_name)

    local_clean_up(dated_zip_name)

    remote_clean_up(zip_name, bucket_name, rotation_count_max)


if __name__ == "__main__":
    main()
