# SPDX-FileCopyrightText: 2024 Howetuft
#
# SPDX-License-Identifier: Apache-2.0

# Debug linux build locally


# Script to run build locally for Linux.
# You need 'act' to be installed in your system

#export CIBW_DEBUG_KEEP_CONTAINER=TRUE
cd ..

zipfolder=/tmp/luxcore/1/cibw-wheels-ubuntu-latest-${python_minor}

act workflow_dispatch \
  --var conan_log_level=debug \
  --action-offline-mode \
  --job build-deps \
  -s GITHUB_TOKEN="$(gh auth token)" \
  --matrix os:ubuntu-latest \
  --artifact-server-path /tmp/pyluxcore \
  --rm \
  | tee /tmp/pyluxcore.log
  #&& unzip -o ${zipfolder}/cibw-wheels-ubuntu-latest-13.zip -d ${zipfolder}

