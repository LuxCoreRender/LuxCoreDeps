# SPDX-FileCopyrightText: 2024 Howetuft
#
# SPDX-License-Identifier: Apache-2.0

# This is the main script. It installs build tools, retrieve local recipes and
# remote recipes, build everything and make the dependency cache.

# Caveat!
# LUXDEPS_VERSION, RUNNER_OS, RUNNER_ARCH are expected to be set by caller beforehand
#
die() { rc=$?; (( $# )) && printf '::error::%s\n' "$*" >&2; exit $(( rc == 0 ? 1 : rc )); }
test -n "$LUXDEPS_VERSION" || die "LUXDEPS_VERSION not set"
test -n "$RUNNER_OS" || die "RUNNER_OS not set"
test -n "$RUNNER_ARCH" || die "RUNNER_ARCH not set"

CONAN_PROFILE=conan-profile-${RUNNER_OS}-${RUNNER_ARCH}

# Debug utility (install a specific package)
function debug() {
  conan install \
    --requires=$1 \
    --profile:all=$CONAN_PROFILE \
    --version=$LUXDEPS_VERSION \
    --remote=mycenter \
    --remote=mylocal \
    --build=missing;
}

# Script starts here

# 0. Initialize: set globals and install conan and ninja
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

# 1. Clone conancenter at a specific commit and add this cloned repo as a
# remote ('mycenter')
# This has 2 benefits:
# - We can decide which packages will be built from sources (remote=mycenter)
#   and which ones will use precompiled binaries (remote=conancenter)
# - We pin the index to a specific state (commit), which avoids spurious
#   updates
# https://docs.conan.io/2/devops/devops_local_recipes_index.html
echo "::group::CIBW_BEFORE_BUILD: local recipes index repository"
git clone https://github.com/conan-io/conan-center-index
cd conan-center-index
git reset --hard 73bae27b468ae37f5bacd4991d1113aefcf23b2b
git clean -df  # cleans any untracked files/folders
cd ..
conan remote add mycenter ./conan-center-index

# 2. Add local recipe repository (as a remote)
conan remote add mylocal ./conan-local-recipes
conan list -r mylocal
echo "::endgroup::"

if [[ "$RUNNER_OS" == "Linux" ]]; then
  # ispc
  echo "::group::CIBW_BEFORE_BUILD: ispc"
  source /opt/intel/oneapi/ispc/latest/env/vars.sh
  echo "::endgroup::"
fi

# 3. Restore conan cache (add -vverbose to debug)
echo "::group::CIBW_BEFORE_BUILD: restore conan cache"
cachefile=$cache_dir/conan-cache-save.tgz
if [[ -e $cachefile ]]; then
  conan cache restore $cachefile
else
  echo "::warning::No cache file $cachefile"
fi
echo "::endgroup::"

# 4. Install profiles
echo "::group::CIBW_BEFORE_BUILD: Install profiles"
conan create $WORKSPACE/conan-profiles \
  --profile:all=$WORKSPACE/conan-profiles/$CONAN_PROFILE \
  --version=$LUXDEPS_VERSION
conan config install-pkg -vvv luxcoreconf/$LUXDEPS_VERSION@luxcore/luxcore
echo "::endgroup::"

# 5. Install build requirements
echo "::group::CIBW_BEFORE_BUILD: Install tool requirements"
# We specify conancenter as a remote, thus allowing to use precompiled
# binaries.
# For pkgconf and meson, we have to manually target the right version
build_deps=(b2/[*] cmake/[*] m4/[*] pkgconf/2.1.0 meson/1.2.2 yasm/[*])
if [[ $RUNNER_OS == "Windows" ]]; then
  build_deps+=(msys2/[*])
fi
for d in "${build_deps[@]}"; do
  conan install \
    --tool-requires=${d} \
    --profile:all=$CONAN_PROFILE \
    --build=missing \
    --remote=conancenter \
    --build=b2/*
done
echo "::endgroup::"

if [[ $RUNNER_OS == "Windows" ]]; then
  DEPLOY_PATH=$(cygpath "C:\\Users\\runneradmin")
else
  DEPLOY_PATH=$WORKSPACE
fi

# 6. Show graph (for debug purpose)
echo "::group::CIBW_BEFORE_BUILD: Explain graph"
# This is only for debugging purpose...
cd $WORKSPACE
conan graph info $WORKSPACE \
  --profile:all=$CONAN_PROFILE \
  --version=$LUXDEPS_VERSION \
  --remote=mycenter \
  --remote=mylocal \
  --build=missing \
  --format=dot
echo "::endgroup::"

# (Debug) Install particular package, for debugging
debug embree


# 7. Create luxcoredeps package and all dependencies
# (we do not specify conancenter as a remote, so it prevents conan from using
# precompiled binaries and it forces compilation)
echo "::group::CIBW_BEFORE_BUILD: Create LuxCore Deps"
cd $WORKSPACE
conan create $WORKSPACE \
  --profile:all=$CONAN_PROFILE \
  --version=$LUXDEPS_VERSION \
  --remote=mycenter \
  --remote=mylocal \
  --build=missing
echo "::endgroup::"

# 8. Save result
echo "::group::Saving dependencies in ${cache_dir}"
conan cache clean "*"  # Clean non essential files
conan remove -c -vverbose "*/*#!latest"  # Keep only latest version of each package
# Save only dependencies of current target (otherwise cache gets bloated)
conan graph info \
  --requires=luxcoredeps/$LUXDEPS_VERSION@luxcore/luxcore \
  --requires=luxcoreconf/$LUXDEPS_VERSION@luxcore/luxcore \
  --format=json \
  --remote=mycenter \
  --remote=mylocal \
  --profile:all=$CONAN_PROFILE \
  > graph.json
conan list --graph=graph.json --format=json --graph-binaries=Cache > list.json
conan cache save -vverbose --file=${cache_dir}/conan-cache-save.tgz --list=list.json
ls $cache_dir
echo "::endgroup::"
