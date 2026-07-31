#!/usr/bin/env python3
"""Validate links, assets, metadata and page structure for the static site."""

import struct
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


SITE_ORIGIN = "https://www.exosett.com"
STANDARD_STORY_NOTE = (
    "This story illustration is intended to depict a scene from the story "
    "rather than accurately represent ExoSett engineering or a finished "
    "ExoSett design."
)
REFERENCE_ATTRIBUTES = {
    "a": ("href",),
    "img": ("src",),
    "link": ("href",),
    "script": ("src",),
    "source": ("src",),
    "video": ("poster",),
}


class Page(HTMLParser):
    """The validation-relevant structure extracted from one HTML page."""

    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path.resolve()
        self.ids = []
        self.images = []
        self.references = []
        self.tag_counts = Counter()
        self.canonicals = []
        self.robots = ""
        self.metadata = {}
        self.story_illustrations = []
        self.story_notes = []
        self._note_depth = 0
        self._note_parts = []
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        line = self.getpos()[0]
        self.tag_counts[tag] += 1

        if self._note_depth:
            self._note_depth += 1

        element_id = attributes.get("id")
        if element_id:
            self.ids.append((element_id, line))

        classes = set((attributes.get("class") or "").split())
        if tag == "img":
            self.images.append((attributes, line))
            if "component-media__image" in classes:
                self.story_illustrations.append(attributes)

        if "story-illustration-note" in classes:
            self._note_depth = 1
            self._note_parts = []

        for attribute in REFERENCE_ATTRIBUTES.get(tag, ()):
            value = attributes.get(attribute)
            if value:
                self.references.append((value, f"{tag} {attribute}", line))

        if tag == "link" and attributes.get("rel") == "canonical":
            canonical = attributes.get("href")
            if canonical:
                self.canonicals.append(canonical)

        if tag == "meta":
            content = attributes.get("content") or ""
            if attributes.get("name") == "robots":
                self.robots = content
            for attribute in ("name", "property"):
                key = attributes.get(attribute)
                if key:
                    self.metadata.setdefault(key, []).append(content)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self._note_depth > 1:
            self._note_depth -= 1

    def handle_endtag(self, tag):
        if not self._note_depth:
            return
        self._note_depth -= 1
        if not self._note_depth:
            text = " ".join("".join(self._note_parts).split())
            self.story_notes.append(text)
            self._note_parts = []

    def handle_data(self, data):
        if self._note_depth:
            self._note_parts.append(data)

    @property
    def noindex(self):
        return "noindex" in self.robots.lower()

    @property
    def id_set(self):
        return {element_id for element_id, _ in self.ids}

    def metadata_values(self, name):
        return self.metadata.get(name, [])


