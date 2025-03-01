import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.scm import Git


class ImguiFilebrowserConan(ConanFile):
    name = "imgui-filebrowser"
    version = "0.1"
    user = "luxcore"
    channel = "luxcore"
    url = "https://github.com/AirGuanZ/imgui-filebrowser"

    license = "MIT"
    # No settings/options are necessary, this is header only
    exports_sources = "include/*"
    # We can avoid copying the sources to the build folder in the cache
    no_copy_source = True

    def source(self):
        git = Git(self)  # by default, the current folder "."
        git.fetch_commit(
            url="https://github.com/AirGuanZ/imgui-filebrowser",
            commit="347dda538f37fb71be3767e66930e0d7bc5d5f52",
        ) # git clone url target

    def package(self):
        # This will also copy the "include" folder
        copy(self, "*.h", self.source_folder, self.package_folder)
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        # For header-only packages, libdirs and bindirs are not used
        # so it's necessary to set those as empty.
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
