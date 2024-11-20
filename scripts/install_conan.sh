# SPDX-FileCopyrightText: 2024 Howetuft
#
# SPDX-License-Identifier: Apache-2.0

set -o pipefail
if [[ $RUNNER_OS == "Linux" ]]; then
  cache_dir=/conan_cache
else
  cache_dir=$WORKSPACE/conan_cache
fi

echo "::group::CIBW_BEFORE_BUILD: pip"
pip install conan
pip install ninja
if [[ $PYTHON_MINOR == "8" ]]; then
  pip install "numpy < 2" &
else
  pip install "numpy >= 2" &
fi
echo "::endgroup::"

echo "::group::CIBW_BEFORE_BUILD: conan cache"
ls $cache_dir
conan cache restore -vverbose $cache_dir/conan_cache_save.tgz
echo "::endgroup::"

conan_path=$WORKSPACE/deps/conan

echo "::group::CIBW_BEFORE_BUILD: Boost Python"
boost_python=$conan_path/boost-python
conan editable add ${boost_python}
conan source ${boost_python} &
echo "::endgroup::"

echo "::group::CIBW_BEFORE_BUILD: OIIO"
unset CI  # Otherwise OIIO passes -Werror to compiler (MacOS)!
oiio=$conan_path/openimageio
conan editable add ${oiio}
conan source ${oiio} &
echo "::endgroup::"

echo "::group::CIBW_BEFORE_BUILD: OIDN"
oidn=$conan_path/oidn_${RUNNER_OS}_${RUNNER_ARCH}
conan editable add ${oidn}
conan source ${oidn} &
echo "::endgroup::"


if [[ $RUNNER_OS == "macOS" && $RUNNER_ARCH == "ARM64" ]]; then
    echo "CIBW_BEFORE_BUILD: EMBREE3"
    embree3=$conan_path/embree3
    conan editable add ${embree3}
    conan source ${embree3} &
fi

wait

echo "::group::CIBW_BEFORE_BUILD: LuxCore"
conan editable add $WORKSPACE --name=LuxCoreWheels --version=2.6.0 --user=LuxCoreWheels --channel=LuxCoreWheels
conan install \
  --requires=LuxCoreWheels/2.6.0@LuxCoreWheels/LuxCoreWheels \
  --profile:all=$WORKSPACE/conan_profiles/conan_profile_${RUNNER_OS}_${RUNNER_ARCH} \
  --build=editable \
  --build=missing \
  --deployer=runtime_deploy \
  --deployer-folder=$WORKSPACE/libs \
  -s build_type=Release
echo "::endgroup::"

echo "::group::Installing oidn"
if [[ $RUNNER_OS == "Linux" ]]; then
    oidn_version=2.3.0
    cp -rv $oidn/oidn-${oidn_version}.x86_64.linux/bin/. $WORKSPACE/libs/
    cp -rv $oidn/oidn-${oidn_version}.x86_64.linux/lib/. $WORKSPACE/libs/
    cp -rv $oidn/oneapi-tbb-2021.12.0/lib/intel64/gcc4.8/. $WORKSPACE/libs/
elif [[ $RUNNER_OS == "Windows" ]]; then
    oidn_version=2.3.0
    cp -rv $oidn/oidn-${oidn_version}.x64.windows/bin/. $WORKSPACE/libs/
elif [[ $RUNNER_OS == "macOS" && $RUNNER_ARCH == "X64" ]]; then
    oidn_version=2.3.0
    cp -rv $oidn/oidn-${oidn_version}.x86_64.macos/bin/. $WORKSPACE/libs/
    cp -rv $oidn/oidn-${oidn_version}.x86_64.macos/lib/. $WORKSPACE/libs/
elif [[ $RUNNER_OS == "macOS" && $RUNNER_ARCH == "ARM64" ]]; then
      oidn_version=2.3.0
      cp -rv $oidn/oidn-${oidn_version}.arm64.macos/bin/. $WORKSPACE/libs/
      cp -rv $oidn/oidn-${oidn_version}.arm64.macos/lib/. $WORKSPACE/libs/
else
      echo "ERROR: unhandled runner os/arch '${RUNNER_OS}/${RUNNER_ARCH}'"
      exit 64
fi
echo "::endgroup::"

echo "::group::Saving dependencies in ${cache_dir}"
conan cache save -vverbose --file $cache_dir/conan_cache_save.tgz "*/*:*"
ls $cache_dir  # Check
echo "::endgroup::"