class SiteValidator:
    """Own the site context and run all validation passes."""

    def __init__(self, root):
        self.root = root.resolve()
        self.redirect_page = (
            self.root / "components" / "accommodation-module" / "index.html"
        )
        self.pages = {}
        self.errors = []

    def run(self):
        self.load_pages()

        for page in self.pages.values():
            self.validate_page(page)

        for path in sorted((self.root / "stories").glob("*/index.html")):
            self.validate_story(self.pages[path.resolve()])

        self.validate_sitemap()
        return not self.errors

    def load_pages(self):
        self.pages = {
            path.resolve(): Page(path)
            for path in sorted(self.root.rglob("*.html"))
        }

    def validate_page(self, page):
        self.validate_ids(page)
        self.validate_landmarks(page)
        self.validate_canonical(page)
        self.validate_references(page)
        self.validate_images(page)
        self.validate_social_metadata(page)

    def validate_ids(self, page):
        counts = Counter(element_id for element_id, _ in page.ids)
        for element_id, count in sorted(counts.items()):
            if count > 1:
                self.error(
                    page,
                    f"duplicate id {element_id!r} appears {count} times",
                )

    def validate_landmarks(self, page):
        for tag in ("h1", "main"):
            count = page.tag_counts[tag]
            if count != 1:
                self.error(page, f"expected exactly one {tag}, found {count}")

    def validate_canonical(self, page):
        if page.path == self.redirect_page:
            expected = (
                "https://www.exosett.com/components/accommodation-cassette/"
            )
        else:
            expected = self.page_url(page.path)

        if page.canonicals != [expected]:
            self.error(page, f"canonical must be exactly {expected}")

    def validate_references(self, page):
        for value, source, line in page.references:
            destination = self.local_path(page.path, value)
            if destination is None:
                continue
            if not destination.is_file():
                self.error(page, f"missing {source} target: {value}", line)
                continue

            fragment = unquote(urlparse(value).fragment)
            if not fragment or destination.suffix.lower() not in {".html", ".htm"}:
                continue

            target = self.pages.get(destination)
            if not target or fragment not in target.id_set:
                target_name = self.relative(destination)
                self.error(
                    page,
                    f"missing fragment #{fragment} in {target_name}",
                    line,
                )

    def validate_images(self, page):
        for image, line in page.images:
            if "alt" not in image:
                self.error(page, "image is missing alt", line)

            width = image.get("width")
            height = image.get("height")
            if bool(width) != bool(height):
                self.error(page, "image must declare both width and height", line)

            source = image.get("src")
            destination = self.local_path(page.path, source) if source else None
            if not destination or not destination.is_file() or not width or not height:
                continue

            try:
                declared = (int(width), int(height))
            except ValueError:
                self.error(page, "image dimensions must be integers", line)
                continue

            actual = raster_dimensions(destination)
            if actual and declared != actual:
                message = (
                    f"dimensions {declared[0]}x{declared[1]} do not match "
                    f"{self.relative(destination)} ({actual[0]}x{actual[1]})"
                )
                self.error(page, message, line)

    def validate_social_metadata(self, page):
        if page.noindex:
            return

        og_image = self.one_metadata(page, "og:image")
        twitter_image = self.one_metadata(page, "twitter:image")
        og_alt = self.one_metadata(page, "og:image:alt")
        twitter_alt = self.one_metadata(page, "twitter:image:alt")

        for label, value in (
            ("og:image", og_image),
            ("twitter:image", twitter_image),
        ):
            if not value:
                continue
            parsed = urlparse(value)
            if parsed.scheme != "https" or parsed.netloc != "www.exosett.com":
                self.error(page, f"{label} must use an absolute ExoSett URL")
                continue
            destination = self.root / unquote(parsed.path).lstrip("/")
            if not destination.is_file():
                self.error(page, f"{label} asset does not exist: {value}")

        if og_image and twitter_image and og_image != twitter_image:
            self.error(page, "Open Graph and Twitter images must match")
        if og_alt is not None and twitter_alt is not None and og_alt != twitter_alt:
            self.error(page, "Open Graph and Twitter image alt text must match")
        if og_alt is not None and not og_alt.strip():
            self.error(page, "social image alt text must not be empty")

    def validate_story(self, page):
        illustration_count = len(page.story_illustrations)
        if illustration_count != 1:
            self.error(
                page,
                f"expected exactly one story illustration, found {illustration_count}",
            )

        note_count = len(page.story_notes)
        if note_count != 1:
            self.error(
                page,
                f"expected exactly one story illustration note, found {note_count}",
            )
        elif page.story_notes[0] != STANDARD_STORY_NOTE:
            self.error(page, "story illustration note is not standard")

        for name in ("og:image", "twitter:image"):
            values = page.metadata_values(name)
            if len(values) == 1:
                path = urlparse(values[0]).path.lower()
                if not path.endswith(".png"):
                    self.error(page, f"{name} must use the PNG story image")

        if illustration_count != 1:
            return

        image_alt = page.story_illustrations[0].get("alt") or ""
        for name in ("og:image:alt", "twitter:image:alt"):
            values = page.metadata_values(name)
            if len(values) == 1 and values[0] != image_alt:
                self.error(page, f"{name} must match the story illustration alt")

    def validate_sitemap(self):
        sitemap_path = self.root / "sitemap.xml"
        try:
            sitemap = ET.parse(sitemap_path)
        except (ET.ParseError, OSError) as exc:
            self.error(None, f"cannot parse sitemap: {exc}", label="sitemap.xml")
            return

        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        actual = {
            element.text or ""
            for element in sitemap.findall("s:url/s:loc", namespace)
        }
        expected = {
            self.page_url(page.path)
            for page in self.pages.values()
            if not page.noindex
        }

        for url in sorted(expected - actual):
            self.error(None, f"missing indexable page: {url}", label="sitemap.xml")
        for url in sorted(actual - expected):
            self.error(
                None,
                f"contains non-indexable or missing page: {url}",
                label="sitemap.xml",
            )

    def one_metadata(self, page, name):
        values = page.metadata_values(name)
        if len(values) != 1:
            self.error(
                page,
                f"expected exactly one {name}, found {len(values)}",
            )
            return None
        return values[0]

    def local_path(self, source, value):
        parsed = urlparse(value)
        if parsed.scheme in {"mailto", "tel", "data", "javascript"}:
            return None
        if parsed.netloc and parsed.netloc != "www.exosett.com":
            return None
        if parsed.scheme and parsed.scheme not in {"http", "https"}:
            return None

        url_path = unquote(parsed.path)
        if not url_path:
            return source

        if url_path.startswith("/"):
            destination = self.root / url_path.lstrip("/")
        else:
            destination = source.parent / url_path

        if url_path.endswith("/") or destination.is_dir():
            destination /= "index.html"
        return destination.resolve()

    def page_url(self, path):
        if path == self.root / "index.html":
            return f"{SITE_ORIGIN}/"
        directory = path.parent.relative_to(self.root).as_posix()
        return f"{SITE_ORIGIN}/{directory}/"

    def relative(self, path):
        return path.relative_to(self.root).as_posix()

    def error(self, page, message, line=None, label=None):
        source = label or self.relative(page.path)
        location = f"{source}:{line}" if line else source
        self.errors.append(f"{location}: {message}")


