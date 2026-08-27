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
HOME_URL = "https://www.exosett.com/"
ACCOMMODATION_MODULE_URL = (
    "https://www.exosett.com/components/accommodation-module/"
)
ACCOMMODATION_CASSETTE_REDIRECT = (
    ROOT / "components" / "accommodation-cassette" / "index.html"
)
SYSTEM_REDIRECT = ROOT / "system" / "index.html"
FIRE_SAFETY_ENGINEER_REDIRECT = (
    ROOT / "design" / "fire-safety-engineer" / "index.html"
)
REDIRECTS = {
    ACCOMMODATION_CASSETTE_REDIRECT: ACCOMMODATION_MODULE_URL,
    SYSTEM_REDIRECT: HOME_URL,
    FIRE_SAFETY_ENGINEER_REDIRECT: (
        "https://www.exosett.com/design/safety-engineer/"
    ),
}
EXCLUDED_PAGES = (
    ROOT / "components" / "index.html",
    ROOT / "design" / "index.html",
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
        self.robots: str | None = None
        self.refresh: str | None = None
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
        elif tag == "meta" and attributes.get("name") == "robots":
            self.robots = attributes.get("content")
        elif tag == "meta" and attributes.get("http-equiv") == "refresh":
            self.refresh = attributes.get("content")
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
        or parsed.netloc != "www.exosett.com"
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


def validate_canonical_url(url: Any, source: Path, errors: list[str]) -> None:
    expected_path = "/" if source == ROOT / "index.html" else f"/{source.parent.relative_to(ROOT).as_posix()}/"
    parsed = urlparse(url) if isinstance(url, str) else None
    if (
        parsed is None
        or parsed.scheme != "https"
        or parsed.netloc != "www.exosett.com"
        or parsed.path != expected_path
        or parsed.params
        or parsed.query
        or parsed.fragment
    ):
        errors.append(
            f"{relative(source)}: canonical URL must be {HOME_URL.rstrip('/')}{expected_path}"
        )


def validate_breadcrumb_page(
    path: Path,
    section: str,
    errors: list[str],
    intermediate_names: tuple[str, ...] = (),
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
    expected_count = 3 + len(intermediate_names)
    if not isinstance(items, list) or len(items) != expected_count:
        errors.append(
            f"{relative(path)}: breadcrumb must contain {expected_count} items"
        )
        return

    positions = [item.get("position") for item in items if isinstance(item, dict)]
    expected_positions = list(range(1, expected_count + 1))
    if positions != expected_positions:
        errors.append(
            f"{relative(path)}: breadcrumb positions must be exactly "
            f"{', '.join(str(position) for position in expected_positions)}"
        )

    expected_names = ["ExoSett", section, *intermediate_names, parser.h1]
    names = [item.get("name") for item in items if isinstance(item, dict)]
    if names != expected_names:
        errors.append(
            f"{relative(path)}: breadcrumb names {names!r} do not match "
            f"{expected_names!r}"
        )

    if not parser.canonical:
        errors.append(f"{relative(path)}: canonical URL is missing")
    elif not isinstance(items[-1], dict) or items[-1].get("item") != parser.canonical:
        errors.append(
            f"{relative(path)}: final breadcrumb URL must match the canonical URL"
        )

    for item in items:
        if not isinstance(item, dict) or item.get("@type") != "ListItem":
            errors.append(f"{relative(path)}: every breadcrumb item must be a ListItem")
            continue
        validate_breadcrumb_url(item.get("item"), path, errors)


def validate_redirect_page(
    path: Path,
    expected_url: str,
    parser: PageParser,
    documents: list[Any],
    errors: list[str],
) -> None:
    if parser.canonical != expected_url:
        errors.append(
            f"{relative(path)}: redirect canonical must be {expected_url}"
        )
    if parser.robots != "noindex, follow":
        errors.append(f"{relative(path)}: redirect must use noindex, follow")
    expected_refresh = f"0; url={expected_url}"
    if parser.refresh != expected_refresh:
        errors.append(
            f"{relative(path)}: redirect refresh must be {expected_refresh}"
        )
    if documents:
        errors.append(f"{relative(path)}: redirect must not contain JSON-LD")


def main() -> int:
    errors: list[str] = []
    html_pages = sorted(ROOT.rglob("*.html"))
    parsed_pages = {path: parse_page(path, errors) for path in html_pages}

    for path, (parser, _) in parsed_pages.items():
        if path in REDIRECTS:
            continue
        validate_canonical_url(parser.canonical, path, errors)

    for path, expected_url in REDIRECTS.items():
        redirect_parser, redirect_documents = parsed_pages[path]
        validate_redirect_page(
            path,
            expected_url,
            redirect_parser,
            redirect_documents,
            errors,
        )

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
        if website.get("@id") != "https://www.exosett.com/#website":
            errors.append("index.html: WebSite @id is incorrect")

    component_pages = sorted(
        path
        for path in (ROOT / "components").glob("*/index.html")
        if path != ACCOMMODATION_CASSETTE_REDIRECT
    )
    story_pages = sorted((ROOT / "stories").glob("*/index.html"))
    design_pages = sorted(
        path
        for path in (ROOT / "design").glob("*/index.html")
        if path not in REDIRECTS
    )
    about_pages = sorted((ROOT / "about").glob("*/index.html"))
    nested_about_pages = sorted((ROOT / "about").glob("*/*/index.html"))
    for path in component_pages:
        validate_breadcrumb_page(path, "Components", errors)
    for path in design_pages:
        validate_breadcrumb_page(path, "Design", errors)
    for path in story_pages:
        validate_breadcrumb_page(path, "Stories", errors)
    for path in about_pages:
        validate_breadcrumb_page(path, "About", errors)
    for path in nested_about_pages:
        validate_breadcrumb_page(
            path,
            "About",
            errors,
            intermediate_names=("Research and Reading",),
        )

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
        f"{len(design_pages)} Design breadcrumbs, "
        f"{len(story_pages)} story breadcrumbs, "
        f"{len(about_pages) + len(nested_about_pages)} About breadcrumbs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
