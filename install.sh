#!/bin/bash
set -eo pipefail

./venv-exec create-if-not-exists aws

. ./venv-exec load aws

prefix="$HOME/.local/bin/"

install () {
  # ln -sf "$PWD/$1.py" "$prefix/$1"
  cat << EOF > "$prefix/$1"
#!/bin/bash -i

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
ln -sf "$PWD/awsenv-vault-exec.sh" "$prefix/awsenv-vault-exec"
ln -sf "$PWD/aws-s3-pipe-upload.sh" "$prefix/aws-s3-pipe-upload"

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