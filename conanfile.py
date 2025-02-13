# SPDX-FileCopyrightText: 2024 Howetuft
#
# SPDX-License-Identifier: Apache-2.0

from conan import ConanFile

from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.system.package_manager import Brew, Yum
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, copy, rmdir, rename, rm, save

import os
import io
import shutil
from pathlib import Path

# Gather here the various dependency versions, for convenience
# (in alphabetic order)
BLENDER_VERSION = "4.2.3"
BOOST_VERSION = "1.84.0"
EIGEN_VERSION = "3.4.0"
EMBREE3_VERSION = "3.13.5"
FMT_VERSION = "11.0.2"
GLFW_VERSION = "3.4"
IMATH_VERSION = "3.1.9"
IMGUI_VERSION = "1.91.5"
JSON_VERSION = "3.11.3"
LIBDEFLATE_VERSION = "1.22"
LLVM_OPENMP_VERSION = "18.1.8"
MINIZIP_VERSION = "4.0.3"
NFD_VERSION = "1.2.1"
OCIO_VERSION = "2.4.0"
OIDN_VERSION = "2.3.1"
OIIO_VERSION = "2.5.16.0"
OPENEXR_VERSION = "3.3.2"
OIIO_VERSION = "2.5.18.0"
OPENSUBDIV_VERSION = "3.6.0"
OPENVDB_VERSION = "11.0.0"
PYBIND11_VERSION = "2.13.6"
ROBINHOOD_VERSION = "3.11.5"
SPDLOG_VERSION = "1.15.0"
TBB_VERSION = "2021.12.0"
WINFLEXBISON_VERSION = "2.5.25"


class LuxCore(ConanFile):
    name = "luxcoredeps"
    version = "2.10.0"
    user = "luxcore"
    channel = "luxcore"

    requires = [
        f"minizip-ng/{MINIZIP_VERSION}",
        f"boost/{BOOST_VERSION}",
        f"openvdb/{OPENVDB_VERSION}",
        f"embree3/{EMBREE3_VERSION}",
        f"blender-types/{BLENDER_VERSION}@luxcore/luxcore",
        f"oidn/{OIDN_VERSION}@luxcore/luxcore",
        f"opensubdiv/{OPENSUBDIV_VERSION}@luxcore/luxcore",
        f"imath/{IMATH_VERSION}",
        f"openimageio/{OIIO_VERSION}",
        f"nativefiledialog/{NFD_VERSION}@luxcore/luxcore",
        f"imgui/{IMGUI_VERSION}",
        f"glfw/{GLFW_VERSION}",
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


        # Header only - make them transitive
        self.requires(
            f"robin-hood-hashing/{ROBINHOOD_VERSION}", transitive_headers=True
        )
        self.requires(f"eigen/{EIGEN_VERSION}", transitive_headers=True)
        self.requires(f"nlohmann_json/{JSON_VERSION}", transitive_headers=True)
        self.requires(f"pybind11/{PYBIND11_VERSION}", transitive_headers=True)
        self.requires(f"spdlog/{SPDLOG_VERSION}", transitive_headers=True)

        if self.settings.os == "Macos":
            self.requires(f"llvm-openmp/{LLVM_OPENMP_VERSION}")

        if self.settings.os == "Windows":
            self.tool_requires(f"winflexbison/{WINFLEXBISON_VERSION}")

    def build_requirements(self):
        self.tool_requires("cmake/[*]")
        self.tool_requires("meson/[*]")
        self.tool_requires("pkgconf/[*]")
        self.tool_requires("yasm/[*]")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.absolute_paths = True
        tc.preprocessor_definitions["OIIO_STATIC_DEFINE"] = True
        tc.variables["CMAKE_COMPILE_WARNING_AS_ERROR"] = False

        # OIDN denoiser executable
        oidn_info = self.dependencies["oidn"].cpp_info
        oidn_bindir = Path(oidn_info.bindirs[0])
        if self.settings.os == "Windows":
            denoise_path = oidn_bindir / "oidnDenoise.exe"
        else:
            denoise_path = oidn_bindir / "oidnDenoise"
        tc.variables["LUX_OIDN_DENOISE_PATH"] = denoise_path.as_posix()

        # OIDN denoiser cpu (for Linux)
        oidn_libdir = Path(oidn_info.libdirs[0])
        tc.variables["LUX_OIDN_DENOISE_LIBS"] = oidn_libdir.as_posix()
        tc.variables["LUX_OIDN_DENOISE_BINS"] = oidn_bindir.as_posix()
        tc.variables["LUX_OIDN_VERSION"] = OIDN_VERSION
        if self.settings.os == "Linux":
            denoise_cpu = (
                oidn_libdir / f"libOpenImageDenoise_device_cpu.so.{OIDN_VERSION}"
            )
        elif self.settings.os == "Windows":
            denoise_cpu = oidn_bindir / "OpenImageDenoise_device_cpu.dll"
        elif self.settings.os == "Macos":
            denoise_cpu = (
                oidn_libdir / f"OpenImageDenoise_device_cpu.{OIDN_VERSION}.pylib"
            )
        tc.variables["LUX_OIDN_DENOISE_CPU"] = denoise_cpu.as_posix()

        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            tc.cache_variables["CMAKE_OSX_ARCHITECTURES"] = "arm64"

        if self.settings.os == "Macos":
            buildenv = VirtualBuildEnv(self)

            bisonbrewpath = io.StringIO()
            self.run("brew --prefix bison", stdout=bisonbrewpath)
            bison_root = os.path.join(bisonbrewpath.getvalue().rstrip(), "bin")
            buildenv.environment().define("BISON_ROOT", bison_root)

            flexbrewpath = io.StringIO()
            self.run("brew --prefix flex", stdout=flexbrewpath)
            flex_root = os.path.join(flexbrewpath.getvalue().rstrip(), "bin")
            buildenv.environment().define("FLEX_ROOT", flex_root)

            buildenv.generate()
            tc.presets_build_environment = buildenv.environment()

        tc.cache_variables["SPDLOG_FMT_EXTERNAL_HO"] = True

        tc.generate()

        cd = CMakeDeps(self)

        cd.generate()

    def package(self):
        # Just to ensure package is not empty
        save(self, os.path.join(self.package_folder, "dummy.txt"), "Hello World")

    def layout(self):
        self.folders.root = ""
        self.folders.generators = "cmake"
        self.folders.build = "build"

    def package_info(self):

        if self.settings.os == "Linux":
            self.cpp_info.libs = ["pyluxcore"]
        elif self.settings.os == "Windows":
            self.cpp_info.libs = [
                "pyluxcore.pyd",
                "tbb12.dll",  # TODO
            ]
