#!/bin/bash -i

venv-exec create-if-not-exists aws

. venv-exec load aws

prefix="$HOME/.local/bin/"

install () {
  # ln -sf "$PWD/$1.py" "$prefix/$1"
  cat << EOF > "$prefix/$1"
#!/bin/bash

venv load aws
python "$PWD/$1.py" "$@"
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
  sed -i '/venv () { . venv-exec "$@"; }/d' ~/.bashrc
  echo 'venv () { . venv-exec "$@"; }' >> ~/.bashrc
  echo "added venv to ~/.bashrc"
)

pip install pyyaml
echo "done"