# This file injects SIMD options for Embree
# Better choose only one architecture (and synchronize /arch cxx flag, see profile)
#set(EMBREE_ISA_SSE2 ON CACHE BOOL "")
#set(EMBREE_ISA_SSE42 ON CACHE BOOL "")
#set(EMBREE_ISA_AVX ON CACHE BOOL "")
#set(EMBREE_ISA_AVX2 ON CACHE BOOL "")
#set(EMBREE_ISA_AVX512 OFF CACHE BOOL "")
set(EMBREE_MAX_ISA "AVX2" CACHE STRING "")
set(EMBREE_TUTORIALS OFF CACHE BOOL "")
