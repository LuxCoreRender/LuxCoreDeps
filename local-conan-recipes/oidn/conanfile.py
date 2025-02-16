# SPDX-FileCopyrightText: 2024 Howetuft
#
# SPDX-License-Identifier: Apache-2.0

import os
import shutil
from pathlib import Path
from conan.tools.files import get, copy, rmdir, rename, rm, replace_in_file
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan import ConanFile
from conan.tools.scm import Git

# Gather here the various dependency versions, for convenience
TBB_VERSION = "2021.12.0"

class OidnConan(ConanFile):
    name = "oidn"
    version = "2.3.1"
    user = "luxcore"
    channel = "luxcore"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_device_cpu": [True, False],
        "with_device_sycl": [True, False],
        "with_device_sycl_aot": [True, False],
        "with_device_cuda": [True, False],
        "device_cuda_api": ["Driver", "RuntimeStatic", "RuntimeShared"],
        "with_device_hip": [True, False],
        "with_device_metal": [True, False],
        "with_filter_rt": [True, False],
        "with_filter_rtlightmap": [True, False],
        "with_apps": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_device_cpu": True,
        "with_device_sycl": False,
        "with_device_sycl_aot": True,
        "with_device_cuda": False,
        "device_cuda_api": "Driver",
        "with_device_hip": False,
        "with_device_metal": False,
        "with_filter_rt": True,
        "with_filter_rtlightmap": True,
        "with_apps": True,
    }

    def requirements(self):
        self.requires(f"onetbb/{TBB_VERSION}")

    def source(self):
        git = Git(self)
        res = git.run("lfs install")
        print(res)
        git.clone(
            "https://github.com/OpenImageDenoise/oidn.git",
            args=["--recursive", f"--branch v{self.version}"],
            target=Path(self.source_folder) / "oidn"
        )


    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OIDN_STATIC_LIB"] = not self.options.shared

        tc.variables["OIDN_DEVICE_CPU"] = self.options.with_device_cpu
        tc.variables["OIDN_DEVICE_SYCL"] = self.options.with_device_sycl
        tc.variables["OIDN_DEVICE_SYCL_AOT"] = self.options.with_device_sycl_aot
        tc.variables["OIDN_DEVICE_CUDA"] = self.options.with_device_cuda
        tc.variables["OIDN_DEVICE_CUDA_API"] = self.options.device_cuda_api
        tc.variables["OIDN_DEVICE_HIP"] = self.options.with_device_hip
        tc.variables["OIDN_DEVICE_METAL"] = self.options.with_device_metal
        tc.variables["OIDN_FILTER_RT"] = self.options.with_filter_rt
        tc.variables["OIDN_FILTER_RTLIGHTMAP"] = self.options.with_filter_rtlightmap
        tc.variables["OIDN_APPS"] = self.options.with_apps
        if self.settings.os == "Linux":
            tc.cache_variables["CMAKE_SKIP_RPATH"] = True
            tc.cache_variables["CMAKE_INSTALL_RPATH"] = "\\\\\${ORIGIN}/."
        if self.settings.os == "Macos":
            tc.cache_variables["CMAKE_SKIP_RPATH"] = True
            tc.cache_variables["CMAKE_INSTALL_RPATH"] = "\\\\\${ORIGIN}/."
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(cli_args=[], build_script_folder=Path(self.folders.source) / "oidn")
        cmake.build(cli_args=["--verbose", "--clean-first"])

    def package(self):
        copy(
            self,
            "LICENSE.txt",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        if self.options.shared:
            # Shared
            if self.settings.os == "Linux":
                self.cpp_info.libs = [
                    "OpenImageDenoise",
                    f"libOpenImageDenoise_core.so.{self.version}",
                ]
            elif self.settings.os == "Windows":
                self.cpp_info.libs = [
                    "OpenImageDenoise",
                    "OpenImageDenoise_core",
                ]
            elif self.settings.os == "Macos":
                self.cpp_info.libs = [
                    f"OpenImageDenoise.{self.version}",
                    f"OpenImageDenoise_device_cpu.{self.version}",
                    f"OpenImageDenoise_core.{self.version}",
                ]
        else:
            # Static
            # Warning: library order matters!
            self.cpp_info.libs = [
                "OpenImageDenoise",
                "OpenImageDenoise_device_cpu",
                "OpenImageDenoise_core",
            ]
