# dobackup - DigitalOcean backup utility
Backup file to DigitalOcean. Supports rotating backups by default. Has the ability to compress a list of directories.

## Setup
1. Clone this repo
1. [Install pip](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-ubuntu-16-04)
1. Install requirements: `python -m pip install -r requirements.txt`
1. Add your S3 keys to the following named environment variables:
    - SPACES_KEY: `export SPACES_KEY=yourkey`
    - SPACES_SECRET: `export SPACES_SECRET=yoursecret`
    - SPACES_REGION_NAME: `export SPACES_REGION_NAME=yourregionname`
    - SPACES_ENDPOINT_URL: `export SPACES_ENDPOINT_URL=yourendpointurl`

## Help
`python dobackup.py -h`

## Example crontab entry for cron job
```
0 0 * * 1 source /home/username/.dobackup_env && /opt/digitalocean-spaces-backup/dobackup.py -o 5 --basedir /some/base/directory/to/backup space-name zip_name.zip specific/directory importantDir1 importantDir2
30 0 * * * mysqldump databasename | gzip -c > databasename.sql.gz && source /home/username/.dobackup_env && /opt/digitalocean-spaces-backup/dobackup.py -o 30 space-name database.sql.gz
```

## Example `.dobackup_env` file
See [`example.env`](example.env)