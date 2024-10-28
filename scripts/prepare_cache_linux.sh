#!/usr/bin/env bash
set -xe

# manylinux prep
# sometimes the epel server is down. retry 5 times
for i in $(seq 1 5); do 
    dnf install -y epel-release
    dnf install -y ccache && s=0 && break || s=$? && sleep 15;
done

[ $s -eq 0 ] || exit $s

if [[ -d "/usr/lib64/ccache" ]]; then
    ln -s /usr/bin/ccache /usr/lib64/ccache/c++
    ln -s /usr/bin/ccache /usr/lib64/ccache/cc
    ln -s /usr/bin/ccache /usr/lib64/ccache/gcc
    ln -s /usr/bin/ccache /usr/lib64/ccache/g++
    export PATH="/usr/lib64/ccache:$PATH"
elif [[ -d "/usr/lib/ccache" ]]; then
    ln -s /usr/bin/ccache /usr/lib/ccache/c++
    ln -s /usr/bin/ccache /usr/lib/ccache/cc
    ln -s /usr/bin/ccache /usr/lib/ccache/gcc
    ln -s /usr/bin/ccache /usr/lib/ccache/g++
    export PATH="/usr/lib/ccache:$PATH"
fi


# hack until https://github.com/pypa/cibuildwheel/issues/1030 is fixed
# Place ccache folder in /outputs
HOST_CCACHE_DIR="/host${HOST_CCACHE_DIR:-/home/runner/work/LuxCoreWheel/LuxCoreWheel/.ccache}"
if [ -d $HOST_CCACHE_DIR ]; then
    mkdir -p /output
    cp -R $HOST_CCACHE_DIR /output/.ccache
fi

ls -la /output/

ccache -o cache_dir="/output/.ccache"
ccache -o direct_mode="false"
# export CCACHE_DIR="/host/home/runner/work/klayout/klayout/.ccache"
ccache -M 5 G  # set cache size to 5 G

# Show ccache stats
echo "Cache stats:"
ccache -s
