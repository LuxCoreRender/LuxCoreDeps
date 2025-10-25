# This file injects CMake variables in MacOS build
set(CMAKE_OSX_DEPLOYMENT_TARGET "11.0" CACHE STRING "" FORCE)
set(MACOS_VERSION_MIN "11.0" CACHE STRING "" FORCE)

# Set tools
set(CMAKE_AR "$ENV{AR}")
set(CMAKE_RANLIB "$ENV{RANLIB}")

# Some checks
include(CMakePrintHelpers)
cmake_print_variables(
  CMAKE_HOST_APPLE
)
