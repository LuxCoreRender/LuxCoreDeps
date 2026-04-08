# Local Embree Conan Recipe

This recipe packages a prebuilt `embree/4.4.0` binary for local use.

## How to use

1. Place your prebuilt Embree files under:
   - `conan-local-recipes/recipes/embree/all/prebuilt/include/`
   - `conan-local-recipes/recipes/embree/all/prebuilt/lib/`
   - `conan-local-recipes/recipes/embree/all/prebuilt/bin/` (optional, for shared DLLs)

2. If available, also add `LICENSE` into `conan-local-recipes/recipes/embree/all/prebuilt/`.

3. Create the local package from the recipe:

   ```bash
   cd c:\SPEC\LuxCoreDeps\conan-local-recipes\recipes\embree\all
   conan create . --profile:all=c:\SPEC\LuxCoreDeps\conan-profiles\conan-profile-Windows-ARM64 --version=4.4.0
   ```

4. Then rerun the main build script. The local recipe is served via `mylocal` remote and will be used instead of rebuilding Embree.

## Notes

- This recipe expects the packaged library to be named `embree4.lib` and the package consumer to link against `embree4`.
- If you are packaging a shared build, include both `lib/embree4.lib` and `bin/embree4.dll`.
- If you are packaging a static build, only `lib/embree4.lib` is required.
