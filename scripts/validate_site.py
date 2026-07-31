#!/usr/bin/env python3
"""Validate links, assets, metadata and page structure for the static site."""

from __future__ import annotations

import struct
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
SITE_ORIGIN = "https://www.exosett.com"
REDIRECT_PAGE = ROOT / "components" / "accommodation-module" / "index.html"
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


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[tuple[str, int]] = []
        self.images: list[tuple[dict[str, str | None], int]] = []
        self.references: list[tuple[str, str, int]] = []
        self.tag_counts: Counter[str] = Counter()
        self.canonicals: list[str] = []
        self.robots: str = ""
        self.metadata: dict[str, list[str]] = {}
        self.story_illustrations: list[dict[str, str | None]] = []
        self.story_notes: list[str] = []
        self._note_depth = 0
        self._note_parts: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
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

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        if self._note_depth > 1:
            self._note_depth -= 1

    def handle_endtag(self, tag: str) -> None:
        if self._note_depth:
            self._note_depth -= 1
            if not self._note_depth:
                self.story_notes.append(" ".join("".join(self._note_parts).split()))
                self._note_parts = []

    def handle_data(self, data: str) -> None:
        if self._note_depth:
            self._note_parts.append(data)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def expected_page_url(path: Path) -> str:
    if path == ROOT / "index.html":
        return f"{SITE_ORIGIN}/"
    return f"{SITE_ORIGIN}/{path.parent.relative_to(ROOT).as_posix()}/"


def local_path(source: Path, value: str) -> Path | None:
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
    destination = (
        ROOT / url_path.lstrip("/")
        if url_path.startswith("/")
        else source.parent / url_path
    )
    if url_path.endswith("/") or destination.is_dir():
        destination /= "index.html"
    return destination.resolve()


def raster_dimensions(path: Path) -> tuple[int, int] | None:
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
            if kind == b"VP8 " and len(payload) >= 10 and payload[3:6] == b"\x9d\x01\x2a":
                return (
                    int.from_bytes(payload[6:8], "little") & 0x3FFF,
                    int.from_bytes(payload[8:10], "little") & 0x3FFF,
                )
            if kind == b"VP8L" and len(payload) >= 5 and payload[0] == 0x2F:
                bits = int.from_bytes(payload[1:5], "little")
                return (1 + (bits & 0x3FFF), 1 + ((bits >> 14) & 0x3FFF))
            offset += 8 + size + (size % 2)
    if data.startswith(b"\xff\xd8"):
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
            if marker in range(0xC0, 0xC4):
                return (
                    int.from_bytes(data[offset + 7 : offset + 9], "big"),
                    int.from_bytes(data[offset + 5 : offset + 7], "big"),
                )
            offset += 2 + length
    return None


def validate_references(
    path: Path,
    parser: PageParser,
    parsed_pages: dict[Path, PageParser],
    errors: list[str],
) -> None:
    for value, source, line in parser.references:
        destination = local_path(path, value)
        if destination is None:
            continue
        if not destination.is_file():
            errors.append(
                f"{relative(path)}:{line}: missing {source} target: {value}"
            )
            continue
        fragment = unquote(urlparse(value).fragment)
        if fragment and destination.suffix.lower() in {".html", ".htm"}:
            target = parsed_pages.get(destination)
            target_ids = {element_id for element_id, _ in target.ids} if target else set()
            if fragment not in target_ids:
                errors.append(
                    f"{relative(path)}:{line}: missing fragment #{fragment} in "
                    f"{relative(destination)}"
                )


def validate_images(path: Path, parser: PageParser, errors: list[str]) -> None:
    for image, line in parser.images:
        if "alt" not in image:
            errors.append(f"{relative(path)}:{line}: image is missing alt")
        source = image.get("src")
        destination = local_path(path, source) if source else None
        width = image.get("width")
        height = image.get("height")
        if bool(width) != bool(height):
            errors.append(
                f"{relative(path)}:{line}: image must declare both width and height"
            )
        if not destination or not destination.is_file() or not width or not height:
            continue
        try:
            declared = (int(width), int(height))
        except ValueError:
            errors.append(
                f"{relative(path)}:{line}: image dimensions must be integers"
            )
            continue
        actual = raster_dimensions(destination)
        if actual and declared != actual:
            errors.append(
                f"{relative(path)}:{line}: dimensions {declared[0]}x{declared[1]} "
                f"do not match {relative(destination)} ({actual[0]}x{actual[1]})"
            )


def one_metadata(
    path: Path, parser: PageParser, name: str, errors: list[str]
) -> str | None:
    values = parser.metadata.get(name, [])
    if len(values) != 1:
        errors.append(
            f"{relative(path)}: expected exactly one {name}, found {len(values)}"
        )
        return None
    return values[0]


