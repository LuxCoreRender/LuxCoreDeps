#!/bin/bash

# Tip: to clean before running, you can issue a `conan remove "*" -c`
# Warning: this command will totally erase your cache
# You may also want to clean /tmp/conan-cache, to avoid reinjection of previous
# builds in the current one

# Specialized for Linux, but could be changed
export RUNNER_OS=Linux
export RUNNER_ARCH=X64


export LUXDEPS_VERSION=test
export GCC_VERSION=14   # Note: even for gcc > 14
export WORKSPACE=.
export CXX_VERSION=20
export CMAKE_POLICY_VERSION_MINIMUM=3.25
export DEPS_BUILD_TYPE=Debug  # Or Release/RelWithDebInfo/MinSizeRel, as needed
export cache_dir

# Run conan
export CMAKE_BUILD_PARALLEL_LEVEL=
source run-conan.sh 2>&1 | tee /tmp/run-conan.log

# Zip file
cd /tmp/conan-cache
zip -1 luxcoredeps.zip conan-cache-save.tgz build-info.json
