# SPDX-FileCopyrightText: 2024 Howetuft
#
# SPDX-License-Identifier: Apache-2.0

import os
from conan import ConanFile
from conan.tools.files import copy, rmdir


class EmbreeConan(ConanFile):
    name = "embree"
    version = "4.4.0"
    license = "Apache-2.0"
    url = "https://github.com/embree/embree"
    description = "Intel Embree ray tracing kernels."
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
    }
    exports_sources = "prebuilt/**"

    def layout(self):
        pass

    def build(self):
        # This recipe consumes prebuilt binaries, so there is no build step.
        pass

    def package(self):
        prebuilt_dir = os.path.join(self.source_folder, "prebuilt")
        copy(self, "**", src=prebuilt_dir, dst=self.package_folder)
        # Remove any accidental packaged CMake helper files.
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "embree")
        self.cpp_info.set_property("cmake_target_name", "embree::embree")
        self.cpp_info.libs = ["embree4"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.bindirs = ["bin"]
