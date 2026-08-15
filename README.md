# ExoSett Website

This repository contains the source for the ExoSett public website.

## Website

https://www.exosett.com

## Purpose

The ExoSett website introduces the ExoSett building system and provides
information, diagrams, engineering notes, stories and contact details.

## Technology

The site is intentionally simple:

- Static HTML
- CSS
- Hosted using GitHub Pages

## Validation

Run the complete site validation, including internal links, local assets,
metadata, image dimensions, story illustrations, sitemap coverage and JSON-LD,
with:

```sh
python3 scripts/validate.py
```

The structured-data checks can still be run independently with
`python3 scripts/validate_structured_data.py`.

## ExoSett Sketch

The public Sketch page is `/design/sketch/`. Its page shell belongs to this repository, while its browser application is built from the sibling `ExoSett/modelling` repository.

To assemble and validate the combined site locally:

```sh
cd ../modelling/sketch
npm ci
npm run check
npm run build:embed

cd ../../website
python3 scripts/build_site.py \
  --sketch-dist ../modelling/sketch/dist-embed \
  --output _site
cd _site
python3 scripts/validate.py
```

The `_site/` directory is generated deployment output and is not committed.

## Brand assets

Logo source files, production SVGs, favicon assets and usage guidance are in [`assets/brand/`](assets/brand/).

## Component media

Review animations for component pages are stored by component in
`assets/media/components/<component-name>/`. Each set uses `animation.webm`,
`animation.mp4` and `poster.webp`; transparent turntables additionally use an
HEVC-alpha `animation.mov` for Safari. Pages use the poster as a static
alternative when reduced motion is requested.

## Copyright

Copyright © 2026 ExoSett. All rights reserved.
