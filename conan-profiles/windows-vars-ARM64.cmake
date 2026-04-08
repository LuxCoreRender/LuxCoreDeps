# This file injects SIMD options for Embree on ARM64
# Better choose only one architecture (and synchronize /arch cxx flag, see profile)
set(EMBREE_ISA_NEON ON CACHE BOOL "")
set(EMBREE_MAX_ISA "NEON" CACHE STRING "")
set(EMBREE_TUTORIALS OFF CACHE BOOL "")