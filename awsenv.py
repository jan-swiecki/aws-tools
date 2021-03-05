#!/usr/bin/env python
"""awsenv

Usage:
  awsenv ctx (--list | --delete-all | (--add <alias> --aws-account-id <aws_account_id>) | (--delete <alias>))
  awsenv exec <alias>
  awsenv (-h | --help)
  awsenv --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""

from __future__ import print_function
import sys
import io
import os
import argparse
from pathlib import Path
import subprocess

from docopt import docopt
import boto3
import yaml


HOME = str(Path.home())
AWSENV_YAML_PATH = f"{HOME}/.aws/awsenv.yaml"

def confirm_or_exit(msg):
  if input(f"{msg} (y/n)") != "y":
    exit()

def aws_vault_add(alias):
  # subprocess.run(["exit", "1"], shell=True, check=True, capture_output=True)
  # os.system("aws-vault add")
  # os.putenv('AWS_VAULT_BACKEND', 'pass')
  os.system(f"aws-vault add '{alias}'")

def aws_vault_exec(alias):
  # subprocess.run(["exit", "1"], shell=True, check=True, capture_output=True)
  # os.system("aws-vault add")
  # os.putenv('AWS_VAULT_BACKEND', 'pass')
  # --pass-dir ~/.aws/.password-store
  ctx = get_context(alias)
  if ctx == None:
    print(f"error: no such context: {alias}")
    exit()

  os.system(f"_PS1=\"$PS1\" awsenv-vault-exec {alias}")

def add_context(alias, aws_account_id):
  Path(AWSENV_YAML_PATH).touch()
  with open(AWSENV_YAML_PATH, 'r') as stream:
    y = yaml.safe_load(stream)
    if y == None:
      y = {
        'contexts': {}
      }

    y['contexts'][alias] = {
      'alias': alias,
      'aws_account_id': aws_account_id
    }
    with io.open(AWSENV_YAML_PATH, 'w', encoding='utf8') as outfile:
      yaml.dump(y, outfile, default_flow_style=False, allow_unicode=True)

    aws_vault_add(alias)

    print(f"added {alias} ({aws_account_id})")

def delete_context(alias):
  Path(AWSENV_YAML_PATH).touch()
  with open(AWSENV_YAML_PATH, 'r') as stream:
    y = get_yaml()
    if alias in y['contexts']:
      aws_account_id = y['contexts'][alias]['aws_account_id']
      del y['contexts'][alias]
      with io.open(AWSENV_YAML_PATH, 'w', encoding='utf8') as outfile:
        yaml.dump(y, outfile, default_flow_style=False, allow_unicode=True)

      print(f"removed {alias} ({aws_account_id})")
    else:
      print('No such context')

def list_contexts():
  Path(AWSENV_YAML_PATH).touch()
  with open(AWSENV_YAML_PATH, 'r') as stream:
    print(stream.read())

def get_yaml():
  Path(AWSENV_YAML_PATH).touch()
  with open(AWSENV_YAML_PATH, 'r') as stream:
    y = yaml.safe_load(stream.read())
    if 'contexts' not in y:
      y['contexts'] = {}
    return y

def get_context(alias):
  y = get_yaml()
  return y['contexts'][alias] if alias in y['contexts'] else None

def delete_config():
  os.remove(AWSENV_YAML_PATH)

if __name__ == '__main__':
  args = docopt(__doc__, version='0.0.0')
  if args['ctx']:
    if args['--list']:
      list_contexts()
    elif args['--delete-all']:
      delete_config()
    elif args['--add']:
      add_context(args['<alias>'], args['<aws_account_id>'])
    elif args['--delete']:
      delete_context(args['<alias>'])
  elif args['exec']:
    aws_vault_exec(args['<alias>'])