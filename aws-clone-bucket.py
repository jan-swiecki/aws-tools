#!/usr/bin/env python-venv-aws
import sys
import argparse
import time

import boto3

parser = argparse.ArgumentParser(description='1-1 clone whole bucket with all objects to another bucket (including versioned objects)')
parser.add_argument('source_bucket', metavar='source_bucket', type=str, help='source bucket name')
parser.add_argument('target_bucket', metavar='target_bucket', type=str, help='target bucket name')


args = parser.parse_args()
SOURCE_BUCKET = args.source_bucket
TARGET_BUCKET = args.target_bucket

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

print('checking if source bucket exists')

source_bucket = s3.Bucket(SOURCE_BUCKET)
target_bucket = s3.Bucket(TARGET_BUCKET)

if source_bucket.creation_date == None:
  print(f"source bucket {SOURCE_BUCKET} does not exist")
  exit()

def get_location(bucket_name):
  response = s3_client.get_bucket_location(Bucket=bucket_name)
  return response['LocationConstraint']

def get_s3_location(bucket_name):
  conn = boto3.connect_s3()
  bucket = conn.get_bucket(bucket_name)
  return bucket.get_location()

if target_bucket.creation_date == None:
  print(f"target bucket {TARGET_BUCKET} does not exist")
  source_location = get_location(SOURCE_BUCKET)
  if input(f"create {TARGET_BUCKET} in {source_location}? (y/n)") != "y":
    exit()
  else:
    s3_client.create_bucket(
      Bucket=TARGET_BUCKET,
      ACL='private',
      CreateBucketConfiguration={'LocationConstraint': source_location})

    time.sleep(5)

    response = s3_client.put_public_access_block(
      Bucket=TARGET_BUCKET,
      PublicAccessBlockConfiguration={
        'BlockPublicAcls': True,
        'IgnorePublicAcls': True,
        'BlockPublicPolicy': True,
        'RestrictPublicBuckets': True
      }
    )

if target_bucket.creation_date == None:
  print(f"FATAL: target bucket {TARGET_BUCKET} still does not exist")
  exit(1)

def clone(from_bucket, to):
  from_keys = set([x.key for x in from_bucket.objects.all()])
  target_keys = set([x.key for x in to.objects.all()])

  for from_key in (from_keys - target_keys):
    print(f"copy {from_bucket.name}/{from_key} into {to.name} ... ", end='')
    copy_source = {
      'Bucket': from_bucket.name,
      'Key': from_key
    }
    to.copy(copy_source, from_key)
    print("OK")

  print("done")

clone(source_bucket, target_bucket)

# if input(f"are you sure you want to COMPLETELY DESTROY {SOURCE_BUCKET}? (y/n)") != "y":
#   exit()

# print('nuking objects and all their versions')
# bucket.object_versions.delete()

# if not args.dont_remove_bucket:
#   if input(f"are you sure you want to DELETE empty bucket {SOURCE_BUCKET}? (y/n)") != "y":
#     exit()

#   print('nuking bucket')
#   bucket.delete()

# print('done')