#!/usr/bin/env python-venv-aws
from __future__ import print_function
import sys
import io
import argparse
from pathlib import Path

import boto3
import yaml

HOME = str(Path.home())
AWSENV_YAML_PATH = f"{HOME}/.aws/awsenv.yaml"

def log(*args, **kwargs):
  if not quiet:
    print(*args, file=sys.stderr, **kwargs)

def einput(msg):
  print(msg, file=sys.stderr)
  return input()

def confirm_or_exit(msg):
  if input(f"{msg} (y/n)") != "y":
    exit()

parser = argparse.ArgumentParser(description='aws env management')
parser.add_argument('--ctx', '-c', help='context', nargs='?')

subparsers = parser.add_subparsers(description='sub-command help')

_aws_contexts = subparsers.add_parser('ctx', description="asd")
_aws_contexts.set_defaults(command='ctx')
# __aws_contexts = _aws_contexts.add_mutually_exclusive_group(required=True)
__aws_contexts_default = _aws_contexts.add_argument_group()
__aws_contexts_default.add_argument('--list', '-l', help='show config', action='store_true')
__aws_contexts_default.add_argument('--reset', '-r', help='reset config', action='store_true')
__aws_contexts_add = _aws_contexts.add_argument_group()
__aws_contexts_add.add_argument('--add', required=True, metavar='<aws_account_name>=<aws_account_id>', help='add aws account')
__aws_contexts_add.add_argument('--xyz', required=True, metavar='<aws_account_name>=<aws_account_id>', help='add aws account')

# _ctx = subparsers.add_parser('ctx', description="asd")
# _ctx.set_defaults(command='ctx')
# g = _ctx.add_mutually_exclusive_group(required=True)
# g.add_argument('--list', '-l', help='show config', action='store_true')
# g.add_argument('--reset', '-r', help='reset config', action='store_true')
# g.add_argument('--add-account', metavar='<aws_account_name>=<aws_account_id>', help='add aws account')



args = parser.parse_args()
# group.add_argument('--account', '-a', metavar='aws_account_name', help='use <aws_account_name>')
# parser.add_argument('-f', metavar='force', help='force (dont prompt)', action=argparse.BooleanOptionalAction)
# parser.add_argument('-q', metavar='quiet', help='quiet', action=argparse.BooleanOptionalAction)

def add_account(aws_account_name, aws_account_id):
  Path(AWSENV_YAML_PATH).touch()
  with open(AWSENV_YAML_PATH, 'r') as stream:
    y = yaml.safe_load(stream)
    if y == None:
      y = {}
    y[aws_account_name] = {
      'aws_account_name': aws_account_name,
      'aws_account_id': aws_account_id,
      'users': []
    }
    with io.open(AWSENV_YAML_PATH, 'w', encoding='utf8') as outfile:
      yaml.dump(y, outfile, default_flow_style=False, allow_unicode=True)

def list_contexts():
  Path(AWSENV_YAML_PATH).touch()
  with open(AWSENV_YAML_PATH, 'r') as stream:
    print(stream.read())

def purge_config():
  with io.open(AWSENV_YAML_PATH, 'w', encoding='utf8') as outfile:
    yaml.dump({}, outfile, default_flow_style=False, allow_unicode=True)

if 'command' in args and args.command == 'contexts':
  if 'add_account' in args and args.add_account:
    xs = args.add_account.split("=")
    if len(xs) != 2:
      print('Must be in format: name=value')
      exit(1)
    add_account(xs[0], xs[1])
  if 'list' in args and args.list:
    list_contexts()
  elif 'reset' in args and args.reset:
    confirm_or_exit(f"Reset {AWSENV_YAML_PATH}?")
    purge_config()
else:
  parser.print_help()