# SPDX-FileCopyrightText: 2024 Howetuft
#
# SPDX-License-Identifier: Apache-2.0

# Debug linux build locally


# Script to run build locally for Linux.
# You need 'act' to be installed in your system

#export CIBW_DEBUG_KEEP_CONTAINER=TRUE

zipfolder=/tmp/luxcore/1/cibw-wheels-ubuntu-latest-${python_minor}

act workflow_call \
  --var conan_log_level=debug \
  --input luxdeps-version=test \
  --input rebuild-all=true \
  --action-offline-mode \
  --workflows ./.github/workflows/build.yml \
  --job build-deps \
  -s GITHUB_TOKEN="$(gh auth token)" \
  --matrix os:ubuntu-latest \
  --artifact-server-path /tmp/pyluxcore \
  --rm \
  | tee /tmp/pyluxcore.log
  #&& unzip -o ${zipfolder}/cibw-wheels-ubuntu-latest-13.zip -d ${zipfolder}

