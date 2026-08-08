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
