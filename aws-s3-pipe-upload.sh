#!/bin/bash
set -eo pipefail

if [ -z "$1" ]; then
  cat <<EOF
usage: stdin_source | aws-s3-pipe-cp <s3_target>

Options:
  s3_target  S3 target in the format: s3://<your_bucket>/<path>

This will run something similar to below command:
  stdin_source | aws s3 cp - <s3_target>
EOF
  exit
fi

# '< /dev/null' disconnects from stdin
echo "Checking access permissions"

bucket="$(echo "$1" | cut -d '/' -f3)"

echo dummy | aws s3 cp - "s3://$bucket/aws-s3-pipe-upload-test-you-can-remove-me"

echo "Uploading to $1"
aws s3 cp - "$1"