def raster_dimensions(path):
    """Return dimensions for a PNG, WebP or JPEG without external packages."""

    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return struct.unpack(">II", data[16:24])

    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        offset = 12
        while offset + 8 <= len(data):
            kind = data[offset : offset + 4]
            size = struct.unpack("<I", data[offset + 4 : offset + 8])[0]
            payload = data[offset + 8 : offset + 8 + size]
            if kind == b"VP8X" and len(payload) >= 10:
                return (
                    1 + int.from_bytes(payload[4:7], "little"),
                    1 + int.from_bytes(payload[7:10], "little"),
                )
            if kind == b"VP8 " and payload[3:6] == b"\x9d\x01\x2a":
                return (
                    int.from_bytes(payload[6:8], "little") & 0x3FFF,
                    int.from_bytes(payload[8:10], "little") & 0x3FFF,
                )
            if kind == b"VP8L" and len(payload) >= 5 and payload[0] == 0x2F:
                bits = int.from_bytes(payload[1:5], "little")
                return (1 + (bits & 0x3FFF), 1 + ((bits >> 14) & 0x3FFF))
            offset += 8 + size + (size % 2)

    if data.startswith(b"\xff\xd8"):
        return jpeg_dimensions(data)

    return None


def jpeg_dimensions(data):
    start_of_frame_markers = {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
    offset = 2
    while offset + 9 < len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        if marker in {0xD8, 0xD9}:
            offset += 2
            continue
        length = int.from_bytes(data[offset + 2 : offset + 4], "big")
        if marker in start_of_frame_markers:
            width = int.from_bytes(data[offset + 7 : offset + 9], "big")
            height = int.from_bytes(data[offset + 5 : offset + 7], "big")
            return (width, height)
        offset += 2 + length
    return None


def main():
    root = Path(__file__).resolve().parents[1]
    validator = SiteValidator(root)

    if not validator.run():
        print("Site validation failed:", file=sys.stderr)
        for error in validator.errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    story_count = len(list((root / "stories").glob("*/index.html")))
    print(
        "Site validation passed: "
        f"{len(validator.pages)} HTML pages, {story_count} illustrated stories, "
        "internal references, assets, metadata and sitemap checked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
