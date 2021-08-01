
import boto
import boto.s3
import sys
from boto.s3.key import Key
import boto3

from azure.storage.blob import BlobClient

import os

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
    s3 = boto3.client('s3', aws_access_key_id=key, aws_secret_access_key=access_key)
    s3.download_file(bucket_name, fpath, fpath)


def uploadFileAzure(fpath, connection_string, container_name):

    blob = BlobClient.from_connection_string(
        conn_str=connection_string, 
        container_name=container_name,
        blob_name=fpath
    )

    with open(fpath, "rb") as data:
        blob.upload_blob(data, overwrite=True)

def downloadFileAzure(fpath, connection_string, container_name):

    blob = BlobClient.from_connection_string(
        conn_str=connection_string, 
        container_name=container_name,
        blob_name=fpath
    )

    with open(fpath, "wb") as my_blob:
        blob_data = blob.download_blob()
        blob_data.readinto(my_blob)

