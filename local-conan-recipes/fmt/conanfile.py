import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.layout import basic_layout
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.1"


class FmtConan(ConanFile):
    name = "fmt"
    user = "luxcore"
    channel = "luxcore"
    description = "A safe and fast alternative to printf and IOStreams."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/fmtlib/fmt"
    topics = ("format", "iostream", "printf")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    version = "11.0.2"
    options = {
        "header_only": [True, False],
        "shared": [True, False],
        "fPIC": [True, False],
        "with_fmt_alias": [True, False],
        "with_os_api": [True, False],
        "with_unicode": [True, False],
    }
    default_options = {
        "header_only": True,
        "shared": False,
        "fPIC": True,
        "with_fmt_alias": False,
        "with_os_api": True,
        "with_unicode": True,
    }

    @property
    def _has_with_os_api_option(self):
        return Version(self.version) >= "7.0.0"

    @property
    def _has_with_unicode_option(self):
        return Version(self.version) >= "11.0.0"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_with_os_api_option:
            del self.options.with_os_api
        elif str(self.settings.os) == "baremetal":
            self.options.with_os_api = False
        if not self._has_with_unicode_option:
            del self.options.with_unicode

    def configure(self):
        if self.options.header_only:
            self.options.rm_safe("fPIC")
            self.options.rm_safe("shared")
            self.options.rm_safe("with_os_api")
        elif self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        if self.options.header_only:
            basic_layout(self, src_folder="src")
        else:
            cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()
        else:
            del self.info.options.with_fmt_alias

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not self.options.header_only:
            tc = CMakeToolchain(self)
            tc.cache_variables["FMT_DOC"] = False
            tc.cache_variables["FMT_TEST"] = False
            tc.cache_variables["FMT_INSTALL"] = True
            tc.cache_variables["FMT_LIB_DIR"] = "lib"
            if self._has_with_os_api_option:
                tc.cache_variables["FMT_OS"] = bool(self.options.with_os_api)
            if self._has_with_unicode_option:
                tc.cache_variables["FMT_UNICODE"] = bool(self.options.with_unicode)
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        if Version(self.version) < "10.2.0":
            copy(self, pattern="*LICENSE.rst", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        else:
            copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if self.options.header_only:
            copy(self, pattern="*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        else:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "res"))
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        target = "fmt-header-only" if self.options.header_only else "fmt"
        self.cpp_info.set_property("cmake_file_name", "fmt")
        self.cpp_info.set_property("cmake_target_name", f"fmt::{target}")
        if target == "fmt-header-only":
            self.cpp_info.set_property("cmake_target_aliases", ["fmt::fmt"])

        # Mirror upstream find package version policy:
        # https://github.com/fmtlib/fmt/blob/11.1.1/CMakeLists.txt#L403-L407
        self.cpp_info.set_property("cmake_config_version_compat", "AnyNewerVersion")
        self.cpp_info.set_property("pkg_config_name",  "fmt")

        if is_msvc(self):
            if self.options.get_safe("with_unicode"):
                self.cpp_info.components["_fmt"].cxxflags.append("/utf-8")
            else:
                # Set the FMT_UNICODE=0, as defined publicly upstream
                # https://github.com/fmtlib/fmt/blob/11.1.1/CMakeLists.txt#L371
                self.cpp_info.components["_fmt"].defines.append("FMT_UNICODE=0")

        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        if self.options.with_fmt_alias:
            self.cpp_info.components["_fmt"].defines.append("FMT_STRING_ALIAS=1")

        if self.options.header_only:
            self.cpp_info.components["_fmt"].defines.append("FMT_HEADER_ONLY=1")
            self.cpp_info.components["_fmt"].libdirs = []
            self.cpp_info.components["_fmt"].bindirs = []
        else:
            postfix = "d" if self.settings.build_type == "Debug" else ""
            libname = "fmt" + postfix
            self.cpp_info.components["_fmt"].libs = [libname]
            if self.settings.os == "Linux":
                self.cpp_info.components["_fmt"].system_libs.extend(["m"])
            if self.options.shared:
                self.cpp_info.components["_fmt"].defines.append("FMT_SHARED")

        self.cpp_info.components["_fmt"].set_property("cmake_target_name", f"fmt::{target}")
        if target == "fmt-header-only":
            self.cpp_info.components["_fmt"].set_property("cmake_target_aliases", ["fmt::fmt"])
