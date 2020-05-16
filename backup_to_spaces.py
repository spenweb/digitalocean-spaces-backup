import os
import boto3

SPACES_KEY = os.getenv('SPACES_KEY')
SPACES_SECRET = os.getenv('SPACES_SECRET')
BUCKET_NAME = 'humhub-cfb03fc7'

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
    file = open(filename, 'rb')
    client.upload_fileobj(file, bucket, filename)
    file.close()


def main():
    if not does_bucket_exist(BUCKET_NAME):
        create_bucket(BUCKET_NAME)

    upload_file("test2.txt", BUCKET_NAME)


if __name__ == "__main__":
    main()
