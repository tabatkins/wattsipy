# WattsiPy

WattsiPy is a Python port of [Wattsi](https://github.com/whatwg/wattsi), the build tool for generating the [HTML Standard](https://html.spec.whatwg.org/multipage/) from its source.

This project is 100% Gemini-authored, intended solely to help with a different project (converting the HTML source file from Wattsi to Bikeshed).
It produces identical output as the original Pascal version, but the source code has had zero review, as it's not actually important.
Don't use this for any other purpose besides historical interest.

## Features

- Number the sections and headings
- Create comprehensive and small Tables of Contents (TOC)
- Cross-reference `<span>` and `<code>` to `<dfn>`
- Create cross-reference indices (`xrefs.json`)
- Spec splitting into multipage versions (`multipage-html`, `multipage-dev`) with fragment links (`fragment-links.json`)
- Dev edition search index generation (`search-index.json`)
- Add output for `<wpt>` elements
- Add MDN browser compatibility annotations
- Strip unused references and validate missing references

## Usage

```bash
wattsipy [--quiet] [--single-page-only] <source-file> <source-git-sha> <output-directory> <default-or-review> <mdn-spec-links/html.json> [<highlight-server-url>]
```

Or via python:

```bash
python3 -m wattsipy ...
```
