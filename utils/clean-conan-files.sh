#!/bin/bash
echo "Cleaning Conan intermediary files"


files=(
  "conanbuildenv-release-x86_64.sh" \
  "conanbuildenv-debug-x86_64.sh" \
  "conanbuild.sh" \
  "conanrunenv-release-x86_64.sh" \
  "conanrunenv-debug-x86_64.sh" \
  "conanrun.sh" \
  "deactivate_conanbuildenv-release-x86_64.sh" \
  "deactivate_conanbuildenv-debug-x86_64.sh" \
  "deactivate_conanbuild.sh" \
  "deactivate_conanrun.sh" \
  "graph.json" \
  "list.json" \
)

for file in "${files[@]}"; do
  echo "- Removing ${file}"
  rm -f "$file"
done


echo "- Removing conan-center-index (folder)"
rm -rf conan-center-index
