#!/usr/bin/python
import boto3
import os
from zipfile import ZipFile
from datetime import datetime
import argparse
from enum import Enum, auto

# Read S3 keys from environment variables
SPACES_KEY = os.getenv('SPACES_KEY')
SPACES_SECRET = os.getenv('SPACES_SECRET')

# Constants
PREFIX_SEPARATOR = '____'
TIME_FORMAT = "%Y%m%d%H%M%S"
DEFAULT_ROTATION_COUNT_MAX = 10

# Mode types
class Mode(Enum):
    SINGLE_FILE = auto()
    COMPRESS_DIRS = auto()


# Setup command line arguments
parser = argparse.ArgumentParser(description='Backup file to DigitalOcean. Supports rotating backups by default. '
                                             'Has the ability to compress a list of directories.', prog='dobackup',
                                 epilog='Created 2020 by Spencer Brown')
parser.add_argument('bucketname', type=str, help='The s3 compatible bucket name')
parser.add_argument('backupfilename', type=str, help='The file name for a single file to be backed up. When a list '
                                                     'of directories is provided, this is the name of the generated '
                                                     'compressed zip file of the provided directories. This file name '
                                                     'will be prefixed with a timestamp and also used for tracking old '
                                                     'backups when rotating.')
parser.add_argument('--basedir', dest='base_dir', type=str, help='Parent directory that all directories to zip are in. '
                                                                 'Defaults to cwd.', default=os.getcwd())
parser.add_argument('directories', metavar='D', type=str, nargs='*', help='List of directories to zip up')
parser.add_argument('-o', '--rotationcountmax', dest='rotation_count_max', type=int, help='Max number of backups for '
                                                                                          'the given backupfilename ('
                                                                                          'default is ' +
                                                                                          str(
                                                                                              DEFAULT_ROTATION_COUNT_MAX
                                                                                          ) + ')',
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


def upload_file(filename: str, bucket: str, rename: str = None):
    with open(filename, 'rb') as file:
        client.upload_fileobj(file, bucket, filename if rename is None else rename)


def delete_remote_file(filename, bucket):
    client.delete_object(Bucket=bucket, Key=filename)


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
    """
    Given a list of files that have a similar file name, sort the files by date and then return a list with
    the full file name (with time prefix) of files that should be deleted according to the rotation count max.
    :param file_data:
    :param rotation_count_max:
    :return:
    """
    files_to_delete = []

    if len(file_data) > rotation_count_max:
        files_with_good_dates = []
        for file_parts in file_data:
            try:
                d = datetime.strptime(file_parts[0], TIME_FORMAT)
                file_parts.append(d)
                files_with_good_dates.append(file_parts)
            except ValueError:
                print(f'Badly formatted time prefix on file name: {file_parts[0]}{PREFIX_SEPARATOR}{file_parts[1]}')

        # Sort the files
        files_with_good_dates.sort(key=lambda tup: tup[2])

        overage = max(0, len(files_with_good_dates) - rotation_count_max)
        file_delete_data = files_with_good_dates[0:overage]

        for data in file_delete_data:
            files_to_delete.append(f'{data[0]}{PREFIX_SEPARATOR}{data[1]}')

    return files_to_delete


def remote_clean_up(filename: str, bucket: str, rotation_count_max: int):
    """
    Rotate the backups according to the rotation count max value for the particular filename (without time prefix).
    :param filename:
    :param bucket:
    :param rotation_count_max:
    :return:
    """
    file_parts = find_related_remote_files(filename, bucket)
    files_to_delete = determine_files_to_delete(file_parts, rotation_count_max)
    for file in files_to_delete:
        delete_remote_file(file, bucket)


def main():
    mode = None
    args = parser.parse_args()
    bucket_name = args.bucketname
    backup_name = args.backupfilename  # Possibly contains directory in the name
    dated_backup_name = date_prefix_name(os.path.basename(backup_name))
    dirs_to_zip = args.directories
    base_dir = args.base_dir
    rotation_count_max = args.rotation_count_max

    # Determine what mode (upload existing or compress dirs and upload generated)
    file_exists = os.path.isfile(os.path.join(base_dir, backup_name))
    if file_exists and len(dirs_to_zip) == 0:
        mode = Mode.SINGLE_FILE
    elif not file_exists and len(dirs_to_zip) > 0:
        mode = Mode.COMPRESS_DIRS
    else:
        print("Bad usage!")
        parser.print_help()
        exit()

    # Prepare bucket
    if not does_bucket_exist(bucket_name):
        create_bucket(bucket_name)

    if mode == Mode.COMPRESS_DIRS:
        zip_folders(dated_backup_name, dirs_to_zip, base_dir)
        upload_file(dated_backup_name, bucket_name)
        local_clean_up(dated_backup_name)

    if mode == Mode.SINGLE_FILE:
        upload_file(backup_name, bucket_name, dated_backup_name)

    # Auto rotate backups
    remote_clean_up(os.path.basename(backup_name), bucket_name, rotation_count_max)


if __name__ == "__main__":
    main()
