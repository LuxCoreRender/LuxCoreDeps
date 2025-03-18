# SPDX-FileCopyrightText: 2024 Howetuft
#
# SPDX-License-Identifier: Apache-2.0

"""A package to install profiles in cache.

(to be used with conan config install-pkg)
"""

import os
from conan import ConanFile
from conan.tools.files import copy

class Conf(ConanFile):
    name = "luxcoreconf"
    # Version should be set by `conan install`
    user = "luxcore"
    channel = "luxcore"
    package_type = "configuration"

    def export_sources(self):
        print(self.recipe_folder)
        print(os.listdir(self.recipe_folder))
        copy(self,
             "conan-profile-*",
             src=self.recipe_folder,
             dst=self.export_sources_folder
        )


    def package(self):
        copy(self,
             "conan-profile-*",
             src=self.export_sources_folder,
             dst=os.path.join(self.package_folder, "profiles")
        )
