#!/bin/bash

# Tip: to clean before running, you can issue a `conan remove "*" -c`
# Warning: this command will totally erase your cache
# You may also want to clean /tmp/conan-cache, to avoid reinjection of previous
# builds in the current one

# Run conan
export CMAKE_BUILD_PARALLEL_LEVEL=
source run-conan.sh 2>&1 | tee /tmp/run-conan.log

# Zip file
cd /tmp/conan-cache
zip -1 luxcoredeps.zip conan-cache-save.tgz build-info.json
