#!/bin/bash -i
set -eou pipefail

if [ ! -z "$_PS1" ]; then
  PS1="$_PS1"
fi

if [ "${AWS_ENV:-}" != "" ]; then
  echo "error: cannot run nested awsenv sessions (trying to run session $1 on top of $AWS_ENV)" >&2
  exit 1
fi

. venv-exec load aws

export AWS_ENV="$1"
PS1="[$1] $PS1"

PROMPT_COMMAND='PS1="'$PS1'";unset PROMPT_COMMAND' \
  aws-vault exec "$@"