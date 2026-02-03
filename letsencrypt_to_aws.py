#!/usr/bin/env python3

import os
import sys
import time
import math
import datetime
import boto3

DAYS = 22
PROFILE_NAME = os.environ.get('AWS_PROFILE', "default")
REGION_NAME = os.environ.get('AWS_REGION', "us-east-1")
PLATFORM = sys.platform
SRC_DIR = "/usr/local/etc/letsencrypt/live" if 'freebsd' in PLATFORM else "/etc/letsencrypt/live"

print(REGION_NAME)
NOW =  math.floor(time.time())
THRESHOLD = NOW + 86400 * DAYS

# Create boto ACM client
boto3.setup_default_session(profile_name=PROFILE_NAME)
client = boto3.client('acm', region_name=REGION_NAME)

# Get a list of active SSL certs at AWS
_ = client.list_certificates(CertificateStatuses=['ISSUED','EXPIRED'])

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

        files = []

        src_dir = os.path.join(SRC_DIR, cert_domain)
        print("Checking", src_dir)
        if not (os.path.exists(src_dir) or os.path.isdir(src_dir)):
            continue

        # Check for new files
        for f in ["cert.pem", "privkey.pem", "chain.pem"]:
            file = os.path.join(src_dir, f)
            print(file)
            contents = open(file, 'rb').read()
            files.append(contents)

        # Re-import the Certificate
        response = client.import_certificate(
            CertificateArn = cert['CertificateArn'],
            Certificate = files[0],
            PrivateKey = files[1],
            CertificateChain = files[2]
        )
