#!/usr/bin/env python-venv-aws
import sys
import argparse

import boto3

parser = argparse.ArgumentParser(description='Completely destroy RDS with all it\'s backups WITHOUT final snapshot')
parser.add_argument('rds', metavar='rds', type=str, help='rds name')

args = parser.parse_args()

RDS = args.rds

print('checking if rds exists')

rds = boto3.client('rds')

def get_instance():
  try:
    instances = rds.describe_db_instances(
        DBInstanceIdentifier=RDS,
        MaxRecords=50
    )
  except Exception as err:
    if type(err).__name__ == 'DBInstanceNotFoundFault':
      print('rds not found or already deleted')
      return None
    else:
      raise err

  if len(instances['DBInstances']) == 0:
    print('rds not found or already deleted')
    return None

  instance = instances['DBInstances'][0]
  return instance

instance = get_instance()
if instance == None:
  exit(1)

status = instance['DBInstanceStatus']

def wait_delete():
  while status == 'deleting':
    instance = get_instance()
    print(f"status = f{instance['DBInstanceStatus']}")
    if instance == None or instance['DBInstanceStatus'] != 'deleting':
      print('done')
      return

if status == 'deleting':
  print('already deleting')
  if input(f"wait until complete? (y/n)") != "y":
    exit()
  wait_delete()

if input(f"are you sure you want to COMPLETELY DESTROY {RDS} WITHOUT LEAVING ANY BACKUPS/SNAPSHOTS? (y/n)") != "y":
  exit()

print('nuking RDS')

rds.delete_db_instance(
  DBInstanceIdentifier=RDS,
  SkipFinalSnapshot=True,
  DeleteAutomatedBackups=True
)
wait_delete()

print('done')