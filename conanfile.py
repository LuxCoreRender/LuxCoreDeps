# SPDX-FileCopyrightText: 2024 Howetuft
#
# SPDX-License-Identifier: Apache-2.0

from conan import ConanFile

from conan.tools.cmake import CMakeDeps, CMakeToolchain
from conan.tools.files import save

import os

# Gather here the various dependency versions, for convenience
# (in alphabetic order)
BLENDER_VERSION = "4.2.3"
BOOST_VERSION = "1.84.0"
EIGEN_VERSION = "3.4.0"
EMBREE3_VERSION = "3.13.5"
FMT_VERSION = "11.0.2"
GLFW_VERSION = "3.4"
IMATH_VERSION = "3.1.9"
IMGUI_VERSION = "1.91.8"
IMGUIFILEDIALOG_VERSION = "0.6.7"
JSON_VERSION = "3.11.3"
LIBDEFLATE_VERSION = "1.22"
LLVM_OPENMP_VERSION = "17.0.6"
MINIZIP_VERSION = "4.0.3"
NINJA_VERSION = "1.12.1"
NVRTC_VERSION = "12.8.61"
OCIO_VERSION = "2.4.2"
OIDN_VERSION = "2.3.1"
OIIO_VERSION = "2.5.16.0"
OPENEXR_VERSION = "3.3.3"
OIIO_VERSION = "2.5.18.0"
OPENSUBDIV_VERSION = "3.6.0"
OPENVDB_VERSION = "11.0.0"
PYBIND11_VERSION = "2.13.6"
ROBINHOOD_VERSION = "3.11.5"
SPDLOG_VERSION = "1.15.0"
TBB_VERSION = "2021.12.0"
ZSTD_VERSION = "1.5.7"



class LuxCoreDeps(ConanFile):
    name = "luxcoredeps"
    # Version should be set by `conan install`
    user = "luxcore"
    channel = "luxcore"

    requires = [
        f"minizip-ng/{MINIZIP_VERSION}",
        f"boost/{BOOST_VERSION}",
        f"openvdb/{OPENVDB_VERSION}",
        f"embree3/{EMBREE3_VERSION}",
        f"oidn/{OIDN_VERSION}@luxcore/luxcore",
        f"opensubdiv/{OPENSUBDIV_VERSION}@luxcore/luxcore",
        f"imath/{IMATH_VERSION}",
        f"openimageio/{OIIO_VERSION}",
        f"imgui/{IMGUI_VERSION}",
        f"glfw/{GLFW_VERSION}",
        f"imguifiledialog/{IMGUIFILEDIALOG_VERSION}@luxcore/luxcore",
    ]

    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires(
            f"onetbb/{TBB_VERSION}",
            override=True,
            libs=True,
            transitive_libs=True,
        )  # For oidn
        self.requires(
            f"libdeflate/{LIBDEFLATE_VERSION}",
            force=True,
            libs=True,
            transitive_libs=True,
        )
        self.requires(
            f"zstd/{ZSTD_VERSION}",
            override=True,
            libs=True,
            transitive_libs=True,
        )
        self.requires(
            f"opencolorio/{OCIO_VERSION}",
            force=True,
        )
        self.requires(
            f"openexr/{OPENEXR_VERSION}",
            force=True,
        )
        self.requires(
            f"fmt/{FMT_VERSION}@luxcore/luxcore",
            force=True,
            transitive_headers=True,
        )

        # Header only deps - make them transitive
        self.requires(
            f"robin-hood-hashing/{ROBINHOOD_VERSION}", transitive_headers=True
        )
        self.requires(f"eigen/{EIGEN_VERSION}", transitive_headers=True)
        self.requires(f"nlohmann_json/{JSON_VERSION}", transitive_headers=True)
        self.requires(f"pybind11/{PYBIND11_VERSION}", transitive_headers=True)
        self.requires(f"spdlog/{SPDLOG_VERSION}", transitive_headers=True)
        self.requires(
            f"blender-types/{BLENDER_VERSION}@luxcore/luxcore",
            transitive_headers=True,
        )

        # Macos OpenMP
        if self.settings.os == "Macos":
            self.requires(f"llvm-openmp/{LLVM_OPENMP_VERSION}")

        # nvrtc
        if self.settings.os in ("Linux", "Windows"):
            self.requires(f"nvrtc/{NVRTC_VERSION}@luxcore/luxcore")

        # LuxCore build requirements
        # As they are build requirements for LuxCore, they must be full
        # requirements for LuxCoreDeps (otherwise it won't get saved in cache)

        # Bison/flex (Luxcore build requirement)
        if self.settings.os == "Windows":
            self.requires("winflexbison/[*]", build=False, run=True, visible=True)
        else:
            self.requires("bison/[*]", build=False, run=True, visible=True)
            self.requires("flex/[*]", build=False, run=True, visible=True)

        # Ninja (Luxcore build requirement)
        self.requires(f"ninja/[*]", build=False, run=True, visible=True)

        # Doxygen (Luxcore build requirement)
        self.requires(f"doxygen/1.13.2", build=False, run=True, visible=True)
        self.requires(f"xapian-core/1.4.19", build=False, run=False, visible=True)
        self.requires(f"libiconv/1.17", build=False, run=False, visible=True)

    def build_requirements(self):
        # LuxCoreDeps build requirements
        self.tool_requires("cmake/[*]")
        self.tool_requires("meson/[*]")
        self.tool_requires("pkgconf/[*]")
        self.tool_requires("yasm/[*]")

    def generate(self):
        tc = CMakeToolchain(self)

        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            tc.cache_variables["CMAKE_OSX_ARCHITECTURES"] = "arm64"

        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

    def package(self):
        # Just to ensure package is not empty
        save(self, os.path.join(self.package_folder, "dummy.txt"), "Hello World")
