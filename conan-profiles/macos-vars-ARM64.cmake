# This file injects CMake variables in MacOS ARM build
# 14.2 is required by opensubdiv for metal
MESSAGE(STATUS "Injecting Conan CMake variables")
set(CMAKE_OSX_DEPLOYMENT_TARGET "14.2")
set(MACOS_VERSION_MIN "14.2")

# Set tools
set(CMAKE_AR "$ENV{AR}")
set(CMAKE_RANLIB "$ENV{RANLIB}")
set(LINKER_FLAGS
  "-Wl,-flat_namespace -Wl,-export_dynamic -Wl,-headerpad_max_install_names"
)
set (CMAKE_SHARED_LINKER_FLAGS ${LINKER_FLAGS})
set(CMAKE_VERBOSE_MAKEFILE ON)


# Some checks
include(CMakePrintHelpers)
cmake_print_variables(
  CMAKE_HOST_APPLE
)
