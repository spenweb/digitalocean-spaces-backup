# dobackup - DigitalOcean backup utility
Backup file to DigitalOcean. Supports rotating backups by default. Has the ability to compress a list of directories.

## Setup
1. Clone this repo
1. Install requirements: `pip install -r requirements.txt`
1. Add your S3 keys to the following named environment variables:
    - SPACES_KEY: `export SPACES_KEY=yourkey`
    - SPACES_SECRET: `export SPACES_SECRET=yoursecret`

## Help
`python dobackup.py -h`