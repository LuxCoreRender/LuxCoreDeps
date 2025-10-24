# This file injects CMake variables in MacOS ARM build
# 14.2 is required by opensubdiv for metal
MESSAGE(STATUS "Injecting Conan CMake variables")
set(CMAKE_OSX_DEPLOYMENT_TARGET "14.2" CACHE STRING "" FORCE)
set(CMAKE_SYSTEM_PROCESSOR arm)

set(MACOS_VERSION_MIN "14.2" CACHE STRING "" FORCE)
