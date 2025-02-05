from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, rm, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os
from pathlib import PurePosixPath

required_conan_version = ">=1.53.0"

# Gather here the various dependency versions, for convenience
BOOST_VERSION = "1.84.0"
OCIO_VERSION = "2.4.0"

class OpenImageIOConan(ConanFile):
    name = "openimageio"
    description = (
        "OpenImageIO is a library for reading and writing images, and a bunch "
        "of related classes, utilities, and applications. There is a "
        "particular emphasis on formats and functionality used in "
        "professional, large-scale animation and visual effects work for film."
    )
    topics = ("vfx", "image", "picture")
    license = "Apache-2.0", "BSD-3-Clause"
    homepage = "http://www.openimageio.org/"
    version = "2.5.16.0"
    user = "luxcore"
    channel = "luxcore"
    # revision_mode = "scm_folder"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo"],
        "with_libpng": [True, False],
        "with_freetype": [True, False],
        "with_hdf5": [True, False],
        "with_opencolorio": [True, False],
        "with_opencv": [True, False],
        "with_tbb": [True, False],
        "with_dicom": [True, False],
        "with_ffmpeg": [True, False],
        "with_giflib": [True, False],
        "with_libheif": [True, False],
        "with_raw": [True, False],
        "with_openjpeg": [True, False],
        "with_openvdb": [True, False],
        "with_ptex": [True, False],
        "with_libwebp": [True, False],
    }
    default_options = {
        "shared": False,
        "with_libjpeg": "libjpeg",
        "with_libpng": True,
        "with_freetype": True,
        "with_hdf5": False,
        "with_opencolorio": True,
        "with_opencv": False,
        "with_tbb": False,
        "with_dicom": False,  # Heavy dependency, disabled by default
        "with_ffmpeg": False,
        "with_giflib": True,
        "with_libheif": False,
        "with_raw": False,  # libraw is available under CDDL-1.0 or LGPL-2.1, for this reason it is disabled by default
        "with_openjpeg": True,
        "with_openvdb": False,  # FIXME: broken on M1
        "with_ptex": True,
        "with_libwebp": True,
        "fmt/*:header_only": True,
        "openexr/*:shared": False
    }

    tool_requires = [
        "yasm/1.3.0",
    ]

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        # Required libraries
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("boost/1.84.0")
        self.requires("libtiff/4.6.0")
        self.requires("imath/3.1.9", transitive_headers=True)
        # self.requires("openexr/3.1.9")
        self.requires("openexr/3.2.3")
        if self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.2")
        self.requires("pugixml/1.14")
        self.requires("libsquish/1.15")
        self.requires("tsl-robin-map/1.2.1")
        if Version(self.version) >= "2.4.17.0":
            self.requires("fmt/10.2.1", transitive_headers=True)
        else:
            self.requires("fmt/9.1.0", transitive_headers=True)

        # Optional libraries
        if self.options.with_libpng:
            self.requires("libpng/1.6.42")
        if self.options.with_freetype:
            self.requires("freetype/2.13.2")
        if self.options.with_hdf5:
            self.requires("hdf5/1.14.3")
        if self.options.with_opencolorio:
            self.requires(f"opencolorio/{OCIO_VERSION}")
        if self.options.with_opencv:
            self.requires("opencv/4.8.1")
        if self.options.with_tbb:
            self.requires("onetbb/2021.12.0")
        if self.options.with_dicom:
            self.requires("dcmtk/3.6.7")
        if self.options.with_ffmpeg:
            self.requires("ffmpeg/6.1")
        # TODO: Field3D dependency
        if self.options.with_giflib:
            self.requires("giflib/5.2.1")
        if self.options.with_libheif:
            self.requires("libheif/1.16.2")
        if self.options.with_raw:
            self.requires("libraw/0.21.2")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.5.2")
        if self.options.with_openvdb:
            self.requires("openvdb/8.0.1")
        if self.options.with_ptex:
            self.requires("ptex/2.4.2")
        if self.options.with_libwebp:
            self.requires("libwebp/1.3.2")
        self.requires(
            f"libdeflate/1.22",
            override=True,
            libs=True,
            transitive_libs=True,
        )
        # TODO: R3DSDK dependency
        # TODO: Nuke dependency

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if is_msvc(self) and is_msvc_static_runtime(self) and self.options.shared:
            raise ConanInvalidConfiguration(
                "Building shared library with static runtime is not supported!"
            )

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        rm(self, "conanfile.txt", ".")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.absolute_paths = True

        # CMake options
        tc.cache_variables["BUILD_SHARED_LIBS"] = False
        tc.variables["CMAKE_DEBUG_POSTFIX"] = ""  # Needed for 2.3.x.x+ versions
        tc.cache_variables["OIIO_BUILD_TOOLS"] = False
        tc.cache_variables["OIIO_BUILD_TESTS"] = False
        tc.cache_variables["BUILD_DOCS"] = False
        tc.cache_variables["INSTALL_DOCS"] = False
        tc.cache_variables["INSTALL_FONTS"] = False
        tc.cache_variables["INSTALL_CMAKE_HELPER"] = False
        tc.cache_variables["EMBEDPLUGINS"] = True  # Modified (to cache variable)
        tc.cache_variables["USE_OPENEXR"] = True  # Added
        tc.cache_variables["USE_PYTHON"] = False
        tc.cache_variables["USE_EXTERNAL_PUGIXML"] = True
        tc.cache_variables["BUILD_MISSING_FMT"] = False
        tc.cache_variables["USE_Qt5"] = False
        tc.cache_variables["VERBOSE"] = True
        tc.cache_variables["USE_Libsquish"] = False
        tc.cache_variables["LINKSTATIC"] = True


        # Conan is normally not used for testing, so fixing this option to not build the tests
        tc.cache_variables["BUILD_TESTING"] = False

        # OIIO CMake files are patched to check USE_* flags to require or not use dependencies
        tc.variables["USE_JPEGTURBO"] = (
            self.options.with_libjpeg == "libjpeg-turbo"
        )
        tc.variables[
            "USE_JPEG"
        ] = True  # Needed for jpeg.imageio plugin, libjpeg/libjpeg-turbo selection still works
        tc.variables["USE_HDF5"] = self.options.with_hdf5
        tc.variables["USE_OPENCOLORIO"] = self.options.with_opencolorio
        tc.variables["USE_OPENCV"] = self.options.with_opencv
        tc.variables["USE_TBB"] = self.options.with_tbb
        tc.variables["USE_DCMTK"] = self.options.with_dicom
        tc.variables["USE_FFMPEG"] = self.options.with_ffmpeg
        tc.variables["USE_FIELD3D"] = False
        tc.variables["USE_GIF"] = self.options.with_giflib
        tc.variables["USE_LIBHEIF"] = self.options.with_libheif
        tc.variables["USE_LIBRAW"] = self.options.with_raw
        tc.variables["USE_OPENVDB"] = self.options.with_openvdb
        tc.variables["USE_PTEX"] = self.options.with_ptex
        tc.variables["USE_R3DSDK"] = False
        tc.variables["USE_NUKE"] = False
        tc.variables["USE_OPENGL"] = False
        tc.variables["USE_LIBPNG"] = self.options.with_libpng
        tc.variables["USE_FREETYPE"] = self.options.with_freetype
        tc.variables["USE_LIBWEBP"] = self.options.with_libwebp
        tc.variables["USE_OPENJPEG"] = self.options.with_openjpeg

        tc.preprocessor_definitions["BOOST_NO_CXX98_FUNCTION_BASE"] = None  # No deprecated functions (C++17)
        tc.cache_variables["STOP_ON_WARNING"] = False
        tc.cache_variables["USE_STD_REGEX"] = True

        tc.generate()

        cd = CMakeDeps(self)
        if self.options.with_libwebp:
            cd.set_property("libwebp::webp", "cmake_target_name", "WebP::webp")
            cd.set_property("libwebp::webpdemux", "cmake_target_name", "WebP::webpdemux")
        if self.options.with_freetype:
            cd.set_property("freetype", "cmake_find_mode", "module")

        cd.generate()

        # Copy fmt files
        print("Copy fmt files")
        fmt = self.dependencies["fmt"]
        fmt_includes = fmt.cpp_info.includedirs
        destination = PurePosixPath(
            self.source_folder, "src", "include", "OpenImageIO", "detail", "fmt"
        )

        for origin in fmt_includes:
            copied = copy(
                self,
                pattern="*.h",
                src=origin,
                dst=destination,
                keep_path=False,
            )
            print(f"Copied '{copied}' from '{origin}' to '{destination}'...")



    def build(self):
        print("Building OIIO")
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "src", "cmake", "externalpackages.cmake"), "fmt::fmt", "fmt::fmt-header-only")
        replace_in_file(self, os.path.join(self.source_folder, "src", "libutil", "CMakeLists.txt"), "fmt::fmt", "fmt::fmt-header-only")
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        copy(
            self,
            "*.h",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "include"),
        )
        copy(
            self,
            "*.hpp",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "include"),
        )
        copy(
            self,
            "*.lib",
            src=self.build_folder,
            dst=os.path.join(self.package_folder, "lib"),
            keep_path=False,
        )
        copy(
            self,
            "*.a",
            src=self.build_folder,
            dst=os.path.join(self.package_folder, "lib"),
            keep_path=False,
        )
        copy(
            self,
            "*.cmake",
            src=self.build_folder,
            dst=os.path.join(self.package_folder, "lib", "cmake"),
            keep_path=False,
        )

        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.settings.os == "Windows":
            for vc_file in ("concrt", "msvcp", "vcruntime"):
                rm(self, f"{vc_file}*.dll", os.path.join(self.package_folder, "bin"))

    @staticmethod
    def _conan_comp(name):
        return f"openimageio_{name.lower()}"

    def _add_component(self, name):
        component = self.cpp_info.components[self._conan_comp(name)]
        component.set_property("cmake_target_name", f"OpenImageIO::{name}")
        component.set_property("cmake_file_name", name)
        return component

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenImageIO")
        self.cpp_info.set_property("pkg_config_name", "OpenImageIO")

        self.cpp_info.names["cmake_find_package"] = "OpenImageIO"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenImageIO"

        # OpenImageIO::OpenImageIO_Util
        open_image_io_util = self._add_component("OpenImageIO_Util")
        open_image_io_util.libs = ["OpenImageIO_Util"]
        open_image_io_util.requires = [
            "boost::filesystem",
            "boost::thread",
            "boost::system",
            "boost::regex",
            "imath::imath",
            "openexr::openexr",
        ]
        if self.settings.os in ["Linux", "FreeBSD"]:
            open_image_io_util.system_libs.extend(
                ["dl", "m", "pthread"]
            )
        if self.options.with_tbb:
            open_image_io_util.requires.append("onetbb::onetbb")

        # OpenImageIO::OpenImageIO
        open_image_io = self._add_component("OpenImageIO")
        open_image_io.libs = ["OpenImageIO"]
        open_image_io.requires = [
            "openimageio_openimageio_util",
            "zlib::zlib",
            "boost::thread",
            "boost::system",
            "boost::container",
            "boost::regex",
            "libtiff::libtiff",
            "pugixml::pugixml",
            "tsl-robin-map::tsl-robin-map",
            "libsquish::libsquish",
            "fmt::fmt",
            "imath::imath",
            "openexr::openexr",
        ]

        if self.options.with_libjpeg == "libjpeg":
            open_image_io.requires.append("libjpeg::libjpeg")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            open_image_io.requires.append(
                "libjpeg-turbo::libjpeg-turbo"
            )
        if self.options.with_libpng:
            open_image_io.requires.append("libpng::libpng")
        if self.options.with_freetype:
            open_image_io.requires.append("freetype::freetype")
        if self.options.with_hdf5:
            open_image_io.requires.append("hdf5::hdf5")
        if self.options.with_opencolorio:
            open_image_io.requires.append("opencolorio::opencolorio")
        if self.options.with_opencv:
            open_image_io.requires.append("opencv::opencv")
        if self.options.with_dicom:
            open_image_io.requires.append("dcmtk::dcmtk")
        if self.options.with_ffmpeg:
            open_image_io.requires.append("ffmpeg::ffmpeg")
        if self.options.with_giflib:
            open_image_io.requires.append("giflib::giflib")
        if self.options.with_libheif:
            open_image_io.requires.append("libheif::libheif")
        if self.options.with_raw:
            open_image_io.requires.append("libraw::libraw")
        if self.options.with_openjpeg:
            open_image_io.requires.append("openjpeg::openjpeg")
        if self.options.with_openvdb:
            open_image_io.requires.append("openvdb::openvdb")
        if self.options.with_ptex:
            open_image_io.requires.append("ptex::ptex")
        if self.options.with_libwebp:
            open_image_io.requires.append("libwebp::libwebp")
        if self.settings.os in ["Linux", "FreeBSD"]:
            open_image_io.system_libs.extend(["dl", "m", "pthread"])

        if not self.options.shared:
            open_image_io.defines.append("OIIO_STATIC_DEFINE")
