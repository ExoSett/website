# ExoSett business card production notes

The two SVG files are editable artwork masters. Each is **91 × 61 mm**, comprising an **85 × 55 mm** UK business-card trim size plus **3 mm bleed** on every edge. The trim box begins at `(3 mm, 3 mm)`. Important content remains within a safe box inset another 4 mm from the trim edge.

The front carries the approved outlined ExoSett production lock-up, headline, frame-and-cassette diagram, website and email address. The lock-up is reused without altering the symbol-to-wordmark geometry established by the editable source master. The back contains only a centred standalone ExoSett frame symbol. The combined print PDF contains the front as page 1 and the back as page 2. Text outside the approved logo is converted to vector paths during PDF export for reliable commercial output. The SVG front master retains editable IBM Plex Sans text and references the repository's local WOFF2 font files.

The PNG previews show the **trimmed 85 × 55 mm card**, not the bleed. They are rendered at 1200 × 776 pixels (approximately 359 ppi at finished size) for convenient inspection.

The PDF is a high-quality vector PDF with an RGB/DeviceRGB warm-grey background and monochrome artwork. The available SVG export workflow does not provide a dependable managed CMYK conversion, so the printer should apply its preferred CMYK profile during preflight/RIP. No crop marks are included.

## MKII QR back

`exosett-card-mk2-print.pdf` preserves page 1 directly from the approved print PDF. Its new page 2 is generated from `exosett-card-mk2-back.svg` and contains only a centred vector QR code and the approved ExoSett standalone symbol.

The QR code resolves to `https://www.exosett.com/` and uses error-correction level H. Its overall size is 30 mm square, including the required four-module quiet zone. The 29 × 29 data matrix uses a 0.810811 mm module pitch when the quiet zone is included. The visible hash symbol is 5.1 mm wide, or 17% of the overall QR width, with a centred nine-module background knockout.

The combined MKII preview shows the trimmed front and back side by side. The MKII PDF retains the original 91 × 61 mm page size, 3 mm bleed, vector artwork, DeviceRGB colour handling and no crop marks.
