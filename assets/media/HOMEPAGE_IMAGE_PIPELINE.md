# Home-page component image pipeline

The component illustration on the ExoSett home page is generated from the CAD
source. It should not be edited manually as a finished raster image.

The published website asset is:

`assets/media/home/accommodation-cell-module-installation.webp`

The generation tools and geometry live in the separate `exosett_cad`
repository. The generated FreeCAD, mesh, Blender and preview files are build
outputs and are not committed there.

## Pipeline overview

```text
ExoSett specifications and Python geometry generators
    -> FreeCAD composition (.FCStd)
    -> STL meshes and material manifest
    -> Blender scene and render
    -> transparent PNG and WebP
    -> website WebP asset
```

## 1. Source geometry and composition

The composition is defined by these principal files in `exosett_cad`:

- `specs/exosett_homepage_composition_spec.toml` defines which frame variant is
  used and places the accommodation frame, service frame, module and direction
  arrow.
- `src/exosett/freecad_homepage_composition.py` assembles the component geometry
  in FreeCAD.
- The underlying frame, node, module-envelope and connection geometry comes
  from the other specifications and Python generators in `specs/` and
  `src/exosett/`.
- `scripts/build_homepage_composition.py` writes the assembled FreeCAD document.

The generated FreeCAD file is:

`output/fcstd/exosett_homepage_composition_study_v0_2_0.FCStd`

From the root of `exosett_cad`, build it with FreeCAD's command-line
interpreter. On the current macOS development machine, the command is:

```sh
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c \
  "import runpy, sys; sys.argv = ['scripts/build_homepage_composition.py']; runpy.run_path('scripts/build_homepage_composition.py', run_name='__main__')"
```

## 2. Export FreeCAD objects for rendering

`scripts/export_homepage_render_meshes.py` opens the generated `.FCStd` file and
exports each non-empty FreeCAD object as an STL mesh. It also creates a JSON
manifest that maps the objects to the Blender material groups for the
accommodation frame, service frame, module, corner castings, connections and
direction arrow.

The outputs are written under:

`output/render/homepage-v0.2/`

Run the export with:

```sh
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c \
  "import runpy, sys; sys.argv = ['scripts/export_homepage_render_meshes.py']; runpy.run_path('scripts/export_homepage_render_meshes.py', run_name='__main__')"
```

This creates `meshes/*.stl` and `mesh-manifest.json`.

## 3. Render in Blender

`scripts/render_homepage_preview.py` builds the Blender scene from the STL
meshes and manifest. It is the source of truth for the image's materials,
lighting, orthographic camera, 1600 x 900 canvas and colour management.

The material colours identify the main parts:

- beige: accommodation module;
- dark blue: accommodation frame;
- grey-blue: service frame;
- orange-red: insertion/removal arrow.

The Blender render uses a transparent film and RGBA output. There is no ground
plane. Both the PNG and WebP must retain an alpha channel and contain genuinely
transparent pixels; the render script checks this and fails if transparency is
lost.

Render with:

```sh
/opt/homebrew/bin/blender --background --python scripts/render_homepage_preview.py
```

The principal outputs are:

- `output/render/homepage-v0.2/exosett-homepage-preview-v0.2.blend`
- `output/render/homepage-v0.2/exosett-homepage-preview-v0.2.png`
- `output/render/homepage-v0.2/exosett-homepage-preview-v0.2.webp`

The WebP is currently saved at quality 88 with RGBA colour mode.

## 4. Publish the web asset

After visually checking the regenerated preview, copy the WebP from
`exosett_cad` into this website repository:

```sh
cp ../../exosett_cad/output/render/homepage-v0.2/exosett-homepage-preview-v0.2.webp \
  assets/media/home/accommodation-cell-module-installation.webp
```

The exact relative path between the two repositories may differ between
machines. Do not replace the website asset unless the geometry, camera,
lighting, scale and composition remain equivalent to the existing image apart
from an intentional change.

The image is referenced from the home page in `index.html`. If browsers may
have cached an older file at the same URL, update the asset URL with an
appropriate version identifier or use a versioned filename.

## 5. Verification

Before publishing:

1. Confirm that the final WebP is 1600 x 900 and has an alpha channel with both
   transparent and opaque pixels.
2. Compare the regenerated image with the previous version for unintended
   changes to geometry, camera, lighting, scale or composition.
3. Check the actual home page at desktop and mobile widths against its white
   background.
4. Inspect fine edges around the frame, module, arrow and node details for grey
   pixels, dark or light halos, and other alpha artefacts.
5. Run the website's normal validation from the website repository:

   ```sh
   python3 scripts/validate.py
   ```

Only the intended generated asset and any deliberately related HTML or CSS
changes should be included in the website commit.
