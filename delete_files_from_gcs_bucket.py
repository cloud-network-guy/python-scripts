#!/usr/bin/env python3

from pathlib import Path
from time import time
from os import environ
from yaml import load, FullLoader
from google.cloud import storage

PWD = Path(__file__).parent
SETTINGS_FILE = "settings.yaml"
DAYS = 10


def read_settings(settings_file: str = SETTINGS_FILE) -> dict:

    _settings_file = PWD.joinpath(settings_file)
    assert _settings_file.exists(), f"Error occurred while reading '{_settings_file}'"
    with open(_settings_file, mode="rb") as fp:
        return load(fp, Loader=FullLoader)


def list_blobs(bucket_name: str, prefix: str = None) -> list:

    storage_client = storage.Client()
    _ = storage_client.list_blobs(bucket_name, prefix=prefix)
    return list(_)


def delete_blobs(bucket_name: str, files: tuple) -> None:

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    for file in files:
        _ = bucket.blob(file)
        _.delete()
        print("Object", _.name, "has been deleted")

    return


if __name__ == "__main__":

    settings = read_settings()
    if _bucket_name := settings.get('bucket_name'):
       _bucket_prefix = settings.get('bucket_prefix')
       if gcp_key := settings.get('gcp_key'):
           gcp_key = PWD.joinpath(gcp_key)
           environ.update({'GOOGLE_APPLICATION_CREDENTIALS': gcp_key.__str__()})
       _ = list_blobs(_bucket_name, _bucket_prefix)
       _ = sorted(_, key=lambda x: int(x.updated.timestamp()))  # sort by last modified so oldest are first to be deleted
       blobs = [blob.name for blob in _ if int(blob.updated.timestamp()) < (round(time()) - (3600 * 24 * DAYS))]
       delete_blobs(_bucket_name, tuple(blobs))
    else:
        quit(f"Bucket name was not configured in '{SETTINGS_FILE}'.")
