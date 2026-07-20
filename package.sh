rm -rf dist &&
  mkdir -p dist &&
  rsync -a --exclude-from=.gitignore --exclude={.git,*.sh,tests/,dist/,docs/,legacy/,latex/,README.md,pyrefly.toml,requirements.txt,ruff.toml,.gitignore,.gitattributes,.vscode,examples/} ./ dist/ &&
  sed -i '/latex/d' dist/__init__.py &&
  cd dist &&
  blender --command extension validate &&
  blender --command extension build &&
  find . -type f -name "*.zip" -exec mv {} ../ \; &&
  cd .. &&
  rm -rf dist
