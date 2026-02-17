#!/usr/bin/env python3

from pathlib import Path
from os import environ
from yaml import load, FullLoader
from google.cloud import storage

PWD = Path(__file__).parent

if __name__ == "__main__":

    with open('settings.yaml', mode="rb") as fp:
        settings = load(fp, Loader=FullLoader)
    gcp_project = settings.get('gcp_project')
    if gcp_key := settings.get('gcp_key'):
        gcp_key = PWD.joinpath(gcp_key)
        environ.update({'GOOGLE_APPLICATION_CREDENTIALS': gcp_key.__str__()})

    storage_client = storage.Client()
    buckets = storage_client.list_buckets(project=gcp_project)
    for bucket in list(buckets):
        bucket_size = 0
        blobs = storage_client.list_blobs(bucket.name)
        for blob in list(blobs):
            bucket_size = bucket_size + blob.size
        for i, unit in enumerate(["B", "KB", "MB", "GB", "TB", "PB"]):
            if bucket_size >= 1024:
                bucket_size /= 1024
            else:
                break
        print(bucket.name, bucket_size if i == 0 else f"{bucket_size:.2f}", unit)




