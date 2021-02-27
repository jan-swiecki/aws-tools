#!/usr/bin/env python-venv-aws
import sys
import argparse

import boto3

ec2 = boto3.client('ec2')
for region in ec2.describe_regions()['Regions']:
    print(region['RegionName'])