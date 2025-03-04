import os
from pathlib import Path
from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain

# https://docs.conan.io/2/tutorial/creating_packages/other_types_of_packages/package_prebuilt_binaries.html#packaging-already-pre-built-binaries
# https://github.com/conda-forge/cuda-nvrtc-feedstock/blob/main/recipe/meta.yaml

class nvrtcRecipe(ConanFile):
    name = "nvrtc"
    version = "12.8.61"
    user = "luxcore"
    channel = "luxcore"
    package_type = "library"
    settings = "os", "arch", "build_type"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": False,
    }

    _libs = []

    def validate(self):
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration("MacOS not supported")

    def build(self):
        _os = str(self.settings.os)
        quirks = {
            "Linux": ("linux-x86_64", "tar.xz"),
            "Windows": ("windows-x86_64", "zip"),
        }

        platform, extension = quirks[_os]

        url = (
            "https://developer.download.nvidia.com/compute/cuda/redist/cuda_nvrtc/"
            f"{platform}/cuda_nvrtc-{platform}-{self.version}-archive.{extension}"
        )
        get(self, url, destination=self.build_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def layout(self):
        cmake_layout(self)

    def package(self):
        debug = self.output.debug

        # Folder alias (for convenience)
        build_root = Path(self.build_folder)
        pack_root = Path(self.package_folder)
        build_lib = build_root / "lib"
        build_bin = build_root / "bin"
        pack_lib = pack_root / "lib"
        pack_bin = pack_root / "bin"
        build_include = build_root / "include"
        pack_include = pack_root / "include"

        # Libraries
        if self.settings.os == "Linux":
            # Linux libraries
            if self.options.shared:
                copy(self, "*.so*" , build_lib, pack_lib)
                copy(self, "*.so*", build_lib / "stubs", pack_lib / "stubs")
            else:
                copy(self, "*.a" , build_lib, pack_lib)
        else:
            # Windows libraries
            if self.options.shared:
                copy(self, "*.dll", build_bin, pack_bin)
                copy(self, "nvrtc.lib", build_lib / "x64", pack_lib / "x64")
            else:
                copy(self, "*_static.lib", build_lib / "x64", pack_lib / "x64")

        # Headers
        copy(self, "*.h", build_include, pack_include)

        # License
        copy(self, "LICENSE", build_root, pack_root)

    # https://docs.nvidia.com/cuda/nvrtc/#installation
    def package_info(self):
        if self.options.shared:
            # Don't declare anything here otherwise it will get mangled while
            # repairing (incompatible with dynamic load...)
            self.cpp_info.libs = []
        else:
            self.cpp_info.libs = ["nvrtc_static", "nvrtc-builtins_static"]

        self.cpp_info.set_property("cmake_file_name", "nvrtc")
