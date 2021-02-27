#!/bin/bash

prefix="$HOME/.local/bin/"

install () {
  ln -sf "$PWD/$1.py" "$prefix/$1"
  echo "$1 installed"
}

uninstall () {
  rm "$prefix/$1" >/dev/null 2>&1 || true
  echo "$1 removed"
}

[ -f "$prefix/aws-nuke-bucket" ] && {
  uninstall aws-regions
  uninstall aws-ec2-list
  uninstall aws-nuke-bucket
  echo "done"
} || {
  install aws-regions
  install aws-ec2-list
  install aws-nuke-bucket
  echo "done"
}