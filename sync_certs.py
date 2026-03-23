#!/usr/bin/env python3

from sys import argv, platform
from os.path import getmtime
from shutil import copy, copystat
from pathlib import Path

PWD = Path(__file__).parent
DST_DIR = "../../private/ssl"
FILES = { 'key': 'privkey.pem', 'crt': 'cert.pem', 'cer': 'fullchain.pem' }

def main(mode = None):

    _ = "/usr/local/etc/letsencrypt/live" if 'freebsd' in platform else "/etc/letsencrypt/live"
    src_dir = Path(_)
    dst_dir = PWD.joinpath(DST_DIR)
    sites = [source_file.name for source_file in src_dir.iterdir() if source_file.is_dir()]
    for site in sites:
        for file_extension, file_name in FILES.items():
            src_path = src_dir.joinpath(site, file_name)
            _ = site.replace(".", "_")
            _ = f"{_}.{file_extension}"
            dst_path = dst_dir.joinpath(_)
            if getmtime(src_path) >= getmtime(dst_path):
                continue
            if mode == "dry":
                print(src_path, "->", dst_path)
            else:
                print(f"Copying {src_path} -> {dst_path}")
                copy(src_path, dst_path)
                copystat(src_path, dst_path)

if __name__ == "__main__":

    if len(argv) > 1 and argv[1] == "-d":
        main(mode = "dry")
    else:
        main()
    quit()

