#!/bin/bash -i
set -eo pipefail

./venv-exec create-if-not-exists aws

. ./venv-exec load aws

prefix="$HOME/.local/bin/"

install () {
  # ln -sf "$PWD/$1.py" "$prefix/$1"
  cat << EOF > "$prefix/$1"
#!/bin/bash

. venv-exec load aws
python "$PWD/$1.py" "\$@"
EOF
  chmod +x "$prefix/$1"
  echo "$1 installed"
}

list=`cat manifest.txt`

for l in $list; do
  install "$l"
done

ln -sf "$PWD/venv-exec" "$prefix/venv-exec"

read -p "add venv to ~/.bashrc? (y?)" q && [ "$q" == "y" ] && (
  cp -f ~/.bashrc ~/.bashrc.bak
  echo "created ~/.bashrc.bak"
  sed -i "/$(cat venv-bashrc)/d" ~/.bashrc
  echo >> ~/.bashrc
  cat venv-bashrc >> ~/.bashrc
  echo "added venv to ~/.bashrc"
)

pip install poetry
poetry install
echo "done"