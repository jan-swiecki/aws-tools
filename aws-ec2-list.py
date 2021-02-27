#!/usr/bin/env python-venv-aws
import sys
import argparse

import boto3

parser = argparse.ArgumentParser(description='List AWS EC2 pricing')
parser.add_argument('region', metavar='region', type=str,
                    help='region name')
parser.add_argument('pattern', metavar='pattern', type=str, nargs='?',
                    help='ec2 pattern')

args = parser.parse_args()

def ec2_instance_types(region_name, filter=None):
    '''Yield all available EC2 instance types in region <region_name>'''
    ec2 = boto3.client('ec2', region_name=region_name)
    describe_args = {}
    if filter is not None:
      describe_args['Filters'] = [
          {
              'Name': 'instance-type',
              'Values': [
                  filter+'*',
              ]
          },
      ]
      
    while True:
        describe_result = ec2.describe_instance_types(**describe_args)
        yield from [i for i in describe_result['InstanceTypes']]
        if 'NextToken' not in describe_result:
            break
        describe_args['NextToken'] = describe_result['NextToken']

ec2s = ec2_instance_types(args.region, filter=args.pattern)
ec2s = sorted(ec2s, key=lambda x: (int(x['VCpuInfo']['DefaultVCpus']), int(x['MemoryInfo']['SizeInMiB']), x['InstanceType']))

print("%-18s %-6s %-12s" % ('Name', 'VCPUs', 'Memory'))
for ec2 in ec2s:
  print("%-18s %-6s %-12s" % (
    ec2['InstanceType'],
    ec2['VCpuInfo']['DefaultVCpus'],
    str(round(ec2['MemoryInfo']['SizeInMiB']/1024))+"G"
  ))