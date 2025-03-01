# SPDX-FileCopyrightText: 2024 Howetuft
#
# SPDX-License-Identifier: Apache-2.0

from conan import ConanFile

from conan.tools.cmake import CMakeDeps, CMakeToolchain, cmake_layout, CMake
from conan.tools.files import save
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, load, rmdir, rm
import os

class ImguiFileDialogConan(ConanFile):
    name = "imguifiledialog"
    user = "luxcore"
    channel = "luxcore"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    homepage = "https://github.com/aiekick/ImGuiFileDialog"
    license = "MIT"
    version = "0.6.7"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_std_filesystem": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "use_std_filesystem": True,
    }
    requires = "imgui/1.91.8"


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        save(
            self,
            path=os.path.join(self.source_folder, "CMakeLists.txt"),
            content=(
                "find_package(imgui)\n"
                "target_link_libraries(ImGuiFileDialog PRIVATE imgui::imgui)\n"
                "install(TARGETS ImGuiFileDialog)\n"
                "install(FILES ImGuiFileDialog.h ImGuiFileDialogConfig.h DESTINATION include)\n"
            ),
            append=True,
        )  # Append


    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.use_std_filesystem:
            tc.preprocessor_definitions["USE_STD_FILESYSTEM"] = None
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["ImGuiFileDialog"]
