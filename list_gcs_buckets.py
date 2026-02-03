#!/usr/bin/env python3

from datetime import datetime
#from google.cloud import resourcemanager_v3
from aiohttp import ClientSession
from gcloud.aio.storage import Storage
import google.auth
import google.auth.transport.requests

PROJECT="websites-270319"
UNITS = ("KB", "MB", "GB", "TB", "PB")
STORAGE_TIMEOUT = 15
"""
async def list_project_ids(credentials: any) -> list:

    resource_manager_client = resourcemanager_v3.ProjectsClient(credentials=credentials)
    projects = resource_manager_client.search_projects()
    return [project.project_id for project in projects]
"""
async def get_project_ids(session: ClientSession, access_token: str) -> list:

    url = "https://cloudresourcemanager.googleapis.com/v1/projects"
    headers = {'Authorization': f"Bearer {access_token}"}
    params = {}
    project_ids = []
    while True:
        async with (session.get(url, headers=headers, params=params, ssl=False) as response):
            #print(response)
            if int(response.status) == 200:
                _ = await response.json()
                project_ids.extend([project['projectId'] for project in _['projects']])
                if next_page_token := _.get('nextPageToken'):
                    params.update({'pageToken': next_page_token})
                else:
                    break
            else:
                break
    #print(project_ids)
    return project_ids

async def get_bucket_names(storage: Storage, project_id: str = None) -> list[str]:

    buckets = await storage.list_buckets(project=PROJECT, timeout=STORAGE_TIMEOUT)
    return [bucket.name for bucket in buckets]


async def list_objects(storage: Storage, bucket_name: str) -> dict:

    all_objects = []
    params = {'pageToken': None}
    print("Listing objects in bucket '{}'".format(bucket_name))
    while True:
        _ = await storage.list_objects(bucket=bucket_name, timeout=STORAGE_TIMEOUT)
        all_objects.extend(_.get('items', []))
        if next_page_token := _.get('nextPageToken'):
            params.update({'pageToken': next_page_token})
        else:
            break

    objects_metadata = {}
    for o in all_objects:
        #print(o)
        if updated := o.get('updated'):
            updated_ymd = updated[:10]
            updated_hms = updated[11:19]
            updated_timestamp = int(datetime.timestamp(datetime.strptime(updated_ymd + updated_hms, "%Y-%m-%d%H:%M:%S")))
        else:
            updated_timestamp = 0
        _ = {
            'size': o.get('size'),
            'crc32': o.get('crc32c'),
            #'bucket_name': o.get('bucket'),
            'storage_class': o.get('storageClass'),
            'content_type': o.get('contentType'),
            'updated_timestamp': updated_timestamp,
        }
        objects_metadata.update({ o['name']: _ })
    return objects_metadata


async def get_bucket_info(storage: Storage, bucket_name: str) -> dict:

    objects = await list_objects(storage, bucket_name)
    return {
        'name': bucket_name,
        'num_objects': len(objects),
        'total_size': sum([int(o.get('size', 0)) for o in objects.values()]),
        'last_updated':  datetime.fromtimestamp(max([o.get('updated_timestamp') for o in objects.values()])) if len(objects) > 0 else None,
    }


async def main() -> dict:

    from asyncio import gather
    from itertools import chain

    credentials, project_id = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'], quota_project_id=PROJECT)
    _ = google.auth.transport.requests.Request()
    credentials.refresh(_)
    access_token = credentials.token

    buckets = {}
    async with ClientSession() as session:
        project_ids = await get_project_ids(session, access_token)
        async with Storage(session=session) as storage:
            tasks = [get_bucket_names(storage, project_id=project_id) for project_id in project_ids]
            results = await gather(*tasks)
            bucket_names = set([item for item in list(chain(*results)) if item])
            #print("bucket_names:", bucket_names)
            tasks = [get_bucket_info(storage, bucket_name=bucket_name) for bucket_name in bucket_names]
            results = await gather(*tasks)
            buckets = dict(zip(bucket_names, results))
    return buckets

if __name__ == "__main__":

    from asyncio import run
    from prettytable import PrettyTable

    t = PrettyTable()
    t.field_names = ('Bucket Name', '# of Objects', 'Total Size', 'Last Updated')
    _ = run(main())
    for k, v in _.items():
        size = int(v.get('total_size', 0))
        unit = "Bytes"
        if size >= 1000:
            for i, unit in enumerate(UNITS):
                size = round(size / 1000, 3)
                if size < 1000:
                    break
        size_str = f"{size} {unit}"
        t.add_row([k, v['num_objects'], size_str, v['last_updated']])
    print(t)

