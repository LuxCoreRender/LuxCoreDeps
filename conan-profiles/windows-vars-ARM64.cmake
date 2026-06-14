# ARM architecture flags for Embree
# Compiler (clang-cl) is handled by conan-profile-Windows-ARM64-clang
# via tools.build:compiler_executables

set(EMBREE_ARM ON CACHE BOOL "Enable ARM architecture support")
set(EMBREE_ISA_NEON ON CACHE BOOL "Enable NEON instructions")
set(EMBREE_MAX_ISA "NEON" CACHE STRING "Set maximum ISA to NEON")
set(EMBREE_TUTORIALS OFF CACHE BOOL "Disable tutorials")
set(EMBREE_SYCL_SUPPORT OFF CACHE BOOL "Disable SYCL/DPCPP support")
set(COMPILER_HAS_SYCL_SUPPORT OFF CACHE BOOL "disable SYCL feature test")

set(EMBREE_ISA_SSE2 OFF CACHE BOOL "" FORCE)
set(EMBREE_ISA_SSE42 OFF CACHE BOOL "" FORCE)
set(EMBREE_ISA_AVX OFF CACHE BOOL "" FORCE)
set(EMBREE_ISA_AVX2 OFF CACHE BOOL "" FORCE)
set(EMBREE_ISA_AVX512 OFF CACHE BOOL "" FORCE)