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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("gtk/system")

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


        # copy(self, "LICENSE", dst="licenses", src=self._source_subfolder)

        # libname = "nfd_d" if self.settings.build_type == "Debug" else "nfd"
        # if self.settings.compiler == "msvc":
            # copy(self, "*%s.lib" % libname, dst="lib", src=self._source_subfolder, keep_path=False)
        # else:
            # copy(self, "*%s.a" % libname, dst="lib", src=self._source_subfolder, keep_path=False)
        # copy(self, "*nfd.h", dst="include", src=self._source_subfolder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["nfd_d" if self.settings.build_type == "Debug" else "nfd"]

        self.cpp_info.frameworks = ["AppKit", "UniformTypeIdentifiers"]
