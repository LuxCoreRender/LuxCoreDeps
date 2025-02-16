# SPDX-FileCopyrightText: 2024 Howetuft
#
# SPDX-License-Identifier: Apache-2.0

import os
from sys import version_info as vi

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, replace_in_file





class BlenderTypesConan(ConanFile):
    name = "blender-types"
    version = "4.2.3"
    user = "luxcore"
    channel = "luxcore"
    # No settings/options are necessary, this is header only
    no_copy_source = True
    exports_sources = "include/*"  # for blender_types.h
    generators = "CMakeToolchain", "CMakeDeps"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "header-library"

    def source(self):
        get(
            self,
            f"https://github.com/blender/blender/archive/refs/tags/v{self.version}.zip",
            strip_root=True,
        )

    def _copy_includes(self, *folder):
        destination = os.path.join(self.package_folder, "include")
        root_dir = os.path.join(self.source_folder, *folder)
        files = [
            (dirpath, filename)
            for dirpath, _, filenames in os.walk(root_dir)
            for filename in filenames
            if filename.endswith(".h") or filename.endswith(".hh")
        ]
        for dirpath, filename in files:
            copied = copy(
                self,
                filename,
                src=dirpath,
                dst=destination,
                keep_path=False,
            )
            assert copied
            print(f"Copied: {copied}")

    def layout(self):
        cmake_layout(self)

    def package(self):

        # blender_types.h
        self._copy_includes("include")

        # Blender includes
        self._copy_includes("source", "blender")
        self._copy_includes("intern", "guardedalloc")


        destination = os.path.join(self.package_folder, "include")
        replace_in_file(
            self,
            os.path.join(destination, "DNA_defs.h"),
            "../blenlib/BLI_sys_types.h",
            "BLI_sys_types.h",
        )
        replace_in_file(
            self,
            os.path.join(destination, "MEM_guardedalloc.h"),
            "../../source/blender/blenlib/",
            "",
        )

    def package_info(self):
        # For header-only packages, libdirs and bindirs are not used
        # so it's necessary to set those as empty.
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "blender-types")
        self.cpp_info.set_property("cmake_target_name", "blender-types")
        self.cpp_info.set_property("pkg_config_name", "blender-types")

    def package_id(self):
        self.info.clear()  # Header-only
