# This file injects CMake variables in MacOS ARM build
# 14.2 is required by opensubdiv for metal
MESSAGE(STATUS "Injecting Conan CMake variables")
set(CMAKE_OSX_DEPLOYMENT_TARGET "14.2")
set(MACOS_VERSION_MIN "14.2")

# Set tools
set(CMAKE_VERBOSE_MAKEFILE ON)


# Some checks
include(CMakePrintHelpers)
cmake_print_variables(
  CMAKE_HOST_APPLE
)
