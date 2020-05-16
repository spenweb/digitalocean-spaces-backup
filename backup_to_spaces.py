import os
import boto3
from zipfile import ZipFile
from os.path import basename
from time import gmtime, strftime

SPACES_KEY = os.getenv('SPACES_KEY')
SPACES_SECRET = os.getenv('SPACES_SECRET')
BUCKET_NAME = 'humhub-cfb03fc7'
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
                    zip_object.write(file_path, basename(file_path))


def date_prefix_name(name):
    date = strftime("%Y-%-m-%d", gmtime())
    return f'{date}{PREFIX_SEPARATOR}{name}';


def clean_up(zip_name: str):
    os.remove(zip_name)


def main():
    zip_name = date_prefix_name("test.zip")
    dirs_to_zip = ["test_dir"]
    base_dir = os.getcwd()

    if not does_bucket_exist(BUCKET_NAME):
        create_bucket(BUCKET_NAME)

    zip_folders(zip_name, dirs_to_zip, base_dir)

    upload_file(zip_name, BUCKET_NAME)

    clean_up(zip_name)


if __name__ == "__main__":
    main()
