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

## Required formatting and validation

Before completing or publishing website changes, format all source HTML and CSS,
run the local checks, and check the site using the installed local `vnu` (W3C Nu checker). A successful
build or local validation alone is not sufficient. Fix all conformance errors;
review warnings and notices and record any remaining limitations. A validator execution
failure or unchecked page must be reported as incomplete, never as a pass.

Install the pinned formatter dependencies with `npm ci`, then run:

```sh
npm run format
npm run check
```

Prettier uses the repository's `@awmottaz/prettier-plugin-void-html` configuration so that
void HTML elements use `>` rather than `/>`, avoiding W3C trailing-slash notices. VS Code's Prettier format-on-save uses this
same configuration after `npm ci`. Do not strip slashes manually after formatting
or disable validation to accommodate a formatter conflict. Generated `_site/`
and Sketch assets are excluded from source formatting.

After assembling deployment output, run `npm run check:built` from the website
source directory. This checks source formatting and validates the assembled site.
Do not edit generated output to fix errors: correct its source and rebuild.

## Validation details

The curated primary navigation is maintained in `scripts/sync_navigation.py`.
After editing its menu definitions, run `python3 scripts/sync_navigation.py`
and `npm run format`. The generated navigation stays in the source HTML so
section links and native submenu disclosures work without JavaScript.
`npm run check` checks every header against the shared definition, including
current-page markers. `assets/js/navigation.js` enhances native disclosures
with desktop hover, Escape dismissal and coordinated opening/closing.

Run all checks with `npm run check`: Prettier formatting, ExoSett-specific
validation and local `vnu` HTML/CSS conformance. Any failed stage makes the
command fail.

`python3 scripts/validate.py` runs only the ExoSett-specific checks: internal
links, assets, image dimensions, metadata consistency, sitemap coverage,
navigation, story requirements and JSON-LD. Generic HTML checks such as duplicate
IDs, title validity, image attribute syntax and trailing-slash formatting are
handled by `vnu` and Prettier. The one-heading/one-main rule remains an ExoSett
page convention.

Source validation excludes nested `_site/` deployment output. To validate an
assembled deployment, run `python3 _site/scripts/validate.py` instead; this
checks `_site/` as the site root, including its generated Sketch assets.
Regenerate `_site/` using the build steps below before checking deployment
output. Do not edit generated files directly.

The structured-data checks can still be run independently with
`python3 scripts/validate_structured_data.py`.

W3C validation **must use the locally installed `vnu`**, for both HTML and CSS.
Do not upload site files to online validation services. The wrapper below invokes
`vnu --also-check-css --format json --stdout` with an explicit list of local
HTML and CSS files and saves the results:

```sh
python3 scripts/validate_w3c.py --report /tmp/exosett-w3c.json
```

This requires Python 3.9+ and `vnu` on PATH (on this Mac it is installed at
`/opt/homebrew/bin/vnu`). No network access is needed. A missing or failed local
validator is an incomplete check; there is no online fallback.
Use `--root _site` to check assembled deployment output, including Sketch CSS.
The default checks the source tree, excluding `_site` and dependency directories.
Review every error, warning and notice in the JSON report. Fix errors in source,
reformat and rerun validation after changes. JavaScript-generated markup is not
covered by this static check. This uses Nu's CSS checking, not the separate
online W3C CSS Validation Service.

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
