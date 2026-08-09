---
published: false
---

# Research and Reading: repository notes

This directory contains the public **Research and Reading** section of the
ExoSett website and the private source notes that support it. This README is
for repository contributors and future maintainers. It is not a public website
page.

## Purpose of the section

Research and Reading collects external articles, papers and reports that
inform, test or challenge ideas relevant to ExoSett. The public pages provide
short, selective discussions from an ExoSett perspective. They are not intended
to stand in for the original sources or to imply that the authors or publishers
endorse ExoSett.

Each source also has a private synopsis. The synopsis records a reasonably
detailed, neutral account of what the source itself says before separately
recording ExoSett's interpretation. This separation is important: claims made
by a source must not be confused with conclusions drawn by ExoSett.

## Directory structure

The section index is:

```text
about/research-and-reading/index.html
```

Each source has one child directory named according to this general pattern:

```text
<publication-year>-<recognisable-source-or-subject>
```

The suffix should be concise but specific enough to identify the particular
source. A source, case study or publication name is preferable to a generic
variation on `modular-housing`. Examples include:

```text
2019-arup-housing-revolution/
2019-place-ladywell/
2023-cambridge-modular-homes/
2025-feantsa-modular-housing/
```

The year is the source's publication year, not the year in which the page was
added to ExoSett.

Every source directory contains:

```text
index.html    Public ExoSett discussion
synopses.md   Private source synopsis and research notes
```

The folder name is also the public URL slug for `index.html`. The `Slug` field
inside `synopses.md` must match it exactly.

## Public discussion pages

The `index.html` file is a hand-authored static page following the rest of the
ExoSett site. It should:

- identify and link to the original external source;
- attribute authors and organisations accurately;
- distinguish the source's claims from ExoSett's interpretation;
- explain why the source is relevant, including points of disagreement or
  uncertainty;
- avoid implying endorsement of ExoSett by the source or its publisher;
- include the standard metadata, canonical URL, Open Graph fields and JSON-LD
  breadcrumbs; and
- link back to the Research and Reading index and, where useful, to related
  ExoSett pages.

Public pages should be concise and selective. Substantial neutral summaries
belong in `synopses.md`, not in the published discussion.

## Private synopsis files

Each `synopses.md` begins with:

```yaml
---
published: false
---
```

GitHub Pages uses Jekyll for this static site. The `published: false` front
matter prevents the Markdown file from being emitted as a public page during
the normal Pages build. Synopsis files must also remain unlinked from public
HTML and absent from `sitemap.xml`.

The established synopsis structure is:

```text
# [Source title]

## Source
## Synopsis
## Main arguments and findings
## Qualifications and limitations
## Relevance to ExoSett
## Points reflected on the website
```

The Source section records the directory slug, authors or organisation,
publication date where available, original URL and access date. The Synopsis,
Main arguments and findings, and Qualifications and limitations sections
describe the source itself. The Relevance to ExoSett section must be explicitly
identified as ExoSett's interpretation. Short quotations should be exceptional,
clearly attributed and limited to what is genuinely useful.

## Adding a source

When adding another article, paper or report:

1. Read the original source, not only an abstract, search result or secondary
   account. Record any access limitations.
2. Choose a stable, intention-revealing directory name using the publication
   year and a concise source or subject identifier.
3. Add the public `index.html` discussion and private `synopses.md` together.
4. Add the public page to `about/research-and-reading/index.html`.
5. Add the public canonical URL to `sitemap.xml`. Do not add the synopsis or
   this README.
6. Update relevant internal links where the new source materially informs
   another page.
7. Check attribution, dates, external URLs and the distinction between source
   findings and ExoSett interpretation.
8. Run the complete site validation.

If a source directory is renamed, update all internal links, canonical and Open
Graph URLs, JSON-LD breadcrumb URLs, the sitemap entry and the synopsis `Slug`
field. Search the whole repository for the former slug before considering the
rename complete.

## Build and validation

The website consists of static HTML and assets hosted with GitHub Pages. There
is no separate compilation step for Research and Reading pages: their
`index.html` files are published at their directory paths as part of the normal
site build.

Run the complete validation from the repository root:

```sh
python3 scripts/validate.py
```

This checks internal references, local assets, metadata, image dimensions,
sitemap coverage and structured data. The structured-data checks can also be
run independently:

```sh
python3 scripts/validate_structured_data.py
```

Validation passing does not replace editorial review. Before publishing, also
inspect source attribution, external links, synopsis front matter and the
accuracy of every statement presented as a source finding.
