# LuxCore Dependencies Provider

LuxCoreDeps provides the dependencies needed to build LuxCore, starting with
version 2.10.

LuxCoreDeps is based on Conan dependency manager (https://conan.io/) and Github
Actions (https://github.com/features/actions). It builds dependency sets for
the following 4 platforms:
- Linux
- Windows
- MacOS Intel
- MacOS Arm

## Building dependencies

LuxCoreDeps is exclusively intended to be run in continuous integration by
Github Actions. The main execution script is `.github/workflows/deps.yml`.

Dependencies are built from sources, via Conan recipes.

To trigger dependency build, use `workflow_dispatch` event:
https://github.com/LuxCoreRender/LuxCoreDeps/actions/workflows/deps.yml

Dependency build is also triggered by `push` and `pull request` events.

## Exposing dependencies to LuxCore

Dependencies are made available to LuxCore via LuxCoreDeps _releases_.

To expose a new set of dependency, create a new release in LuxCoreDeps and
upload dependency sets to this release.

On the other side, from 2.10, LuxCore is equipped with scripts that enable it
to download and install the dependency sets thus created.


## Caveats & Tips

### Entry points
The main entry point is `.github/workflows/deps.yml`.
Other interesting files may be:
- `conanfile.py`: Conan script to build dependencies
- `conan-profiles`: folder with Conan profiles

### Compilation environment
For Python wheels to work properly, it is essential that dependencies are built
by `CIBUILDWHEEL`, with the same environment (compiler version, pypa image,
etc.) as the one intended for the wheels.

### Debugging
Dependency build can be debugged locally using `nektos/act`
(https://github.com/nektos/act).

## License This code is released under Apache 2.0 license.
