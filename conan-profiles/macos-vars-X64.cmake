# This file injects CMake variables in MacOS build
MESSAGE(STATUS "Injecting Conan CMake variables")
set(CMAKE_OSX_DEPLOYMENT_TARGET "11.0")
set(MACOS_VERSION_MIN "11.0")

# Set tools
#set(CMAKE_AR "$ENV{AR}")
#set(CMAKE_RANLIB "$ENV{RANLIB}")
#set(LINKER_FLAGS
  #"-Wl,-flat_namespace -Wl,-export_dynamic -Wl,-headerpad_max_install_names"
#)
#set (CMAKE_SHARED_LINKER_FLAGS ${LINKER_FLAGS})

# Some checks
include(CMakePrintHelpers)
cmake_print_variables(
  CMAKE_HOST_APPLE
)
