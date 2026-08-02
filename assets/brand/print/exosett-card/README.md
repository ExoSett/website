# ExoSett business card production notes

The two SVG files are editable artwork masters. Each is **91 × 61 mm**, comprising an **85 × 55 mm** UK business-card trim size plus **3 mm bleed** on every edge. The trim box begins at `(3 mm, 3 mm)`. Important content remains within a safe box inset another 4 mm from the trim edge.

The front carries the ExoSett lock-up, headline, frame-and-cassette diagram, website and email address. The back contains only a centred standalone ExoSett frame symbol. The combined print PDF contains the front as page 1 and the back as page 2. Text is converted to vector paths during PDF export for reliable commercial output. The SVG front master retains editable IBM Plex Sans text and references the repository's local WOFF2 font files.

The PNG previews show the **trimmed 85 × 55 mm card**, not the bleed. They are rendered at 1200 × 776 pixels (approximately 359 ppi at finished size) for convenient inspection.

The PDF is a high-quality vector PDF with an RGB/DeviceRGB warm-grey background and monochrome artwork. The available SVG export workflow does not provide a dependable managed CMYK conversion, so the printer should apply its preferred CMYK profile during preflight/RIP. No crop marks are included.