def validate_social_metadata(
    path: Path, parser: PageParser, errors: list[str]
) -> None:
    if "noindex" in parser.robots.lower():
        return
    og_image = one_metadata(path, parser, "og:image", errors)
    twitter_image = one_metadata(path, parser, "twitter:image", errors)
    og_alt = one_metadata(path, parser, "og:image:alt", errors)
    twitter_alt = one_metadata(path, parser, "twitter:image:alt", errors)

    for label, value in (("og:image", og_image), ("twitter:image", twitter_image)):
        if not value:
            continue
        parsed = urlparse(value)
        if parsed.scheme != "https" or parsed.netloc != "www.exosett.com":
            errors.append(f"{relative(path)}: {label} must use an absolute ExoSett URL")
            continue
        destination = ROOT / unquote(parsed.path).lstrip("/")
        if not destination.is_file():
            errors.append(f"{relative(path)}: {label} asset does not exist: {value}")

    if og_image and twitter_image and og_image != twitter_image:
        errors.append(f"{relative(path)}: Open Graph and Twitter images must match")
    if og_alt is not None and twitter_alt is not None and og_alt != twitter_alt:
        errors.append(f"{relative(path)}: Open Graph and Twitter image alt text must match")
    if og_alt is not None and not og_alt.strip():
        errors.append(f"{relative(path)}: social image alt text must not be empty")


def validate_story(path: Path, parser: PageParser, errors: list[str]) -> None:
    if len(parser.story_illustrations) != 1:
        errors.append(
            f"{relative(path)}: expected exactly one story illustration, found "
            f"{len(parser.story_illustrations)}"
        )
    if len(parser.story_notes) != 1:
        errors.append(
            f"{relative(path)}: expected exactly one story illustration note, found "
            f"{len(parser.story_notes)}"
        )
    elif parser.story_notes[0] != STANDARD_STORY_NOTE:
        errors.append(f"{relative(path)}: story illustration note is not standard")

    og_image = parser.metadata.get("og:image", [])
    twitter_image = parser.metadata.get("twitter:image", [])
    for name, values in (("og:image", og_image), ("twitter:image", twitter_image)):
        if len(values) == 1 and not urlparse(values[0]).path.lower().endswith(".png"):
            errors.append(f"{relative(path)}: {name} must use the PNG story image")

    if len(parser.story_illustrations) == 1:
        image_alt = parser.story_illustrations[0].get("alt") or ""
        for name in ("og:image:alt", "twitter:image:alt"):
            values = parser.metadata.get(name, [])
            if len(values) == 1 and values[0] != image_alt:
                errors.append(
                    f"{relative(path)}: {name} must match the story illustration alt"
                )


def validate_sitemap(
    parsed_pages: dict[Path, PageParser], errors: list[str]
) -> None:
    sitemap_path = ROOT / "sitemap.xml"
    try:
        sitemap = ET.parse(sitemap_path)
    except (ET.ParseError, OSError) as exc:
        errors.append(f"sitemap.xml: cannot parse sitemap: {exc}")
        return
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    actual = {
        element.text or "" for element in sitemap.findall("s:url/s:loc", namespace)
    }
    expected = {
        expected_page_url(path)
        for path, parser in parsed_pages.items()
        if "noindex" not in parser.robots.lower()
    }
    for url in sorted(expected - actual):
        errors.append(f"sitemap.xml: missing indexable page: {url}")
    for url in sorted(actual - expected):
        errors.append(f"sitemap.xml: contains non-indexable or missing page: {url}")


def main() -> int:
    errors: list[str] = []
    html_pages = sorted(ROOT.rglob("*.html"))
    parsed_pages: dict[Path, PageParser] = {}
    for path in html_pages:
        parser = PageParser()
        parser.feed(path.read_text(encoding="utf-8"))
        parsed_pages[path.resolve()] = parser

    for path, parser in parsed_pages.items():
        counts = Counter(element_id for element_id, _ in parser.ids)
        for element_id, count in sorted(counts.items()):
            if count > 1:
                errors.append(
                    f"{relative(path)}: duplicate id {element_id!r} appears {count} times"
                )

        if parser.tag_counts["h1"] != 1:
            errors.append(
                f"{relative(path)}: expected exactly one h1, found "
                f"{parser.tag_counts['h1']}"
            )
        if parser.tag_counts["main"] != 1:
            errors.append(
                f"{relative(path)}: expected exactly one main, found "
                f"{parser.tag_counts['main']}"
            )

        if path == REDIRECT_PAGE.resolve():
            expected_canonical = (
                "https://www.exosett.com/components/accommodation-cassette/"
            )
        else:
            expected_canonical = expected_page_url(path)
        if parser.canonicals != [expected_canonical]:
            errors.append(
                f"{relative(path)}: canonical must be exactly {expected_canonical}"
            )

        validate_references(path, parser, parsed_pages, errors)
        validate_images(path, parser, errors)
        validate_social_metadata(path, parser, errors)

    for path in sorted((ROOT / "stories").glob("*/index.html")):
        validate_story(path, parsed_pages[path.resolve()], errors)

    validate_sitemap(parsed_pages, errors)

    if errors:
        print("Site validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    story_count = len(list((ROOT / "stories").glob("*/index.html")))
    print(
        "Site validation passed: "
        f"{len(html_pages)} HTML pages, {story_count} illustrated stories, "
        "internal references, assets, metadata and sitemap checked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
