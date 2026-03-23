#!/usr/bin/env python3

from os import environ
from pathlib import Path
from sys import platform
from time import time
import math
import datetime
import boto3

DAYS = 22
PROFILE_NAME = environ.get('AWS_PROFILE', "default")
REGION_NAME = environ.get('AWS_REGION', "us-east-1")
SRC_DIR = "/usr/local/etc/letsencrypt/live" if 'freebsd' in platform else "/etc/letsencrypt/live"
print(SRC_DIR)

NOW =  math.floor(time())
THRESHOLD = NOW + 86400 * DAYS

# Create boto ACM client
boto3.setup_default_session(profile_name=PROFILE_NAME, region_name=REGION_NAME)
client = boto3.client('acm', region_name=REGION_NAME)

# Get a list of active SSL certs at AWS
_ = client.list_certificates(CertificateStatuses=['ISSUED','EXPIRED'])
print(_)
for cert in _['CertificateSummaryList']:
    
    # Get details about each cert, namely the timestamp it expires
    cert_domain = cert['DomainName']
    print(cert_domain)
    cert_details = client.describe_certificate(CertificateArn=cert['CertificateArn'])
    expires_date = cert_details['Certificate']['NotAfter']
    expires_timestamp = datetime.datetime.timestamp(expires_date)
    #print(expires_date, expires_timestamp)

    # Check if cert is coming up for renewal or already expired
    if expires_timestamp < THRESHOLD or expires_timestamp <= NOW:

        _ = Path(SRC_DIR)
        src_path = _.joinpath(cert_domain)
        print("Checking", src_path)
        if not (src_path.exists() or src_path.is_dir()):
            continue

        # Check for new files
        source_files = {}
        for file in ("cert", "privkey", "chain"):
            source_file = src_path.joinpath(f'{file}.pem')
            print(source_file)
            source_contents = source_file.read_bytes()
            source_files.update({file: source_contents})

        # Re-import the Certificate
        response = client.import_certificate(
            CertificateArn = cert['CertificateArn'],
            Certificate = source_files['cert'],
            PrivateKey = source_files['privkey'],
            CertificateChain = source_files['chain'],
        )
