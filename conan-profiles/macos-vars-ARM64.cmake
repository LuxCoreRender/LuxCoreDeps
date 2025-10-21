# This file injects CMake variables in MacOS build
# 14.2 is required by opensubdiv for metal
set(CMAKE_OSX_DEPLOYMENT_TARGET "14.2" CACHE STRING "")
