# SPDX-FileCopyrightText: 2024 Howetuft
#
# SPDX-License-Identifier: Apache-2.0

# Caveat!
# LUXDEPS_VERSION, RUNNER_OS, RUNNER_ARCH must be set by caller
#
die() { rc=$?; (( $# )) && printf '::error::%s\n' "$*" >&2; exit $(( rc == 0 ? 1 : rc )); }
test -n "$LUXDEPS_VERSION" || die "LUXDEPS_VERSION not set"
test -n "$RUNNER_OS" || die "RUNNER_OS not set"
test -n "$RUNNER_ARCH" || die "RUNNER_ARCH not set"

CONAN_PROFILE=conan-profile-${RUNNER_OS}-${RUNNER_ARCH}

function conan_local_install() {
  name=$(echo "$1" | tr '[:upper:]' '[:lower:]')  # Package name in lowercase

  conan create \
    --profile:all=$CONAN_PROFILE \
    --build=missing \
    --remote=mycenter \
    -vnotice \
    $WORKSPACE/local-conan-recipes/$name
  conan install \
    --profile:all=$CONAN_PROFILE \
    --build=missing \
    --remote=mycenter \
    -vnotice \
    $WORKSPACE/local-conan-recipes/$name
}


# Script starts here

set -euxo pipefail

if [[ "$RUNNER_OS" == "Linux" ]]; then
  cache_dir=/conan-cache
else
  cache_dir=$WORKSPACE/conan-cache
fi

echo "::group::CIBW_BEFORE_BUILD: pip"
pip install conan
pip install ninja
echo "::endgroup::"

# https://docs.conan.io/2/devops/devops_local_recipes_index.html
# Add the mycenter remote pointing to the local folder
# This allows to decide which packages are built from sources (remote=mycenter)
# and which ones use precompiled binaries (remote=conancenter)
echo "::group::CIBW_BEFORE_BUILD: local recipes index repository"
git clone https://github.com/conan-io/conan-center-index
conan remote add mycenter ./conan-center-index
echo "::endgroup::"

if [[ "$RUNNER_OS" == "Linux" ]]; then
  # ispc
  echo "::group::CIBW_BEFORE_BUILD: ispc"
  source /opt/intel/oneapi/ispc/latest/env/vars.sh
  echo "::endgroup::"
fi

echo "::group::CIBW_BEFORE_BUILD: restore conan cache"
# Restore conan cache (add -vverbose to debug)
cachefile=$cache_dir/conan-cache-save.tgz
if [[ -e $cachefile ]]; then
  conan cache restore $cachefile
else
  echo "::warning::No cache file $cachefile"
fi
echo "::endgroup::"

# Install profiles
echo "::group::CIBW_BEFORE_BUILD: profiles"
conan create $WORKSPACE/conan-profiles \
  --profile:all=$WORKSPACE/conan-profiles/$CONAN_PROFILE \
  --version=$LUXDEPS_VERSION
conan config install-pkg -vvv luxcoreconf/$LUXDEPS_VERSION@luxcore/luxcore
echo "::endgroup::"

# Install local packages
if [[ "$RUNNER_OS" == "Linux" || "$RUNNER_OS" == "Windows" ]]; then
  echo "::group::CIBW_BEFORE_BUILD: nvrtc"
  conan_local_install nvrtc
  echo "::endgroup::"
fi

echo "::group::CIBW_BEFORE_BUILD: imguifiledialog"
conan_local_install imguifiledialog
echo "::endgroup::"

echo "::group::CIBW_BEFORE_BUILD: fmt"
conan_local_install fmt
echo "::endgroup::"

echo "::group::CIBW_BEFORE_BUILD: opensubdiv"
conan_local_install opensubdiv
echo "::endgroup::"

echo "::group::CIBW_BEFORE_BUILD: OIDN"
conan_local_install oidn
echo "::endgroup::"

echo "::group::CIBW_BEFORE_BUILD: Blender types"
conan_local_install blender-types
echo "::endgroup::"

if [[ $RUNNER_OS == "Windows" ]]; then
  DEPLOY_PATH=$(cygpath "C:\\Users\\runneradmin")
else
  DEPLOY_PATH=$WORKSPACE
fi

echo "::group::CIBW_BEFORE_BUILD: Install tool requirements"
# We allow to use precompiled binaries
build_deps=(b2 cmake m4 meson pkgconf yasm)
if [[ $RUNNER_OS == "Windows" ]]; then
  build_deps+=(msys2)
fi
for d in "${build_deps[@]}"; do
  conan install \
    --tool-requires=${d}/[*] \
    --profile:all=$CONAN_PROFILE \
    --build=missing \
    --remote=conancenter \
    --build=b2/*
done
echo "::endgroup::"

echo "::group::CIBW_BEFORE_BUILD: Create LuxCore Deps"
cd $WORKSPACE
# Create package (without using conancenter precompiled binaries)
conan create $WORKSPACE \
  --profile:all=$CONAN_PROFILE \
  --version=$LUXDEPS_VERSION \
  --remote=mycenter \
  --build=missing
echo "::endgroup::"

echo "::group::Saving dependencies in ${cache_dir}"
conan cache clean "*"  # Clean non essential files
conan remove -c -vverbose "*/*#!latest"  # Keep only latest version of each package
# Save only dependencies of current target (otherwise cache gets bloated)
conan graph info \
  --requires=luxcoredeps/$LUXDEPS_VERSION@luxcore/luxcore \
  --requires=luxcoreconf/$LUXDEPS_VERSION@luxcore/luxcore \
  --format=json \
  --remote=mycenter \
  --profile:all=$CONAN_PROFILE \
  > graph.json
conan list --graph=graph.json --format=json --graph-binaries=Cache > list.json
conan cache save -vverbose --file=$cache_dir/conan-cache-save.tgz --list=list.json
echo "::endgroup::"
