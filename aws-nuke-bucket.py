#!/usr/bin/env python-venv-aws
import sys
import argparse

import boto3

parser = argparse.ArgumentParser(description='Completely destroy bucket with all objects (including versioned objects)')
parser.add_argument('bucket', metavar='bucket', type=str, help='bucket name')
parser.add_argument('--dont-remove-bucket', action=argparse.BooleanOptionalAction)

args = parser.parse_args()

BUCKET = args.bucket

print('checking if bucket exists')

s3 = boto3.resource('s3')
bucket = s3.Bucket(BUCKET)

if bucket.creation_date == None:
  print(f"bucket {BUCKET} does not exist")
  exit()

if input(f"are you sure you want to COMPLETELY DESTROY {BUCKET}? (y/n)") != "y":
  exit()

print('nuking objects and all their versions')
bucket.object_versions.delete()

if not args.dont_remove_bucket:
  if input(f"are you sure you want to DELETE empty bucket {BUCKET}? (y/n)") != "y":
    exit()

  print('nuking bucket')
  bucket.delete()

print('done')