import json
import collections

with open("instances.json") as fp:
    _ = json.load(fp)
    _ = _.get('items', {})

matches = []
for k, v in _.items():
    if not k.startswith("zones"):
        continue
    for disk in v.get('disks', []):
        if 'r8040' in disk.get('sourceImage'):
            zone = disk['zone'].split('/')[-1]
            region = zone[:-2]
            matches.append({
                'name': disk['name'],
                'region': region,
            })

    #print(k, v)

#print(_)
count = collections.Counter([m['region'] for m in matches])
for k, v in count.items():
    print("GCP ", k)
    disks = [d['name'] for d in matches if d['region'] == k]
    for disk in disks:
        print(" ", disk)
