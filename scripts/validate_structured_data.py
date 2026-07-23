#!/usr/bin/env python3
"""Validate the JSON-LD embedded in the ExoSett static HTML pages."""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
HOME_URL = "https://exosett.com/"
EXCLUDED_PAGES = (
    ROOT / "system" / "index.html",
    ROOT / "components" / "index.html",
    ROOT / "stories" / "index.html",
    ROOT / "about" / "index.html",
)
UNSUPPORTED_TYPES = {
    "Organization",
    "Project",
    "Article",
    "NewsArticle",
    "Product",
    "HowTo",
    "Review",
    "Rating",
    "AggregateRating",
    "Offer",
    "AggregateOffer",
    "MerchantReturnPolicy",
    "OfferShippingDetails",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.canonical: str | None = None
        self.h1_parts: list[str] = []
        self.json_ld_texts: list[str] = []
        self._in_h1 = False
        self._in_json_ld = False
        self._json_ld_parts: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        if tag == "link" and attributes.get("rel") == "canonical":
            self.canonical = attributes.get("href")
        elif tag == "h1":
            self._in_h1 = True
        elif tag == "script" and attributes.get("type") == "application/ld+json":
            self._in_json_ld = True
            self._json_ld_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1":
            self._in_h1 = False
        elif tag == "script" and self._in_json_ld:
            self.json_ld_texts.append("".join(self._json_ld_parts))
            self._in_json_ld = False
            self._json_ld_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_h1:
            self.h1_parts.append(data)
        if self._in_json_ld:
            self._json_ld_parts.append(data)

    @property
    def h1(self) -> str:
        return " ".join("".join(self.h1_parts).split())


def parse_page(path: Path, errors: list[str]) -> tuple[PageParser, list[Any]]:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    documents: list[Any] = []
    for index, text in enumerate(parser.json_ld_texts, start=1):
        try:
            documents.append(json.loads(text))
        except json.JSONDecodeError as exc:
            errors.append(f"{relative(path)}: JSON-LD block {index} is invalid: {exc}")
    return parser, documents


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def objects_with_type(value: Any, schema_type: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    if isinstance(value, dict):
        types = value.get("@type", [])
        if isinstance(types, str):
            types = [types]
        if schema_type in types:
            matches.append(value)
        for child in value.values():
            matches.extend(objects_with_type(child, schema_type))
    elif isinstance(value, list):
        for child in value:
            matches.extend(objects_with_type(child, schema_type))
    return matches


def schema_types(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        types = value.get("@type", [])
        if isinstance(types, str):
            found.add(types)
        elif isinstance(types, list):
            found.update(item for item in types if isinstance(item, str))
        for child in value.values():
            found.update(schema_types(child))
    elif isinstance(value, list):
        for child in value:
            found.update(schema_types(child))
    return found


def validate_breadcrumb_url(url: Any, source: Path, errors: list[str]) -> None:
    if not isinstance(url, str):
        errors.append(f"{relative(source)}: breadcrumb item URL must be a string")
        return

    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or parsed.netloc != "exosett.com"
        or not parsed.path.endswith("/")
        or parsed.params
        or parsed.query
        or parsed.fragment
    ):
        errors.append(
            f"{relative(source)}: breadcrumb URL is not canonical: {url}"
        )
        return

    destination = ROOT / parsed.path.lstrip("/") / "index.html"
    if not destination.is_file():
        errors.append(
            f"{relative(source)}: breadcrumb destination does not exist: {url}"
        )


def validate_breadcrumb_page(
    path: Path, section: str, errors: list[str]
) -> None:
    parser, documents = parse_page(path, errors)
    breadcrumbs = [
        node
        for document in documents
        for node in objects_with_type(document, "BreadcrumbList")
    ]
    if len(breadcrumbs) != 1:
        errors.append(
            f"{relative(path)}: expected exactly one BreadcrumbList, found "
            f"{len(breadcrumbs)}"
        )
        return

    items = breadcrumbs[0].get("itemListElement")
    if not isinstance(items, list) or len(items) != 3:
        errors.append(f"{relative(path)}: breadcrumb must contain three items")
        return

    positions = [item.get("position") for item in items if isinstance(item, dict)]
    if positions != [1, 2, 3]:
        errors.append(
            f"{relative(path)}: breadcrumb positions must be exactly 1, 2, 3"
        )

    expected_names = ["ExoSett", section, parser.h1]
    names = [item.get("name") for item in items if isinstance(item, dict)]
    if names != expected_names:
        errors.append(
            f"{relative(path)}: breadcrumb names {names!r} do not match "
            f"{expected_names!r}"
        )

    if not parser.canonical:
        errors.append(f"{relative(path)}: canonical URL is missing")
    elif not isinstance(items[2], dict) or items[2].get("item") != parser.canonical:
        errors.append(
            f"{relative(path)}: final breadcrumb URL must match the canonical URL"
        )

    for item in items:
        if not isinstance(item, dict) or item.get("@type") != "ListItem":
            errors.append(f"{relative(path)}: every breadcrumb item must be a ListItem")
            continue
        validate_breadcrumb_url(item.get("item"), path, errors)


def main() -> int:
    errors: list[str] = []
    html_pages = sorted(ROOT.rglob("*.html"))
    parsed_pages = {path: parse_page(path, errors) for path in html_pages}

    home_documents = parsed_pages[ROOT / "index.html"][1]
    websites = [
        node
        for document in home_documents
        for node in objects_with_type(document, "WebSite")
    ]
    if len(websites) != 1:
        errors.append(f"index.html: expected exactly one WebSite, found {len(websites)}")
    else:
        website = websites[0]
        if website.get("name") != "ExoSett":
            errors.append("index.html: WebSite name must be ExoSett")
        if website.get("url") != HOME_URL:
            errors.append(f"index.html: WebSite URL must be {HOME_URL}")
        if website.get("@id") != "https://exosett.com/#website":
            errors.append("index.html: WebSite @id is incorrect")

    component_pages = sorted((ROOT / "components").glob("*/index.html"))
    story_pages = sorted((ROOT / "stories").glob("*/index.html"))
    for path in component_pages:
        validate_breadcrumb_page(path, "Components", errors)
    for path in story_pages:
        validate_breadcrumb_page(path, "Stories", errors)

    for path in EXCLUDED_PAGES:
        _, documents = parsed_pages[path]
        breadcrumbs = [
            node
            for document in documents
            for node in objects_with_type(document, "BreadcrumbList")
        ]
        if breadcrumbs:
            errors.append(f"{relative(path)}: BreadcrumbList is not allowed")

    for path, (_, documents) in parsed_pages.items():
        present_types = set().union(*(schema_types(document) for document in documents))
        unsupported = sorted(present_types & UNSUPPORTED_TYPES)
        if unsupported:
            errors.append(
                f"{relative(path)}: unsupported schema types: {', '.join(unsupported)}"
            )

    if errors:
        print("Structured data validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Structured data validation passed: "
        f"1 WebSite, {len(component_pages)} component breadcrumbs, "
        f"{len(story_pages)} story breadcrumbs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
