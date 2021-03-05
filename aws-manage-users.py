#!/usr/bin/env python-venv-aws
from __future__ import print_function
import sys
import argparse

import boto3

actions = ['create', 'delete_access_keys', 'reset_access_keys', 'delete']

parser = argparse.ArgumentParser(description='CRUD users')
parser.add_argument('username', metavar='username', nargs='?', type=str)
parser.add_argument('action', metavar=' | '.join(actions), nargs='?', type=str,
  choices=actions, help=f"One of: {', '.join(actions)}")
parser.add_argument('-l', metavar='list', help='list user', action=argparse.BooleanOptionalAction)
parser.add_argument('-f', metavar='force', help='force (dont prompt)', action=argparse.BooleanOptionalAction)
parser.add_argument('-q', metavar='quiet', help='quiet', action=argparse.BooleanOptionalAction)

args = parser.parse_args()
force = args.f
quiet = args.q
list = args.l

xs = args.username.split('/') if args.username else None

if xs is not None:
  if len(xs) == 1:
    username = xs[0]
    username_path = None
  else:
    username_path = xs[0]
    username = xs[1]

iam = boto3.client('iam')

def delete_access_keys():
  keys = iam.list_access_keys(UserName = args.username)['AccessKeyMetadata']
  for key in keys:
    log(f"deleting key {key['AccessKeyId']}")
    iam.delete_access_key(
      UserName=args.username,
      AccessKeyId=key['AccessKeyId']
    )

def delete_mfa_devices():
  mfas = iam.list_mfa_devices(UserName = args.username)['MFADevices']
  for mfa in mfas:
    log(f"deleting MFA device {mfa['SerialNumber']}")

    iam.deactivate_mfa_device(
        UserName=args.username,
        SerialNumber=mfa['SerialNumber']
    )

    iam.delete_virtual_mfa_device(
      SerialNumber=mfa['SerialNumber']
    )

def log(*args, **kwargs):
  if not quiet:
    print(*args, file=sys.stderr, **kwargs)

def einput(msg):
  print(msg, file=sys.stderr)
  return input()

def get_user():
  try:
    return iam.get_user(
      UserName=args.username
    )
  except Exception as err:
    if type(err).__name__ == 'NoSuchEntityException':
      log('user not found')
      exit()
    else:
      raise err

def get_user_or_none():
  try:
    # return iam.get_user(
    #   UserName=args.username
    # )
    xs = iam.list_users(PathPrefix=f"/tf/{args.username}")['Users']
    assert len(xs) < 2
    return xs[0] if len(xs) == 1 else None
  except Exception as err:
    if type(err).__name__ == 'NoSuchEntityException':
      return None
    else:
      raise err

if list:
  for user in iam.list_users(PathPrefix='/tf/')['Users']:
    print(f"{user['UserName']} {user['Arn']}")
elif args.action is None:
  user = get_user()
  log(user)
elif args.action == 'create':
  log(f"creating user {args.username}")

  if get_user_or_none() != None:
    print('user already exists')
    exit()

  iam.create_user(
    Path='/tf/',
    UserName=args.username
  )

  keys = iam.create_access_key(
    UserName=args.username
  )

  print(f"export AWS_ACCESS_KEY_ID={keys['AccessKey']['AccessKeyId']}")
  print(f"export AWS_SECRET_ACCESS_KEY={keys['AccessKey']['SecretAccessKey']}")
  log('done')
elif args.action == 'delete_access_keys':
  log(f"deleting access keys for user {args.username}")
  if not force and einput(f"are you sure you want to delete access keys for user {args.username}? (y/n)") != "y":
    exit()

  user = get_user()

  keys = iam.list_access_keys(UserName = args.username)['AccessKeyMetadata']
  if len(keys) == 0:
    log('user has no access keys')
    exit()
  else:
    for key in keys:
      log(f"deleting key {key['AccessKeyId']}")
      iam.delete_access_key(
        UserName=args.username,
        AccessKeyId=key['AccessKeyId']
      )
  log('done')

elif args.action == 'reset_access_keys':
  log(f"resetting keys for user {args.username}")
  if not force and einput(f"are you sure you want to reset keys for user {args.username}? (y/n)") != "y":
    exit()

  user = get_user()

  delete_access_keys()

  log('creating key')
  keys = iam.create_access_key(
    UserName=args.username
  )

  print(f"export AWS_ACCESS_KEY_ID={keys['AccessKey']['AccessKeyId']}")
  print(f"export AWS_SECRET_ACCESS_KEY={keys['AccessKey']['SecretAccessKey']}")
  log('done')
elif args.action == 'delete':
  if not force and einput(f"are you sure you want to delete user {args.username}? (y/n)") != "y":
    exit()

  user = get_user()

  delete_access_keys()
  delete_mfa_devices()
  log(f"deleting user {args.username}")
  iam.delete_user(
    UserName=args.username
  )
  log('done')
