#!/bin/bash

prefix="$HOME/.local/bin/"

read -p "remove venv=aws? (y?)" && venv-exec delete aws

uninstall () {
  rm "$prefix/$1" >/dev/null 2>&1 || true
  echo "$1 removed"
}

list=`cat manifest.txt`

for l in $list; do
  uninstall "$l"
done
uninstall "venv-exec"

read -p "remove venv from ~/.bashrc? (y?)" q && [ "$q" == "y" ] && (
  cp -f ~/.bashrc ~/.bashrc.bak
  echo "created ~/.bashrc.bak"
  sed -i "/$(cat venv-bashrc)/d" ~/.bashrc
  echo "removed venv to ~/.bashrc"
)

echo "done"