import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy


class NativefiledialogConan(ConanFile):
    name = "nativefiledialog"
    version = "1.2.1"
    user = "luxcore"
    channel = "luxcore"
    license = "Zlib"
    homepage = "https://github.com/btzy/nativefiledialog-extended"
    description = "A tiny, neat C library that portably invokes native file open and save dialogs."
    topics = ("conan", "dialog", "gui")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("gtk/system")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["nfd_ROOT_PROJECT"] = False
        tc.cache_variables["NFD_BUILD_TESTS"] = False
        tc.cache_variables["NFD_BUILD_SDL2_TESTS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package(self):
        copy(
            self,
            "LICENSE.txt",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses")
        )
        cmake = CMake(self)
        cmake.install()


    def package_info(self):
        self.cpp_info.libs = ["nfd_d" if self.settings.build_type == "Debug" else "nfd"]

        self.cpp_info.frameworks = ["AppKit", "UniformTypeIdentifiers"]
