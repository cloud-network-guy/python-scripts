#!/usr/bin/env python3

import tomli
from os import environ, path, access, R_OK
from platform import system
from tempfile import gettempdir
from urllib.parse import quote
import google.auth
import google.auth.transport.requests
from git import Repo

SSH_PRIVATE_KEY_FILES = ('id_rsa', 'id_ecdsa', 'id_ed25519')


def configure_git_ssh():

    if not (git_ssh_variant := environ.get('GIT_SSH_VARIANT')):
        git_ssh_variant = "ssh"
        environ.update({'GIT_SSH_VARIANT': git_ssh_variant})

    if not (git_ssh_command := environ.get('GIT_SSH_COMMAND')):
        # Scan SSH Key locations to find valid private key file
        my_os = system().lower()
        home_dir = environ.get('HOME')
        if my_os.startswith('win'):
            home_dir = environ.get("USERPROFILE")
        ssh_private_key_file = None
        for private_key_file in SSH_PRIVATE_KEY_FILES:
            _ = f"{home_dir}/.ssh/{private_key_file}"
            if my_os.startswith('win'):
                _ = _.replace("/", "\\")
            if path.exists(_) and path.isfile(_) and access(_, R_OK):
                ssh_private_key_file = _
                break
        git_ssh_command = f"ssh -i {ssh_private_key_file}"
        environ.update({'GIT_SSH_COMMAND': git_ssh_command})


def get_gcp_access_token() -> str:

    credentials, project = google.auth.default()
    _ = google.auth.transport.requests.Request()
    credentials.refresh(_)
    return credentials.token


def main():

    rs = {
        'username': quote("jheyer.lab@otxlab.net"),
        #'username': quote("jheyer@idldap.net"),
        'hostname': "source.developers.google.com",
        'repo': "p/otl-core-network-pre-comm/r/otl-network",
        #'repo': "p/otc-core-network-prod/r/otc-network",
        'transport': "https",
        'port': None,
        'default_branch': 'master',
    }

    rs_type = "unknown"
    if "developers.google.com" in rs['hostname']:
        rs_type = "google_csr"
    if "github.com" in rs['hostname']:
        rs_type = "github"
    rs.update({'type': rs_type})

    if rs['transport'] == "ssh":
        configure_git_ssh()
        rs.update({'port': 2022 if rs_type == "google_csr" else 22})
    if rs['transport'] == "https":
        rs.update({'port': 443})

    if rs['type'] == "google_csr" and rs['transport'] == "https":
        try:
            access_token = get_gcp_access_token()
        except google.auth.exceptions.RefreshError as e:
            quit(e)
        rs.update({'username': f"{rs['username']}:{access_token}"})

    url = f"{rs['transport']}://{rs['username']}@{rs['hostname']}:{rs['port']}/{rs['repo']}"
    to_path = rs['repo'].split('/')[-1]
    branch = rs['default_branch']

    if path.exists(to_path):
        # Perform git pull
        repo = Repo(path=to_path)
        origin = repo.remotes.origin
        origin.pull()
    else:
        # Perform git clone
        repo = Repo.clone_from(url=url, to_path=to_path, branch=branch)


if __name__ == "__main__":

    main()
