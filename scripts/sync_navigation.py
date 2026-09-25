#!/usr/bin/env python3
"""Synchronise static navigation; --check detects drift without writing files."""

import argparse
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MENUS = {
    "Components": [
        ("Accommodation module", "/components/accommodation-module/"),
        ("Accommodation frame", "/components/accommodation-frame/"),
        ("Service frame", "/components/service-frame/"),
        ("Cell", "/components/cell/"),
        ("Frame node", "/components/frame-node/"),
        ("All components", "/components/"),
    ],
    "Design": [
        ("Sketch", "/design/sketch/"),
        ("Project roles", "/design/#roles-heading"),
        ("Accommodation design", "/design/accommodation-design/"),
        ("Location", "/design/location/"),
        ("Fire safety", "/design/fire-safety/"),
        ("Design overview", "/design/"),
    ],
    "Stories": [
        ("Retirement living", "/stories/retirement-living/"),
        ("Event accommodation", "/stories/event-accommodation/"),
        ("The old prison", "/stories/the-old-prison/"),
        ("The evolving hotel", "/stories/evolving-hotel/"),
        ("All stories", "/stories/"),
    ],
    "About": [
        ("Why are we here?", "/about/"),
        ("Research and Reading", "/about/research-and-reading/"),
        ("ExoSett and conventional modular construction", "/about/exosett-and-conventional-modular-construction/"),
        ("Discuss ExoSett", "/about/#contact-heading"),
    ],
}
NAV = re.compile(r'<nav class="site-nav".*?</nav>', re.S)
SCRIPT = '<script src="/assets/js/navigation.js" defer></script>'


class Tokens(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tokens = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tokens.append((tag, sorted(attrs)))

    def handle_endtag(self, tag):
        self.tokens.append(("end", tag))

    def handle_data(self, data):
        if data.strip():
            self.tokens.append(("text", " ".join(data.split())))


def render(url):
    def link(label, href, section=False):
        current = ' aria-current="page"' if href == url else ""
        active = ' class="site-nav__section-link is-active"' if section and url.startswith(href) else (' class="site-nav__section-link"' if section else "")
        return f'<a href="{href}"{active}{current}>{escape(label)}</a>'

    parts = ['<nav class="site-nav" aria-label="Primary navigation"><ul class="site-nav__list">']
    for title, entries in MENUS.items():
        slug = title.lower()
        parts += [f'<li class="site-nav__item">{link(title, f"/{slug}/", True)}',
                  f'<details class="site-nav__disclosure"><summary aria-controls="nav-{slug}"><span class="visually-hidden">{title} submenu</span><span class="site-nav__chevron" aria-hidden="true"></span></summary>',
                  f'<ul class="site-nav__submenu" id="nav-{slug}">']
        parts += [f'<li>{link(label, href)}</li>' for label, href in entries]
        parts += ['</ul></details></li>']
    return "\n".join(parts + ['</ul></nav>'])


def main(check=False):
    errors = []
    count = 0
    for page in sorted(ROOT.rglob("*.html")):
        if set(page.relative_to(ROOT).parts) & {"_site", "node_modules", ".git"}:
            continue
        html = page.read_text()
        match = NAV.search(html)
        if not match:
            continue
        url = "/" + page.relative_to(ROOT).as_posix().removesuffix("index.html")
        expected = render(url)
        if check:
            if Tokens(match[0]).tokens != Tokens(expected).tokens or SCRIPT not in html:
                errors.append(str(page.relative_to(ROOT)))
        else:
            html = NAV.sub(lambda _: expected, html)
            if SCRIPT not in html:
                html = html.replace("</head>", f"{SCRIPT}\n</head>")
            page.write_text(html)
        count += 1
    if errors:
        print("Navigation out of sync: " + ", ".join(errors))
        return 1
    print(f"Navigation {'checked' if check else 'synchronised'} on {count} pages.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    raise SystemExit(main(parser.parse_args().check))
