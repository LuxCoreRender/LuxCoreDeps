# LuxCoreDeps - the LuxCore Dependency Provider

**LuxCoreDeps provides the dependencies needed to build LuxCore, starting with
version 2.10.**

LuxCoreDeps is based on Conan dependency manager (https://conan.io/) and Github
Actions (https://github.com/features/actions). It builds dependency sets for
the following 4 platforms:
- Linux
- Windows
- MacOS Intel
- MacOS Arm

## How does it work

LuxCoreDeps builds a Conan cache with all the dependencies (binaries and
headers) required to build LuxCore. Once built, the cache is saved (`conan
cache save`) and published in a Github release.

On consumer side (LuxCore), the cache is downloaded and restored (`conan
cache restore`), making all the dependencies available for LuxCore build.

```mermaid
flowchart LR
  Publish --> Download

  subgraph "`**LuxCoreDeps**`"
  direction TB
  GetDeps(Get Dependency Recipes) --> BuildDeps(Build Dependencies)
  --> Save(Save Cache) --> Publish("Publish Cache (Release)");
  end

  subgraph "`**LuxCore**`"
  direction TB
  Download(Download Cache) --> Restore(Restore Cache)
  --> BuildLux(Build LuxCore);
  end
```



## Building dependencies

Dependencies are built from sources, thanks to Conan recipes. Building from
sources provides the following benefits:
- The binary compatibility (compiler version, GLIBC version etc.) can be put
  under control. Which, in particular, is required for Python wheel.
- The options of each dependency can be selected in fine detail.
- The build options (SSE, AVX, compiler optimizations...) can also be selected
  in fine detail
- Dependency source code can be patched if needed

LuxCoreDeps is exclusively intended to be run in continuous integration by
Github Actions. The main execution script is `.github/workflows/deps.yml`.


To trigger dependency build, use `workflow_dispatch` event:
https://github.com/LuxCoreRender/LuxCoreDeps/actions/workflows/deps.yml

Dependency build is also triggered by `push` events.

## Exposing dependencies to LuxCore

_(For admin only - requires special rights on repo)_

Dependencies are made available to LuxCore via LuxCoreDeps **releases**:
https://github.com/LuxCoreRender/LuxCoreDeps/releases


To expose a new set of dependency, create a new release in LuxCoreDeps and
upload dependency sets in the assets of the release.


## Caveats & Tips

### LuxCoreDeps Entry points
The main entry point is `.github/workflows/deps.yml`.
Other interesting files may be:
- `conanfile.py`: Conan script to build dependencies
- `conan-profiles`: folder with Conan profiles

### Compilation environment
For Python wheels to work properly, it is essential that dependencies be built
by `CIBUILDWHEEL`, with the same environment (compiler version, docker image,
etc.) as the one intended for the wheels.
Note that it requires to build a fake wheel.

### Debugging
Dependency build can be debugged locally using `nektos/act`
(https://github.com/nektos/act).

`debug.sh` contains a working example of `act` invokation under Linux.

## License
This code is released under Apache 2.0 license.
