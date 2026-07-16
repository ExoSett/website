# ExoSett brand assets

This directory contains the source and production files for the ExoSett symbol, logo and favicon.

## Directory structure

```text
brand/
├── README.md
├── source/
│   ├── exosett-favicon-master.svg
│   ├── exosett-symbol-master.svg
│   └── exosett-logo-horizontal-master.svg
├── web/
│   ├── exosett-symbol.svg
│   └── exosett-logo-horizontal.svg
└── favicon-source/
    ├── favicon-16.png
    ├── favicon-32.png
    ├── favicon-48.png
    └── favicon.ico
```

The exact contents may expand as further logo formats are developed.

## Source files

Files in `source/` are the editable Inkscape masters.

### `exosett-symbol-master.svg`

The master artwork for the ExoSett frame-cell symbol.

The symbol represents a square ExoSett frame cell, with four frame nodes and structural members extending towards adjacent cells.

### `exosett-logo-horizontal-master.svg`

The editable horizontal logo containing the ExoSett symbol and wordmark.

The wordmark uses:

- IBM Plex Sans
- Medium weight
- the spelling `ExoSett`

The wordmark should remain as editable text in the master file.

## Production files

Files in `web/` are intended for use on the website and in other published material.

Production SVG files should:

- be saved as Plain SVG;
- contain no unnecessary Inkscape metadata;
- use transparent backgrounds;
- preserve the original proportions;
- contain the wordmark as vector paths rather than live text.

Converting the wordmark to paths ensures that the logo renders consistently even where IBM Plex Sans is not installed.

Do not edit the production files directly. Make changes to the relevant master file and create a new production copy.

## Approved versions

The primary logo is the horizontal arrangement:

```text
[symbol] ExoSett
```

The standalone symbol may be used where the full logo would be too large or unnecessary, including:

- favicons;
- social-media icons;
- small interface elements;
- engineering drawing marks;
- watermarks;
- animation identifiers.

The approved base identity is monochrome:

- black artwork on a white or light background;
- white artwork on a black or dark background.

Colour versions may be developed later, but the monochrome logo remains the reference design.

## Clear space

Leave clear space around the logo so that it is not crowded by text, borders or other graphics.

As a general rule, the minimum clear space should be at least the diameter of one frame-node circle on every side.

More space may be used where the layout permits.

## Minimum size

The standalone symbol has been tested at sizes down to 16 × 16 pixels.

At very small sizes, some antialiasing is expected, but the symbol should remain even, recognisable and visually balanced.

The horizontal logo should not be used so small that the `ExoSett` wordmark becomes difficult to read. Use the standalone symbol instead.

## Do not

Do not:

- stretch or squash the logo;
- change its proportions;
- rotate it;
- rearrange the symbol and wordmark;
- alter the spacing between them without updating the master;
- substitute another typeface;
- add shadows, outlines, gradients or other effects;
- place the black logo on a dark background;
- place the white logo on a light background;
- add a coloured or white rectangle behind the symbol unless it is part of the intended layout.

## Website use

Use the production SVG files from `web/`.

Example:

```html
<img src="/assets/brand/web/exosett-logo-horizontal.svg" alt="ExoSett" />
```

The image width may be set in HTML or CSS while allowing the height to adjust automatically:

```css
.exosett-logo {
  width: 240px;
  height: auto;
}
```

## Favicon

The main ExoSett symbol remains transparent. The favicon uses a dedicated opaque white tile behind the black symbol to ensure reliable contrast on both light and dark browser tabs.

The root-level `favicon.ico` contains:

- 16 × 16 pixels;
- 32 × 32 pixels;
- 48 × 48 pixels.

It was generated from PNG exports of `source/exosett-favicon-master.svg`.

The ICO contents can be checked using ImageMagick:

```bash
identify favicon.ico
```

The website may also declare the SVG symbol as a modern favicon while retaining `/favicon.ico` for browsers and tools that request it automatically.

## Updating the logo

When changing the logo:

1. Edit the appropriate file in `source/`.
2. Preserve an editable version of the wordmark.
3. Save a production copy as Plain SVG.
4. Convert production wordmark text to paths.
5. Check the result in a browser.
6. Test the symbol at small sizes.
7. Commit both the updated master and production assets.
