# import tinys3
import boto
import boto.s3
import sys
from boto.s3.key import Key
import boto3
import os

# AWS access
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.environ.get('S3_BUCKET')
fpath = "static/predicted.txt"

def uploadFileAWS(key, access_key, bucket_name, fpath):

    conn = boto.connect_s3(
        key,
        access_key, 
        host='s3.eu-central-1.amazonaws.com'
    )

    bucket = conn.get_bucket(bucket_name)

    k = Key(bucket)
    k.key = fpath
    k.set_contents_from_filename(
        fpath,
        num_cb=10
    )

def downloadFileAWS(key, access_key, bucket_name, fpath):

    s3 = boto3.client('s3', aws_access_key_id=key , aws_secret_access_key=access_key)
    s3.download_file(bucket_name,fpath,fpath)



# uploadFileAWS(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME, fpath)
# downloadFileAWS(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME, fpath)
