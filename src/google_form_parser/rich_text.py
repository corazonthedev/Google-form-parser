from __future__ import annotations

from bs4 import BeautifulSoup, NavigableString, Tag

from .models import RichTextLine

_STYLE_MAP = {
    "b": "bold",
    "strong": "bold",
    "i": "italic",
    "em": "italic",
    "u": "underline",
    "ol": "ordered-list",
    "ul": "unordered-list",
}


def _clean_text(value: str) -> str:
    return " ".join(value.replace("\xa0", " ").split())


def _walk_styles(node: Tag | None) -> list[str]:
    styles: list[str] = []
    current = node
    while isinstance(current, Tag):
        tag_name = current.name.lower()
        if tag_name in _STYLE_MAP:
            styles.append(_STYLE_MAP[tag_name])
        if tag_name == "a" and current.get("href"):
            styles.append(f"link:{current['href']}")
        current = current.parent
    return list(dict.fromkeys(styles))


def extract_rich_text_from_tag(tag: Tag | None) -> list[RichTextLine]:
    if tag is None:
        return []

    lines: list[RichTextLine] = []
    for node in tag.descendants:
        if not isinstance(node, NavigableString):
            continue
        text = _clean_text(str(node))
        if not text:
            continue
        styles = _walk_styles(node.parent)
        lines.append(RichTextLine(text=text, styles=styles or ["normal"]))
    return lines


def extract_rich_text_from_html(html: str) -> list[RichTextLine]:
    soup = BeautifulSoup(html, "html.parser")
    return extract_rich_text_from_tag(soup)
